from typing import Callable, Iterable
from playhouse.shortcuts import model_to_dict
from model import DbBarData
from abc import ABC
import pandas as pd


class PatternCalcltor(ABC):
    # K line number
    bar_num: int = 0
    cal_func: Callable = None

    # 单线程单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def calculate(self, bars: Iterable[DbBarData]):
        bar_df = pd.DataFrame(
            sorted([model_to_dict(bar) for bar in bars], key=lambda i: i['datetime'])[-self.bar_num:])
        return self.cal_func(bar_df)


class PatternCalcltorWithInterval(ABC, PatternCalcltor):
    """带有interval参数的形态计算器"""

    def calculate(self, bars: Iterable[DbBarData]):
        # K线间隔
        intervals = [bar.interval for bar in bars]
        assert len(intervals) == 1
        # bar Dataframe
        bar_df = pd.DataFrame(
            sorted([model_to_dict(bar) for bar in bars], key=lambda i: i['datetime'])[-self.bar_num:])

        return self.cal_func(bar_df, intervals[0])