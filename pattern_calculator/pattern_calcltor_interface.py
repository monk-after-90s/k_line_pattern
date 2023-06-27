from typing import Callable, Iterable

import beeprint
from loguru import logger
from playhouse.shortcuts import model_to_dict
from model import DbBarData
from abc import ABC
import pandas as pd


class PatternCalcltor(ABC):
    # 名字
    name = ''
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

#         logger.debug(
        #             f"""
        # pattern_calcltor_class={type(self)}
        # bar_df=
        # {beeprint.pp({"head bar": f"{bar_df.iloc[0].exchange} {bar_df.iloc[0].symbol} {bar_df.iloc[0].interval} {bar_df.iloc[0].datetime}",
        #               "tail bar": f"{bar_df.iloc[-1].exchange} {bar_df.iloc[-1].symbol} {bar_df.iloc[-1].interval} {bar_df.iloc[-1].datetime}"},
        #              output=False,
        #              sort_keys=False)}""")
        return type(self).cal_func(bar_df)


class PatternCalcltorWithInterval(PatternCalcltor):
    """带有interval参数的形态计算器"""

    def calculate(self, bars: Iterable[DbBarData]):
        # K线间隔
        intervals = list({bar.interval for bar in bars})
        assert len(intervals) == 1
        # bar Dataframe
        bar_df = pd.DataFrame(
            sorted([model_to_dict(bar) for bar in bars], key=lambda i: i['datetime'])[-self.bar_num:])

        return type(self).cal_func(bar_df, intervals[0])
