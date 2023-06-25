import asyncio
import time
from typing import List, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import INTERVALS

# INTERVALS到秒数的转换
interval_secs_map = {"d": 86_400, "4h": 14_400, "1h": 3_600, "30m": 1_800}

schedule_interval = float('inf')


def cronjob_minute():
    """将定时间隔转换成cron job的触发器列表"""
    triggers: List[CronTrigger] = []

    # 计算最小间隔秒数
    global schedule_interval
    schedule_interval = min(interval_secs_map[INTERVAL] for INTERVAL in INTERVALS)
    if schedule_interval < 3600:
        for i in range(3600 // schedule_interval):
            triggers.append(CronTrigger(minute=int(((i + 0.5) * schedule_interval) // 60)))
    else:
        raise NotImplementedError

    return triggers


def interval_filter():
    """根据时间戳决定当前哪个周期的K线有更新"""
    ts = time.time()
    pruned_ts = ts // schedule_interval * schedule_interval

    filtered_intervals = []
    for INTERVAL in INTERVALS:
        if pruned_ts % interval_secs_map[INTERVAL] == 0:
            filtered_intervals.append(INTERVAL)
    return filtered_intervals


def set_scheduler(job: Callable, event_loop: asyncio.get_event_loop()):
    """setup scheduler"""
    # 定时任务
    scheduler = AsyncIOScheduler(event_loop=event_loop)
    triggers = cronjob_minute()
    for trigger in triggers:
        scheduler.add_job(job,
                          trigger=trigger,
                          max_instances=1)
    scheduler.start()
    return scheduler


if __name__ == '__main__':
    schedule_interval = 1800
    print(interval_filter())
