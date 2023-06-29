from typing import Optional
import asyncio
import peewee_async
from peewee import *
import config
from utilities import TimestampJSONField

db = peewee_async.MySQLDatabase(database=config.DB,
                                user=config.DB_USER,
                                password=config.DB_PASSWD,
                                host=config.DB_HOST,
                                port=config.DB_PORT)
db.set_allow_sync(True)
objects: Optional[peewee_async.Manager] = None


async def get_or_create_k_pattern_objects():
    """获取K线形态数据库的入口objects"""
    global objects
    if objects is None:
        objects = peewee_async.Manager(db, loop=asyncio.get_event_loop())
    return objects


class BaseModel(Model):
    is_delete = IntegerField(constraints=[SQL("DEFAULT 0")])
    create_id = IntegerField(constraints=[SQL("DEFAULT 0")])
    create_ts = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    update_id = IntegerField(constraints=[SQL("DEFAULT 0")])
    update_ts = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

    class Meta:
        database = db

    @classmethod
    def select(cls, *selection):
        # Overriding select to add filter condition
        return super().select(*selection).where(cls.is_delete == 0)


class KPattern(BaseModel):
    name = CharField()
    description = CharField(null=True)
    image_url = CharField(column_name='imageUrl', null=True)

    class Meta:
        table_name = 'k_pattern'


class PatternRecognizeRecord(BaseModel):
    extra = TimestampJSONField(null=True)  # json
    match_score = FloatField(column_name='matchScore')
    pattern_end = DateTimeField(column_name='patternEnd', constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    pattern_id = IntegerField(column_name='patternId')
    pattern_start = DateTimeField(column_name='patternStart', constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    exchange = CharField()
    symbol_type = CharField()  # 市场类型:spot、futures
    symbol = CharField()  # 市场符号，如BTC/USDT
    k_interval = CharField(column_name='kInterval')  # K线Interval，如1d，4h，币安标准

    class Meta:
        table_name = 'pattern_recognize_record'
        indexes = (
            (('pattern_id', 'symbol_type', 'symbol', 'k_interval', 'pattern_start', 'pattern_end'), True),
        )
