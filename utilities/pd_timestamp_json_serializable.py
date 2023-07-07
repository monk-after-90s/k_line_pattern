"""使pandas的Timestamp对象可以JSON serializable到SQLAlchemy model的JSON字段类型"""
import json
from .convert_pd_timestamp import convert_to_sh, convert_to_utc
import pandas as pd
from sqlalchemy import JSON, TypeDecorator


class TimestampEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, pd.Timestamp):
            return super().default(obj)
        # 无时区信息则为北京时区
        if obj.tzinfo is None:
            obj = convert_to_sh(obj)
        obj = convert_to_utc(obj)
        return obj.isoformat()


class TimestampJSONField(TypeDecorator):
    """使pandas的Timestamp对象可以JSON serializable到SQLAlchemy model的JSON字段类型"""
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        try:
            json_s = json.dumps(value, cls=TimestampEncoder)
            value = json.loads(json_s)
        finally:
            return value
