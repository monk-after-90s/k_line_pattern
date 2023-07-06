"""填充历史"""
import asyncio
import os
from datetime import datetime, timedelta
from functools import partial
from typing import Iterable, List
import beeprint
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from peewee import fn
from apscheduler_job import set_scheduler
from config import INTERVALS
from generate_pattern import cal_and_record_pattern_mul_pro
from realtime_recognize import job
from utilities import handle_sigterm, symbol_vnpy2united, VNPY_BN_INTERVAL_MAP
from loguru import logger
from orm import get_or_create_k_pattern_objects, PatternRecognizeRecord, get_or_create_bar_objects, DbBarOverview, \
    DbBarData
from utilities import INTERVAL_SECS_MAP as interval_secs_map
from concurrent.futures import ProcessPoolExecutor
from pattern_calculator import pattern_calcltor_classes
from config import SEMAPHORE_VALUE

sem = asyncio.Semaphore(SEMAPHORE_VALUE)


def main():
    logger.warning(f"请手动确保运行在了东八区")
    if os.environ.get("PYTHONUNBUFFERED") == "1":
        logger.info(f"development mode")

    # 事件循环
    loop = asyncio.get_event_loop()
    handle_sigterm(loop)
    # 多进程执行器
    executor = ProcessPoolExecutor()
    # 异步定时器
    aioscheduler: AsyncIOScheduler = set_scheduler(partial(job, executor), loop)
    # 添加任务
    loop.create_task(flush(executor, aioscheduler))
    try:
        loop.run_forever()
    finally:
        logger.info(f"Start gracefully exit")
        aioscheduler.shutdown()
        loop.run_until_complete(gracefully_exit())
        executor.shutdown()
        logger.info(f"Finish gracefully exit")


async def gracefully_exit():
    """优雅退出"""
    print(f"gracefully_exit")


async def flush(executor: ProcessPoolExecutor, aioscheduler: AsyncIOScheduler):
    """填充历史形态记录"""
    interval_last_record_es = []
    handle_interval_tasks = []
    # 分周期处理
    for INTERVAL in INTERVALS:
        interval_last_record_e = asyncio.Event()
        handle_interval_tasks.append(
            asyncio.create_task(handle_interval(INTERVAL, executor, interval_last_record_e)))
        interval_last_record_es.append(interval_last_record_e)
    # 等待所有周期查询完续接日期的事件
    await asyncio.gather(*(interval_last_record_e.wait() for interval_last_record_e in interval_last_record_es))
    # 启动实时形态匹配
    logger.info("启动实时形态匹配")
    aioscheduler.start()

    await asyncio.gather(*handle_interval_tasks)

    logger.success("填充历史形态记录 完成")


async def handle_interval(interval: str, executor: ProcessPoolExecutor, interval_last_record_e: asyncio.Event):
    """
    处理单个周期

    interval_last_record_e: 整个周期查询完续接日期的事件
    """
    # 获取symbol配置，分配任务
    bar_objects = await get_or_create_bar_objects()
    # 获取symbol配置
    bar_configs: Iterable[DbBarOverview] = await bar_objects.execute(
        DbBarOverview.select().where(DbBarOverview.interval == interval))
    # 查询PatternRecognizeRecord最后日期结束的事件 列表
    last_record_es = []
    handle_symbol_interval_tasks = []
    for bar_config in bar_configs:
        last_record_e = asyncio.Event()
        handle_symbol_interval_tasks.append(
            asyncio.create_task(
                handle_symbol_interval(bar_config.symbol,
                                       bar_config.exchange,
                                       bar_config.interval,
                                       executor,
                                       last_record_e)))
        last_record_es.append(last_record_e)
    # 等待全部"查找续接日期"完成
    await asyncio.gather(*(last_record_e.wait() for last_record_e in last_record_es))
    # 触发整个周期查询完续接日期的事件
    interval_last_record_e.set()
    return await asyncio.gather(*handle_symbol_interval_tasks)


async def handle_symbol_interval(symbol,
                                 exchange,
                                 interval,
                                 executor: ProcessPoolExecutor,
                                 last_record_e: asyncio.Event):
    """
    处理单个symbol的单个interval的K线序列

    last_record_e: 查询PatternRecognizeRecord最后日期结束的事件
    """
    bar_objects = await get_or_create_bar_objects()

    # 格式转换
    symbol_type, united_symbol = await asyncio.create_task(symbol_vnpy2united(exchange,
                                                                              symbol))
    # 查找续接日期
    init_bar_datetime: datetime | None = await (await get_or_create_k_pattern_objects()).scalar(
        PatternRecognizeRecord.select(fn.Max(PatternRecognizeRecord.pattern_end)).where(
            (PatternRecognizeRecord.exchange == exchange) &
            (PatternRecognizeRecord.symbol_type == symbol_type) &
            (PatternRecognizeRecord.symbol == united_symbol) &
            (PatternRecognizeRecord.k_interval == VNPY_BN_INTERVAL_MAP[interval])))
    # 查询PatternRecognizeRecord最后日期完成
    last_record_e.set()

    if init_bar_datetime is None:
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
            # 查bar查到了现在
            if init_bar_datetime is not None and init_bar_datetime > datetime.now():
                break
            # 计算并存储pattern_calcltor值
            for pattern_calcltor_class in pattern_calcltor_classes:
                # 信号量控制并发
                await sem.acquire()
                asyncio.create_task(cal_and_record_pattern_mul_pro(pattern_calcltor_class, bars, executor, sem))

            # datetime步进
            init_bar_datetime += timedelta(seconds=interval_secs_map[interval])


if __name__ == '__main__':
    main()
