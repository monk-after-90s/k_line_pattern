import asyncio
from typing import Iterable, List
from model import get_or_create_bar_objects, DbBarData, DbBarOverview
from pattern_calculator import pattern_calcltor_calsses


async def query_newest_bars(intervals: List):
    """
    获取全部symbol配置计算形态所需要的bars数据

    :param intervals: K线间隔筛选
    :return:
    """
    # 获取symbol配置，分配任务
    bar_objects = await get_or_create_bar_objects()
    # 获取symbol配置
    bar_configs: Iterable[DbBarOverview] = await bar_objects.execute(
        DbBarOverview.select().where(DbBarOverview.interval.in_(intervals)))
    return await asyncio.gather(
        *(_query_newest_bars(bar_config.symbol, bar_config.exchange, bar_config.interval) for bar_config in
          bar_configs))


async def _query_newest_bars(symbol: str, exchange: str, interval: str):
    """扫描一个K线序列"""
    # 需要的最大的Kline Bar数量
    max_bar_num: int = max(pattern_calcltor_calss.bar_num for pattern_calcltor_calss in pattern_calcltor_calsses)
    bar_objects = await get_or_create_bar_objects()
    bars: Iterable[DbBarData] = await bar_objects.execute(DbBarData.select().where(
        (DbBarData.symbol == symbol) & (DbBarData.exchange == exchange) & (DbBarData.interval == interval)). \
                                                          order_by(DbBarData.datetime.desc()).limit(max_bar_num))
    bars = sorted(bars, key=lambda item: item.datetime)
    return bars
