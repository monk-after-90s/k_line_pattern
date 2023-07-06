import asyncio
from typing import Optional
import config
import peewee_async
from peewee import *
from datetime import datetime

db = peewee_async.MySQLDatabase(database=config.DB1,
                                user=config.DB_USER1,
                                password=config.DB_PASSWD1,
                                host=config.DB_HOST1,
                                port=config.DB_PORT1)
db.set_allow_sync(True)
objects: Optional[peewee_async.Manager] = None


async def get_or_create_bar_objects():
    """获取K线柱子数据数据库的入口objects"""
    global objects
    if objects is None:
        objects = peewee_async.Manager(db, loop=asyncio.get_event_loop())
    return objects


class BaseModel(Model):
    class Meta:
        database: peewee_async.MySQLDatabase = db


class DbBarData(BaseModel):
    """K线数据表映射对象"""

    id: AutoField = AutoField()

    symbol: str = CharField()
    exchange: str = CharField()
    datetime: datetime = DateTimeField()
    interval: str = CharField()

    volume: float = FloatField()
    turnover: float = FloatField()
    open_interest: float = FloatField()
    open_price: float = FloatField()
    high_price: float = FloatField()
    low_price: float = FloatField()
    close_price: float = FloatField()

    class Meta:
        indexes: tuple = ((("symbol", "exchange", "interval", "datetime"), True),)


class DbBarOverview(BaseModel):
    """K线汇总数据表映射对象"""
    count = IntegerField()
    end = DateTimeField()
    exchange = CharField()
    interval = CharField()
    start = DateTimeField()
    symbol = CharField()

    class Meta:
        table_name = 'dbbaroverview'
        indexes = (
            (('symbol', 'exchange', 'interval'), True),
        )