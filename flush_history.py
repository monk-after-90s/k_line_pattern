"""填充历史"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import Iterable, List
import beeprint
from peewee import fn
from config import INTERVALS
from generate_pattern import cal_and_record_pattern_mul_pro
from utilities import handle_sigterm, symbol_vnpy2united, VNPY_BN_INTERVAL_MAP
from loguru import logger
from model import get_or_create_k_pattern_objects, PatternRecognizeRecord, get_or_create_bar_objects, DbBarOverview, \
    DbBarData
from utilities import INTERVAL_SECS_MAP as interval_secs_map
import pytz
from config import TIMEZONE
from utilities import convert_to_sh
from concurrent.futures import ProcessPoolExecutor
from pattern_calculator import pattern_calcltor_classes


def main():
    logger.warning(f"请手动确保运行在了东八区")
    if os.environ.get("PYTHONUNBUFFERED") == "1":
        logger.info(f"development mode")

    # 事件循环
    loop = asyncio.get_event_loop()
    handle_sigterm(loop)
    # 多进程执行器
    executor = ProcessPoolExecutor()
    # 添加任务
    loop.create_task(flush(executor))
    try:
        loop.run_forever()
    finally:
        logger.info(f"Start gracefully exit")
        loop.run_until_complete(gracefully_exit())
        executor.shutdown()
        logger.info(f"Finish gracefully exit")


async def gracefully_exit():
    """优雅退出"""
    print(f"gracefully_exit")


async def flush(executor: ProcessPoolExecutor):
    """填充历史形态记录"""
    # 分周期处理
    if INTERVALS: await asyncio.wait(
        [asyncio.create_task(handle_interval(INTERVAL, executor)) for INTERVAL in INTERVALS])


async def handle_interval(interval: str, executor: ProcessPoolExecutor):
    """处理单个周期"""
    # 获取symbol配置，分配任务
    bar_objects = await get_or_create_bar_objects()
    # 获取symbol配置
    bar_configs: Iterable[DbBarOverview] = await bar_objects.execute(
        DbBarOverview.select().where(DbBarOverview.interval == interval))

    return await asyncio.gather(
        *(handle_symbol_interval(bar_config.symbol,
                                 bar_config.exchange,
                                 bar_config.interval,
                                 executor)
          for bar_config in bar_configs))


async def handle_symbol_interval(symbol,
                                 exchange,
                                 interval,
                                 executor: ProcessPoolExecutor):
    """处理单个symbol的单个interval的K线序列"""
    bar_objects = await get_or_create_bar_objects()

    # 格式转换
    symbol_type, united_symbol = await asyncio.create_task(symbol_vnpy2united(exchange,
                                                                              symbol))
    # 查找续接日期
    newest_record_dt: datetime | None = await (await get_or_create_k_pattern_objects()).scalar(
        PatternRecognizeRecord.select(fn.Max(PatternRecognizeRecord.pattern_end)).where(
            (PatternRecognizeRecord.exchange == exchange) &
            (PatternRecognizeRecord.symbol_type == symbol_type) &
            (PatternRecognizeRecord.symbol == united_symbol) &
            (PatternRecognizeRecord.k_interval == VNPY_BN_INTERVAL_MAP[interval])))
    if newest_record_dt is not None:
        newest_record_dt = convert_to_sh(newest_record_dt)

    # 修剪起始datetime使其刚好符合interval
    interval_secs = interval_secs_map[interval]
    if newest_record_dt is not None:
        init_bar_datetime: datetime | None = datetime.fromtimestamp(
            newest_record_dt.timestamp() - newest_record_dt.timestamp() % interval_secs,
            tz=pytz.timezone(TIMEZONE))
        # 不要时区
        init_bar_datetime = init_bar_datetime.replace(tzinfo=None)
    else:
        # 柱子的初始datetime
        init_bar_datetime: datetime = await bar_objects.scalar(
            DbBarData.select(fn.Min(DbBarData.datetime)).where((DbBarData.symbol == symbol) &
                                                               (DbBarData.exchange == exchange) &
                                                               (DbBarData.interval == interval)))
        if init_bar_datetime is None:
            logger.error(beeprint.pp({
                "msg": "没有K线",
                "symbol": symbol,
                "exchange": exchange,
                "interval": interval
            }, output=False, sort_keys=False))
            return

    # 需要的最大的Kline Bar数量
    max_bar_num: int = max(pattern_calcltor_class.bar_num for pattern_calcltor_class in pattern_calcltor_classes)

    # 查询、计算、存储循环
    while True:
        # 查bars
        bars: List[DbBarData] = sorted(await bar_objects.execute(
            DbBarData.select().where((DbBarData.symbol == symbol) &
                                     (DbBarData.exchange == exchange) &
                                     (DbBarData.interval == interval) &
                                     (DbBarData.datetime <= init_bar_datetime)).
            order_by(DbBarData.datetime.desc()).limit(max_bar_num)
        ), key=lambda item: item.datetime)

        if not bars:
            logger.error(beeprint.pp({
                "msg": "没有K线",
                "symbol": symbol,
                "exchange": exchange,
                "interval": interval
            }, output=False, sort_keys=False))
            return
        else:
            # 查bar查到了底
            if init_bar_datetime is not None and init_bar_datetime > bars[-1].datetime:
                ...
                # todo
            # 计算并存储pattern_calcltor值
            tasks = []
            for pattern_calcltor_class in pattern_calcltor_classes:
                tasks.append(
                    asyncio.create_task(cal_and_record_pattern_mul_pro(pattern_calcltor_class, bars, executor)))
            [await task for task in tasks]

            # datetime步进
            init_bar_datetime += timedelta(seconds=interval_secs_map[interval])


if __name__ == '__main__':
    main()
