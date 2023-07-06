"""填充历史"""
import asyncio
import os
from datetime import datetime
from peewee import fn

from utilities import handle_sigterm
from loguru import logger
from model import get_or_create_k_pattern_objects, PatternRecognizeRecord, get_or_create_bar_objects, DbBarOverview


def main():
    logger.warning(f"请手动确保运行在了东八区")
    if os.environ.get("PYTHONUNBUFFERED") == "1":
        logger.info(f"development mode")

    # 事件循环
    loop = asyncio.get_event_loop()
    handle_sigterm(loop)
    # 添加任务
    loop.create_task(flush())
    try:
        loop.run_forever()
    finally:
        logger.info(f"Start gracefully exit")
        loop.run_until_complete(gracefully_exit())
        logger.info(f"Finish gracefully exit")


async def gracefully_exit():
    """优雅退出"""
    print(f"gracefully_exit")


async def flush(executor: ProcessPoolExecutor):
    """填充历史形态记录"""
    # 查找续接日期
    newest_record_dt: datetime | None = await (await get_or_create_k_pattern_objects()).scalar(
        PatternRecognizeRecord.select(fn.MAX(PatternRecognizeRecord.pattern_end)))
    if newest_record_dt is not None:
        newest_record_dt = convert_to_sh(newest_record_dt)
    # 分周期处理
    if INTERVALS: await asyncio.wait(
        [asyncio.create_task(handle_interval(newest_record_dt, INTERVAL, executor)) for INTERVAL in INTERVALS])


async def handle_interval(init_datetime: datetime | None, interval: str, executor: ProcessPoolExecutor):
    """处理单个周期"""


if __name__ == '__main__':
    main()
