"""控制台输出设置。"""

import sys


def utf8_stdio() -> None:
    """把标准输出/错误改为 UTF-8：Windows 管道或重定向时的默认编码（如 cp949）可能不支持中文。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
