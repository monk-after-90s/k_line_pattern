"""使pandas的Timestamp对象可以JSON serializable到peewee model的JSONField"""
import json
from playhouse.mysql_ext import JSONField

import pandas as pd


class TimestampEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, pd.Timestamp):
            return super().default(obj)
        return obj.isoformat()


class TimestampJSONField(JSONField):
    """使pandas的Timestamp对象可以JSON serializable到peewee model的JSONField"""

    def db_value(self, value):
        if value is not None:
            return json.dumps(value, cls=TimestampEncoder)
