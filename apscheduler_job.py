import asyncio
import datetime
import os
import time
from typing import List, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import INTERVALS
from utilities import INTERVAL_SECS_MAP as interval_secs_map
from apscheduler.util import undefined
from utilities import find_gcd

schedule_interval = float('inf')


def interval_to_cron_triggers():
    """将定时间隔转换成cron job的触发器列表"""
    triggers: List[CronTrigger] = []

    # 计算最小间隔秒数
    global schedule_interval
    schedule_interval = find_gcd([interval_secs_map[INTERVAL] for INTERVAL in INTERVALS])
    if schedule_interval < 3600:
        for i in range(3600 // schedule_interval):
            triggers.append(CronTrigger(minute=int(((i + 0.5) * schedule_interval) // 60)))
    else:
        raise NotImplementedError

    return triggers


def interval_filter():
    """根据时间戳决定当前哪个周期的K线有更新"""
    if os.environ.get("PYTHONUNBUFFERED") == "1":
        return ['1h']

    ts = time.time()
    pruned_ts = ts // schedule_interval * schedule_interval

    filtered_intervals = []
    for INTERVAL in INTERVALS:
        if pruned_ts % interval_secs_map[INTERVAL] == 0:
            filtered_intervals.append(INTERVAL)
    return filtered_intervals


def set_scheduler(job: Callable, event_loop: asyncio.get_event_loop(), start=False):
    """setup scheduler"""
    # 定时任务
    scheduler = AsyncIOScheduler(event_loop=event_loop)
    triggers = interval_to_cron_triggers()

    # 立即触发标识，用于开发
    next_run_time_set = False
    # 定时trigger绑定job
    for trigger in triggers:
        scheduler.add_job(
            job,
            trigger=trigger,
            max_instances=1,
            next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=1)
            if os.environ.get("PYTHONUNBUFFERED") == "1" and not next_run_time_set else undefined)
        next_run_time_set = True
    if start:
        scheduler.start()
    return scheduler


if __name__ == '__main__':
    schedule_interval = 1800
    print(interval_filter())
