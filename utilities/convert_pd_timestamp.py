from pandas import Timestamp
from pytz import timezone

beijing_tz = timezone('Asia/Shanghai')


def convert_to_sh(ts: Timestamp) -> Timestamp:
    """
    将Timestamp转成上海时区
    ts带时区信息的话根据时区转，否则直接加上上海时区
    """
    if ts.tzinfo is not None:  # tz aware转成北京时区
        ts_beijing = ts.tz_convert('Asia/Shanghai')
    else:  # tz naive到北京时区
        ts_beijing = ts.tz_localize('Asia/Shanghai')
        assert ts_beijing.tzinfo
    return ts_beijing


def convert_to_utc(ts: Timestamp) -> Timestamp:
    """
    将Timestamp转成UTC时区
    ts带时区信息的话根据时区转，否则直接加上UTC时区
    """
    if ts.tzinfo is not None:  # tz aware转成UTC时区
        ts_utc = ts.tz_convert('UTC')
    else:  # tz naive到UTC时区
        ts_utc = ts.tz_localize('UTC')
        assert ts_utc.tzinfo

    return ts_utc
