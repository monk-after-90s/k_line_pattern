import asyncio
from typing import Iterable, List
from orm import bar_asess_fctry, Dbbardata, Dbbaroverview
from pattern_calculator import pattern_calcltor_classes
from sqlalchemy import select


async def query_newest_bars(intervals: List):
    """
    获取全部symbol配置计算形态所需要的bars数据

    :param intervals: K线间隔筛选
    :return:
    """
    # 获取symbol配置，分配任务
    async with bar_asess_fctry() as session:
        # 获取symbol配置
        bar_configs: Iterable[Dbbaroverview] = (await session.execute(
            select(Dbbaroverview).where(Dbbaroverview.interval.in_(intervals))
        )).scalars().all()
        return await asyncio.gather(
            *(_query_newest_bars(bar_config.symbol, bar_config.exchange, bar_config.interval) for bar_config in
              bar_configs))


async def _query_newest_bars(symbol: str, exchange: str, interval: str):
    """
    扫描一个K线序列

    :return: 按datetime排序的K线列表
    """
    # 需要的最大的Kline Bar数量
    max_bar_num: int = max(pattern_calcltor_class.bar_num for pattern_calcltor_class in pattern_calcltor_classes)

    async with bar_asess_fctry() as session:
        bars: Iterable[Dbbardata] = (await session.execute(
            select(Dbbardata).where(
                Dbbardata.symbol == symbol,
                Dbbardata.exchange == exchange,
                Dbbardata.interval == interval).order_by(Dbbardata.datetime.desc()).limit(max_bar_num)
        )).scalars().all()

        bars = sorted(bars, key=lambda item: item.datetime)
        return bars
