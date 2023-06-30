#输入为不低于30行的dataframe，返回为入选时间，开始时间，匹配度
import numpy as np

def GOLDEN_PIT(data,interval='d'):
    # 检查是否有至少30天的数据
    if len(data) < 30:
        return None

    if interval == 'd':
        yuzhi1 = 0.05
        yuzhi2=0.05
    elif interval == '4h':
        yuzhi1=0.035
        yuzhi2=0.035
    elif interval == '1h':
        yuzhi1 = 0.02
        yuzhi2=0.02
    elif interval == '30m':
        yuzhi1 = 0.015
        yuzhi2=0.015

    # 检查前10天是否都是下跌
    if data['close_price'].iloc[-20]/data['close_price'].iloc[-30]>1-yuzhi1:
        return None

    # 检查中间10天是否是震荡区域
    bofu=np.max(data['high_price'].iloc[-20:-10])/np.min(data['low_price'].iloc[-20:-10])
    if bofu >1+yuzhi2:
        return None

    # 检查后10天是否都是上涨
    if data['close_price'].iloc[-1]/data['close_price'].iloc[-10]<1+yuzhi1:
        return None

    return {'EntryTime':data['datetime'].iloc[-1],'StartTime':data['datetime'].iloc[-30],'MatchingScore':1}
