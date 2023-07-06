import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from loguru import logger
from apscheduler_job import set_scheduler
from pattern_bars import query_newest_bars
from pattern_calculator import pattern_calcltor_classes
from apscheduler_job import interval_filter
from orm import close_engines
import beeprint
import signal
import os
from generate_pattern import cal_and_record_pattern_mul_pro
from concurrent.futures import ProcessPoolExecutor
from functools import partial


async def job(executor: ProcessPoolExecutor):
    """
    单次调度任务

    :return:
    """
    # 获取有更新的K线间隔
    intervals = interval_filter()
    logger.info(f"intervals with new kline updated: {intervals}")
    # 获取bars
    symbol_exchange_interval_barses = await query_newest_bars(intervals)
    logger.info(
        f"""symbol_exchange_interval_barses=\n{
        beeprint.pp(
            [(f"{len(symbol_exchange_interval_bars)=}",
              f"{symbol_exchange_interval_bars[0].exchange} {symbol_exchange_interval_bars[0].symbol} {symbol_exchange_interval_bars[0].interval} {symbol_exchange_interval_bars[0].datetime}",
              f"{symbol_exchange_interval_bars[-1].exchange} {symbol_exchange_interval_bars[-1].symbol} {symbol_exchange_interval_bars[-1].interval} {symbol_exchange_interval_bars[-1].datetime}")
             for symbol_exchange_interval_bars in symbol_exchange_interval_barses],
            output=False,
            sort_keys=False)}""")

    tasks = []
    # 获取pattern_calcltor类
    for pattern_calcltor_class in pattern_calcltor_classes:
        # 将bars给pattern_calcltor消化
        for symbol_exchange_interval_bars in symbol_exchange_interval_barses:
            tasks.append(asyncio.create_task(
                cal_and_record_pattern_mul_pro(pattern_calcltor_class, symbol_exchange_interval_bars, executor)))

    [await task for task in tasks]


# 事件循环
loop: asyncio.BaseEventLoop | None = None


def handle_sigterm(sig, frame):
    # 暂停事件循环
    loop.stop()


signal.signal(signal.SIGTERM, handle_sigterm)


async def gracefully_exit():
    """优雅退出"""
    await close_engines()


def main():
    logger.warning(f"请手动确保运行在了东八区")
    if os.environ.get("PYTHONUNBUFFERED") == "1":
        logger.info(f"development mode")

    global loop
    # 事件循环
    loop = asyncio.get_event_loop()
    # 多进程执行器
    executor = ProcessPoolExecutor()
    # 异步定时器
    aioscheduler = set_scheduler(partial(job, executor), loop)
    try:
        loop.run_forever()
    finally:
        logger.info(f"Start gracefully exit")
        aioscheduler.shutdown()
        loop.run_until_complete(gracefully_exit())
        executor.shutdown()
        logger.info(f"Finish gracefully exit")


if __name__ == '__main__':
    main()
