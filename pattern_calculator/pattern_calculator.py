"""形态计算器"""
import threading
from typing import Callable, Iterable
from playhouse.shortcuts import model_to_dict
from model import DbBarData

from cal_pattern import *
import pandas as pd


class PatternCalcltor:
    # K line number
    bar_num: int = 0

    def __init__(self, bars: Iterable[DbBarData]):
        # 转换为pandas Dataframe对象
        self.bar_df = pd.DataFrame(
            sorted([model_to_dict(bar) for bar in bars], key=lambda i: i['datetime'])[-self.bar_num:])
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
        return self.cal_func(self.bar_df)


class FindDuckHeadCalcltor(PatternCalcltor):
    bar_num = 105

    def __init__(self, bars: Iterable[DbBarData]):
        super().__init__(bars)
        self.cal_func: Callable = find_duck_head

    def __call__(self):
        return self.cal_func(self.bar_df)


class ThreeWavesUpCalcltor(PatternCalcltor):
    _instance_lock = threading.Lock()

    bar_num = 1  # todo 可以处理历史数据

    def __init__(self, bars: Iterable[DbBarData]):
        super().__init__(bars)
        self._three_waves_up_ins = ThreeWavesUp()
        self.cal_func: Callable = self._three_waves_up_ins.update_bar

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with ThreeWavesUpCalcltor._instance_lock:
                if not hasattr(cls, '_instance'):
                    ThreeWavesUpCalcltor._instance = super().__new__(cls)

        return ThreeWavesUpCalcltor._instance

    def __call__(self):
        return self.cal_func(self.bar_df)
