"""形态计算器"""
from typing import Callable, Iterable
from playhouse.shortcuts import model_to_dict
from model import DbBarData

from cal_pattern import *
import pandas as pd


class PatternCalcltor:
    # K line number
    bar_num: int = 0

    def __init__(self, bars: Iterable[DbBarData]):
        # 转换为pandas对象
        self.bar_df = pd.DataFrame(sorted([model_to_dict(bar) for bar in bars], key=lambda i: i['datetime']))
        # calculator function
        self.cal_func: Callable | None = None

    def __call__(self, *args, **kwargs):
        return self.cal_func(*args, **kwargs)


class CSFRCalcltor(PatternCalcltor):
    bar_num = 20

    def __init__(self, bars: Iterable[DbBarData]):
        super().__init__(bars)
        self.cal_func: Callable = CSFR

    def __call__(self):
        return self.cal_func(self.bar_df[-self.bar_num:])
