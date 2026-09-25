"""H003：Z32 “弧度 + 英寸”指令的地理命中是否超出偶然（look-elsewhere 检验）。

几何解析规则与判定阈值见 hypotheses/H003-z32-map-lookelsewhere.md（运行前已提交）。
输出：results/h003_map_geometry.json、results/h003_endpoints.csv（全部候选终点，供后续 GIS 使用）。

用法：python scripts/h003_map_geometry.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from m3_z32_grammar import phrases  # noqa: E402

from zkc.cipher import ROOT, load  # noqa: E402
from zkc.console import utf8_stdio  # noqa: E402
from zkc.names import fits  # noqa: E402

EARTH_R = 6_371_008.8  # m
MILE = 1609.344  # m
CENTER = (37.881697781, -121.914154997)  # Mt. Diablo 山顶（维基百科）
DECLINATION = 16.88  # 度，东偏；1970-06-26，NOAA DGRF70
MILES_PER_INCH = 6.4
TARGETS = {  # OpenStreetMap Nominatim，2026-09-25 查询
    "Ingleside 警察分局（Grinell）": (37.7246336, -122.4463020),
    "Blue Rock Springs 公园（Stampher）": (38.1264012, -122.1888741),
}
CONVENTIONS = {  # (方向符号, 磁偏角符号)
    "顺时针+偏角（主约定）": (1, 1),
    "顺时针−偏角": (1, -1),
    "逆时针+偏角": (-1, 1),
    "逆时针−偏角": (-1, -1),
}
RADII = (0.5, 1.0, 2.0)  # 英里
N_ROT = 10_000


def destination(lat, lon, bearing_deg, dist_m):
    """球面上自 (lat, lon) 沿真方位 bearing 前进 dist 后的位置（度）。支持数组。"""
    phi1, lam1 = np.radians(lat), np.radians(lon)
    theta, delta = np.radians(bearing_deg), np.asarray(dist_m) / EARTH_R
    phi2 = np.arcsin(np.sin(phi1) * np.cos(delta) + np.cos(phi1) * np.sin(delta) * np.cos(theta))
    lam2 = lam1 + np.arctan2(np.sin(theta) * np.sin(delta) * np.cos(phi1),
                             np.cos(delta) - np.sin(phi1) * np.sin(phi2))
    return np.degrees(phi2), np.degrees(lam2)


def distance(lat1, lon1, lat2, lon2):
    """球面大圆距离（米），支持广播。"""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi, dlam = p2 - p1, np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlam / 2) ** 2
    return 2 * EARTH_R * np.arcsin(np.sqrt(a))


def bearing(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dlam = np.radians(lon2 - lon1)
    y = np.sin(dlam) * np.cos(p2)
    x = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dlam)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


def endpoints(pairs, conventions):
    """候选 (弧度, 英寸) × 约定 → 终点数组。"""
    rows = []
    for name, (d, s) in conventions.items():
        for r, i in pairs:
            b = (d * np.degrees(r) + s * DECLINATION) % 360
            lat, lon = destination(*CENTER, b, i * MILES_PER_INCH * MILE)
            rows.append((name, r, i, float(b), float(lat), float(lon)))
    return rows


def evaluate(points, rng) -> dict:
    lats = np.array([p[4] for p in points])
    lons = np.array([p[5] for p in points])
    out = {}
    for tname, (tlat, tlon) in TARGETS.items():
        d = distance(tlat, tlon, lats, lons) / MILE
        k = int(np.argmin(d))
        # 零假设：目标绕圆心随机旋转
        t_dist = distance(*CENTER, tlat, tlon)
        rot = rng.uniform(0, 360, N_ROT)
        rlat, rlon = destination(*CENTER, rot, t_dist)
        dmin = np.min(distance(rlat[:, None], rlon[:, None], lats[None, :], lons[None, :]), axis=1) / MILE
        out[tname] = {
            "min_distance_miles": round(float(d[k]), 2),
            "nearest": {"convention": points[k][0], "radians": points[k][1], "inches": points[k][2]},
            "hits": {str(R): int((d <= R).sum()) for R in RADII},
            "p_chance": {str(R): float((dmin <= R).mean()) for R in RADII},
        }
    return out


def main() -> None:
    utf8_stdio()
    rng = np.random.default_rng(0)
    z32 = load("z32").text
    z32_alt = z32[:25] + "④" + z32[26:]  # 第 26 位为独立符号
    grammar = list(phrases(32)[0])
    families = {
        "原转录（65 种组合）": sorted({(r, i) for t, r, i in grammar if fits(t, z32)}),
        "第26位独立（220 种组合）": sorted({(r, i) for t, r, i in grammar if fits(t, z32_alt)}),
    }
    main_conv = {k: v for k, v in CONVENTIONS.items() if "主约定" in k}
    results = {"rules": {"center": CENTER, "declination": DECLINATION, "miles_per_inch": MILES_PER_INCH,
                         "targets": TARGETS, "radii_miles": RADII, "rotations": N_ROT}}
    all_points = []
    for fname, pairs in families.items():
        for cname, convs in (("主约定", main_conv), ("4 种约定合并", CONVENTIONS)):
            pts = endpoints(pairs, convs)
            if cname == "4 种约定合并":
                all_points += [(fname, *p) for p in pts]
            res = evaluate(pts, rng)
            results[f"{fname}/{cname}"] = res
            for tname, r in res.items():
                print(f"{fname} / {cname} / {tname}：最近 {r['min_distance_miles']} 英里；"
                      f"命中(0.5/1/2 英里) {list(r['hits'].values())}；"
                      f"P_chance(0.5/1/2) {[round(v, 3) for v in r['p_chance'].values()]}", flush=True)

    # Grinell 读法在主约定下的落点
    g = endpoints([(4.0, 5.0)], main_conv)[0]
    gd = distance(*TARGETS["Ingleside 警察分局（Grinell）"], g[4], g[5]) / MILE
    results["grinell_main_convention"] = {"bearing": round(g[3], 2), "lat": round(g[4], 5), "lon": round(g[5], 5),
                                          "distance_to_ingleside_miles": round(float(gd), 2)}
    print(f"Grinell（4 弧度、5 英寸，主约定）：真方位 {g[3]:.2f}°，落点 ({g[4]:.5f}, {g[5]:.5f})，"
          f"距 Ingleside 分局 {gd:.2f} 英里", flush=True)
    t = TARGETS["Blue Rock Springs 公园（Stampher）"]
    results["blue_rock_springs_geometry"] = {
        "bearing_from_center": round(float(bearing(*CENTER, *t)), 2),
        "distance_inches": round(float(distance(*CENTER, *t) / MILE / MILES_PER_INCH), 2)}

    (ROOT / "results" / "h003_map_geometry.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    with (ROOT / "results" / "h003_endpoints.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "convention", "radians", "inches", "true_bearing", "lat", "lon"])
        w.writerows([(f, c, r, i, round(b, 3), round(la, 6), round(lo, 6)) for f, c, r, i, b, la, lo in all_points])
    print("已写入 results/h003_map_geometry.json、results/h003_endpoints.csv")


if __name__ == "__main__":
    main()
