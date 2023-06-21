import asyncio
from typing import List, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import INTERVALS

# INTERVALS到秒数的转换
interval_secs_map = {"d": 86_400, "4h": 14_400, "1h": 3_600, "30m": 1_800}


def cronjob_minute():
    """将定时间隔转换成cron job的触发器列表"""
    triggers: List[CronTrigger] = []

    # 计算最小间隔秒数
    schedule_interval = min(interval_secs_map[INTERVAL] for INTERVAL in INTERVALS)
    if schedule_interval < 3600:
        for i in range(3600 // schedule_interval):
            triggers.append(CronTrigger(minute=int(((i + 0.5) * schedule_interval) // 60)))
    else:
        raise NotImplementedError

    return triggers


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
