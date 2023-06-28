# 三浪上涨、三浪下跌辅助，用于存储kline的数据结构
from collections import defaultdict
from pattern_recognition import ThreeWavesUp, ThreeWavesDown


class Exchange:
    def __init__(self, calculator_class):
        # self.name = ''  # BINANCE、OKEX等
        self.symbols = defaultdict(lambda: Symbol(calculator_class))  # btcusdt、BTCUSDT


class Symbol:
    def __init__(self, calculator_class):
        # self.name = ''  # btcusdt、BTCUSDT等
        self.intervals = defaultdict(lambda: Interval(calculator_class))  # 30m、1h、d等


class Interval:
    def __init__(self, calculator_class):
        # self.name = ''  # 30m、1h、d等
        self.calculator: ThreeWavesUp | ThreeWavesDown = calculator_class()
