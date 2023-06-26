"""形态计算器"""
import threading
from typing import Callable, Iterable
from playhouse.shortcuts import model_to_dict
from model import DbBarData
from abc import ABC
from cal_pattern import *
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


class CSFRCalcltor(PatternCalcltor):
    bar_num = 20
    cal_func: Callable = CSFR


class FindDuckHeadCalcltor(PatternCalcltor):
    bar_num = 105
    cal_func: Callable = find_duck_head


class WYGDCalcltor(PatternCalcltor):
    bar_num = 2
    cal_func: Callable = WYGD


class DTZDCalcltor(PatternCalcltor):
    bar_num = 2
    cal_func: Callable = DTZD


class ThreeWavesUpCalcltor(PatternCalcltor):
    _three_waves_up_ins = ThreeWavesUp()

    bar_num = 1  # todo 可以处理历史数据
    cal_func: Callable = _three_waves_up_ins.update_bar


class ThreeWavesDownCalcltor(PatternCalcltor):
    _three_waves_down_ins = ThreeWavesDown()

    bar_num = 1  # todo 可以处理历史数据
    cal_func: Callable = _three_waves_down_ins.update_bar
