import asyncio

from .bar import get_or_create_bar_objects, DbBarData, DbBarOverview
from .k_pattern import get_or_create_k_pattern_objects, KPattern, PatternRecognizeRecord


async def close_objects():
    await asyncio.gather(close_bar_objects(),
                         close_k_pattern_objects())


async def close_bar_objects():
    from .bar import objects
    # 保守关闭
    if objects is not None:
        await objects.close()


async def close_k_pattern_objects():
    from .k_pattern import objects
    # 保守关闭
    if objects is not None:
        await objects.close()
