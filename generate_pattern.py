import asyncio
import uvloop
from sqlalchemy import select, insert

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from loguru import logger
from orm import KPattern, PatternRecognizeRecord, Dbbardata, alrb_asess_fctry
from pattern_calculator.pattern_calcltor_interface import PatternCalcltor
from typing import Type, List
from utilities import symbol_vnpy2united, VNPY_BN_INTERVAL_MAP
import beeprint
from concurrent.futures import ProcessPoolExecutor


async def cal_and_record_pattern_mul_pro(pattern_calcltor_class: Type[PatternCalcltor],
                                         symbol_exchange_interval_bars: List[Dbbardata],
                                         executor: ProcessPoolExecutor,
                                         sem: asyncio.Semaphore = asyncio.Semaphore(100)):
    """计算和存储K线的形态匹配结果，多进程版"""
    try:
        # 格式转换
        for symbol_exchange_interval_bar in symbol_exchange_interval_bars:
            break
        symbol_vnpy2united_task = asyncio.create_task(symbol_vnpy2united(symbol_exchange_interval_bar.exchange,
                                                                         symbol_exchange_interval_bar.symbol))

        # 计算过程的起始时间
        start = asyncio.get_running_loop().time()
        # 匹配结果
        recognize_res = await asyncio.get_running_loop().run_in_executor(executor,
                                                                         pattern_calcltor_class().calculate,
                                                                         symbol_exchange_interval_bars)

        end = asyncio.get_running_loop().time()
        getattr(logger, "success" if isinstance(recognize_res, dict) else "info")(
            beeprint.pp({
                "bar_briefing": f"{symbol_exchange_interval_bars[0].symbol} {symbol_exchange_interval_bars[0].exchange} {symbol_exchange_interval_bars[0].interval}",
                "pattern_calcltor_class": pattern_calcltor_class,
                "cost seconds": end - start,
                "recognize_res": recognize_res},
                output=False,
                sort_keys=False))

        if recognize_res is not None:
            if isinstance(recognize_res, str):
                logger.info(f"""
                {recognize_res=}
                {len(symbol_exchange_interval_bars)=}
                {pattern_calcltor_class=}
                """)

            if isinstance(recognize_res,
                          dict) and 'EntryTime' in recognize_res and 'StartTime' in recognize_res and 'MatchingScore' in recognize_res:

                # 查询形态
                async with alrb_asess_fctry() as session:
                    k_pattern = (await session.execute(
                        select(KPattern).where(KPattern.name == str(pattern_calcltor_class.name)))).scalars().one()
                    # 存储匹配结果
                    symbol_type, united_symbol = await symbol_vnpy2united_task
                    # recognize_res:入选时间,形态开始时间，匹配度，extra
                    entry_datetime, start_datetime, matching_score = \
                        recognize_res['EntryTime'], recognize_res['StartTime'], recognize_res['MatchingScore']
                    extra = {k: v for k, v in recognize_res.items() if
                             k not in ['EntryTime', 'StartTime', 'MatchingScore']}
                async with alrb_asess_fctry() as session:
                    try:
                        async with session.begin():
                            await session.execute(
                                insert(PatternRecognizeRecord).values(
                                    patternId=k_pattern.id,
                                    symbol_type=symbol_type,
                                    symbol=united_symbol,
                                    exchange=symbol_exchange_interval_bar.exchange,
                                    kInterval=VNPY_BN_INTERVAL_MAP[symbol_exchange_interval_bar.interval],
                                    matchScore=matching_score,
                                    patternEnd=entry_datetime,
                                    patternStart=start_datetime,
                                    extra=extra
                                ).prefix_with('IGNORE'))
                            # session.add(
                            #     PatternRecognizeRecord(
                            #         patternId=k_pattern.id,
                            #         symbol_type=symbol_type,
                            #         symbol=united_symbol,
                            #         exchange=symbol_exchange_interval_bar.exchange,
                            #         kInterval=VNPY_BN_INTERVAL_MAP[symbol_exchange_interval_bar.interval],
                            #         matchScore=matching_score,
                            #         patternEnd=entry_datetime,
                            #         patternStart=start_datetime,
                            #         extra=extra
                            #     ))
                    except Exception as e:
                        logger.error("存PatternRecognizeRecord报错:\n" + beeprint.pp(e, output=False, sort_keys=False))
    finally:
        sem.release()
