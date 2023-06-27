import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from loguru import logger
from apscheduler_job import set_scheduler
from pattern_bars import query_newest_bars
from pattern_calculator import pattern_calcltor_calsses
from apscheduler_job import interval_filter
from model import DbBarData, get_or_create_k_pattern_objects, KPattern, PatternMatchRecord, close_objects
from pattern_calculator.pattern_calcltor_interface import PatternCalcltor
from typing import Type, Iterable
from utilities import symbol_vnpy2united, VNPY_BN_INTERVAL_MAP


async def job():
    """
    单次调度任务

    :return:
    """
    # 获取有更新的K线间隔
    intervals = interval_filter()
    logger.info(f"intervals with new kline: {intervals}")
    # 获取bars
    symbol_exchange_interval_barses = await query_newest_bars(intervals)

    tasks = []
    # 获取pattern_calcltor类
    for pattern_calcltor_class in pattern_calcltor_calsses:
        # 将bars给pattern_calcltor消化
        for symbol_exchange_interval_bars in symbol_exchange_interval_barses:
            tasks.append(
                cal_and_record_pattern(pattern_calcltor_class, symbol_exchange_interval_bars))

    [await task for task in tasks]


async def cal_and_record_pattern(pattern_calcltor_calss: Type[PatternCalcltor],
                                 symbol_exchange_interval_bars: Iterable[DbBarData]):
    """计算和存储K线的形态匹配结果"""
    # K线匹配结果model objects
    k_pattern_objects = await get_or_create_k_pattern_objects()

    # 计算过程的起始时间
    start = asyncio.get_running_loop().time()
    # 匹配结果
    match_res = pattern_calcltor_calss().calculate(symbol_exchange_interval_bars)

    end = asyncio.get_running_loop().time()
    logger.info(f"{pattern_calcltor_calss} calculation spends:{end - start} seconds")

    if match_res is not None:
        # match_res:入选时间,形态开始时间，匹配度，extra
        entry_datetime, start_datetime, matching_score = \
            match_res['EntryTime'], match_res['StartTime'], match_res['MatchingScore']
        extra = {k: v for k, v in match_res.items() if k not in ['EntryTime', 'StartTime', 'MatchingScore']}
        # 查询形态
        k_pattern: KPattern = await k_pattern_objects.get(KPattern, KPattern.name == pattern_calcltor_calss.name)
        # 存储匹配结果
        for symbol_exchange_interval_bar in symbol_exchange_interval_bars:
            break
        await k_pattern_objects.create(
            PatternMatchRecord,
            pattern_id=k_pattern.id,
            symbol=await symbol_vnpy2united(symbol_exchange_interval_bar.exchange,
                                            symbol_exchange_interval_bar.symbol),
            k_interval=VNPY_BN_INTERVAL_MAP[symbol_exchange_interval_bar.interval],
            match_degree=matching_score,
            pattern_end=entry_datetime,
            pattern_start=start_datetime,
            extra=extra)


async def gracefully_exit():
    """优雅退出"""
    await close_objects()


def main():
    # 事件循环
    loop = asyncio.get_event_loop()
    # 异步定时器
    aioscheduler = set_scheduler(job, loop)
    try:
        loop.run_forever()
    except:
        logger.info(f"Start gracefully exit")
        aioscheduler.shutdown()
        loop.run_until_complete(gracefully_exit())
        logger.info(f"Finish gracefully exit")


if __name__ == '__main__':
    main()
