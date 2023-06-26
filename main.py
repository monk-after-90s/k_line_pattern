import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from loguru import logger
from apscheduler_job import set_scheduler
from pattern_bars import query_newest_bars
from pattern_calculator import pattern_calcltor_calsses
from apscheduler_job import interval_filter
from concurrent.futures import ProcessPoolExecutor
from functools import partial


async def job(executor: ProcessPoolExecutor):
    """
    单次调度任务

    :param executor: 进程池执行器，用于多进程调用计算密集型函数
    :return:
    """
    ...


def main():
    # 事件循环
    loop = asyncio.get_event_loop()
    # 进程池执行器
    executor = ProcessPoolExecutor()
    # 异步定时器
    aioscheduler = set_scheduler(partial(job, executor=executor), loop)
    try:
        loop.run_forever()
    except:
        logger.info(f"Start gracefully exit")
        aioscheduler.shutdown()
        executor.shutdown()


if __name__ == '__main__':
    main()
