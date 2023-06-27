"""形态计算器"""
from pattern_recognition import *
from pandas import DataFrame
from .pattern_calcltor_interface import *
from collections import defaultdict


class CSFRCalcltor(PatternCalcltor):
    name = "出水芙蓉"
    bar_num = 20
    cal_func: Callable = CSFR


class FindDuckHeadCalcltor(PatternCalcltor):
    name = "老鸭头"
    bar_num = 105
    cal_func: Callable = find_duck_head


class WYGDCalcltor(PatternCalcltor):
    name = "乌云盖顶"
    bar_num = 2
    cal_func: Callable = WYGD


class DTZDCalcltor(PatternCalcltor):
    name = "断头铡刀"
    bar_num = 20
    cal_func: Callable = DTZD


class ThreeWavesUpCalcltor(PatternCalcltor):
    name = "三浪上涨"
    _three_waves_up_inss = defaultdict(lambda: ThreeWavesUp())

    bar_num = 1  # todo 可以处理历史数据

    @classmethod
    def cal_func(cls, bar_df: DataFrame):
        # K线间隔
        intervals = list(set(bar_df['interval']))
        assert len(intervals) == 1
        interval = intervals[0]

        return cls._three_waves_up_inss[interval].update_bar(bar_df)


class ThreeWavesDownCalcltor(PatternCalcltor):
    name = "三浪下跌"
    _three_waves_down_inss = defaultdict(lambda: ThreeWavesDown())

    bar_num = 1  # todo 可以处理历史数据

    @classmethod
    def cal_func(cls, bar_df: DataFrame):
        # K线间隔
        intervals = list(set(bar_df['interval']))
        assert len(intervals) == 1
        interval = intervals[0]

        return cls._three_waves_down_inss[interval].update_bar(bar_df)


class XiangTiZhengLiCalcltor(PatternCalcltorWithInterval):
    name = "箱体震荡"
    bar_num = 35  # todo 可以处理历史数据

    @classmethod
    def cal_func(cls, bar_df: DataFrame, interval: str):
        return XiangTiZhengLi(bar_df, interval).analyse_pattern()


class JDFJCalcltor(PatternCalcltor):
    name = "绝地反击"
    bar_num = 5
    cal_func: Callable = JDFJ


class JZTDCalcltor(PatternCalcltor):
    name = "金针探底"
    bar_num = 5
    cal_func: Callable = JZTD


class SJZXCalcltor(PatternCalcltor):
    name = "射击之星"
    bar_num = 5
    cal_func: Callable = SJZX


class FindMUpperCalcltor(PatternCalcltorWithInterval):
    name = "M顶"
    bar_num = 100
    cal_func: Callable = find_m_upper


class FindHeadAndShouldersCalcltor(PatternCalcltorWithInterval):
    name = "头肩顶"
    bar_num = 150
    cal_func: Callable = find_head_and_shoulders


class FindWBottomCalcltor(PatternCalcltorWithInterval):
    name = "W底"
    bar_num = 100
    cal_func: Callable = find_w_bottom


class FindHeadAndShouldersBottomCalcltor(PatternCalcltorWithInterval):
    name = "头肩底"
    bar_num = 150
    cal_func: Callable = find_head_and_shoulders_bottom


class GOLDENPITCalcltor(PatternCalcltorWithInterval):
    name = "黄金坑"
    bar_num = 30
    cal_func: Callable = GOLDEN_PIT
