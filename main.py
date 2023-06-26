import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from loguru import logger
from apscheduler_job import set_scheduler
from pattern_bars import query_newest_bars
from pattern_calculator import pattern_calcltor_calsses
from apscheduler_job import interval_filter
from functools import partial


async def job():
    """
    单次调度任务

    :return:
    """
    ...


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


if __name__ == '__main__':
    main()
