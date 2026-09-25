"""zkc：Zodiac Killer 密文分析工具包。

模块：
    cipher     密文加载与网格表示
    stats      统计量（多重度、同构模式、周期双字母重复、置换检验、符号重合）
    transpose  换位（抽取读取、Z340 已发表的换位方案）
    keys       密钥推导、应用与准确率评估
    ngram      字母 n-gram 语言模型（AZdecrypt 格式 / 自建语料）
    corpus     内置英文语料（Python 标准库文档）
    solver     同音替换求解器（模拟退火 + 热浴采样）
"""

__version__ = "0.1.0"
