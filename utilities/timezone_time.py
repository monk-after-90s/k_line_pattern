from sqlalchemy import TypeDecorator, TIMESTAMP, DATETIME
from datetime import datetime
from utilities import convert_to_utc, convert_to_sh


class TimestampWithTimezone(TypeDecorator):
    """可以将MySQL表TIMESTAMP字段反序列化为带有时区信息的datetime的SQLAlchemy字段"""
    impl = TIMESTAMP
    cache_ok = True

    def process_result_value(self, value: datetime, dialect):
        if value is not None:
            # 将结果值转换为带时区的 datetime 对象
            value = convert_to_utc(value)
        return value


class DatetimeWithTimezone(TypeDecorator):
    """可以将MySQL表Datetime字段反序列化为带有时区信息的datetime的SQLAlchemy字段"""
    impl = DATETIME
    cache_ok = True

    def process_result_value(self, value: datetime, dialect):
        if value is not None:
            # 将结果值转换为北京时区的 datetime 对象
            value = convert_to_sh(value)
        return value
