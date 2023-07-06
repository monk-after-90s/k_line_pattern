"""填充历史"""
import asyncio
import os
from datetime import datetime, timedelta
from typing import Iterable, List
from peewee import fn
from config import INTERVALS
from generate_pattern import cal_and_record_pattern_mul_pro
from utilities import handle_sigterm
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
    # 查找续接日期
    newest_record_dt: datetime | None = await (await get_or_create_k_pattern_objects()).scalar(
        PatternRecognizeRecord.select(fn.Max(PatternRecognizeRecord.pattern_end)))
    if newest_record_dt is not None:
        newest_record_dt = convert_to_sh(newest_record_dt)
    # 分周期处理
    if INTERVALS: await asyncio.wait(
        [asyncio.create_task(handle_interval(newest_record_dt, INTERVAL, executor)) for INTERVAL in INTERVALS])


async def handle_interval(init_datetime: datetime | None, interval: str, executor: ProcessPoolExecutor):
    """处理单个周期"""
    # 修剪起始datetime使其刚好符合interval
    interval_secs = interval_secs_map[interval]
    if init_datetime is not None:
        init_bar_datetime = datetime.fromtimestamp(
            init_datetime.timestamp() - init_datetime.timestamp() % interval_secs,
            tz=pytz.timezone(TIMEZONE))
    else:
        init_bar_datetime = None
    # 获取symbol配置，分配任务
    bar_objects = await get_or_create_bar_objects()
    # 获取symbol配置
    bar_configs: Iterable[DbBarOverview] = await bar_objects.execute(
        DbBarOverview.select().where(DbBarOverview.interval == interval))

    return await asyncio.gather(
        *(handle_symbol_interval(bar_config.symbol,
                                 bar_config.exchange,
                                 bar_config.interval,
                                 init_bar_datetime,
                                 executor)
          for bar_config in bar_configs))


async def handle_symbol_interval(symbol,
                                 exchange,
                                 interval,
                                 init_bar_datetime: None | datetime,
                                 executor: ProcessPoolExecutor):
    """处理单个symbol的单个interval的K线序列"""


if __name__ == '__main__':
    main()
