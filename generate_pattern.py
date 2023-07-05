import asyncio
import peewee
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from loguru import logger
from model import DbBarData, get_or_create_k_pattern_objects, KPattern, PatternRecognizeRecord
from pattern_calculator.pattern_calcltor_interface import PatternCalcltor
from typing import Type, List
from utilities import symbol_vnpy2united, VNPY_BN_INTERVAL_MAP
import beeprint


async def cal_and_record_pattern(pattern_calcltor_class: Type[PatternCalcltor],
                                 symbol_exchange_interval_bars: List[DbBarData]):
    """计算和存储K线的形态匹配结果"""
    # K线匹配结果model objects
    k_pattern_objects = await get_or_create_k_pattern_objects()

    # 计算过程的起始时间
    start = asyncio.get_running_loop().time()
    # 匹配结果
    recognize_res = pattern_calcltor_class().calculate(symbol_exchange_interval_bars)

    end = asyncio.get_running_loop().time()
    getattr(logger, "info" if recognize_res is None else "success")(
        beeprint.pp({
            "bar_briefing": f"{symbol_exchange_interval_bars[0].symbol} {symbol_exchange_interval_bars[0].exchange} {symbol_exchange_interval_bars[0].interval}",
            "pattern_calcltor_class": pattern_calcltor_class,
            "cost seconds": end - start,
            "recognize_res": recognize_res},
            output=False,
            sort_keys=False))

    if recognize_res is not None:
        if isinstance(recognize_res, str):
            logger.info(f"{recognize_res=}")
            logger.info(f"{pattern_calcltor_class=}")
        # recognize_res:入选时间,形态开始时间，匹配度，extra
        entry_datetime, start_datetime, matching_score = \
            recognize_res['EntryTime'], recognize_res['StartTime'], recognize_res['MatchingScore']
        extra = {k: v for k, v in recognize_res.items() if k not in ['EntryTime', 'StartTime', 'MatchingScore']}
        # 查询形态
        k_pattern: KPattern = await k_pattern_objects.get(KPattern, KPattern.name == pattern_calcltor_class.name)
        # 存储匹配结果
        for symbol_exchange_interval_bar in symbol_exchange_interval_bars:
            break
        symbol_type, united_symbol = await symbol_vnpy2united(symbol_exchange_interval_bar.exchange,
                                                              symbol_exchange_interval_bar.symbol)
        try:
            await k_pattern_objects.create(
                PatternRecognizeRecord,
                pattern_id=k_pattern.id,
                symbol_type=symbol_type,
                symbol=united_symbol,
                exchange=symbol_exchange_interval_bar.exchange,
                k_interval=VNPY_BN_INTERVAL_MAP[symbol_exchange_interval_bar.interval],
                match_score=matching_score,
                pattern_end=entry_datetime,
                pattern_start=start_datetime,
                extra=extra)
        except peewee.IntegrityError:
            pass
