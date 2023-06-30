#输入的dataframe不小于5行，满足返回入选时间和开始时间和匹配度，否则返回None
def SJZX(data):
    # 检查是否有至少5天的数据
    if len(data) < 5:
        return None

    # 检查前两天是否都是下跌
    for i in range(-5, -3):
        if data['close_price'].iloc[i] <= data['open_price'].iloc[i]:
            return None

    # 检查第三天是否有很长的下影线
    third_day_entity = abs(data['open_price'].iloc[-3] - data['close_price'].iloc[-3])
    third_day_tail = min(data['open_price'].iloc[-3], data['close_price'].iloc[-3]) - data['low_price'].iloc[-3]
    third_day_uptail=data['high_price'].iloc[-3]-max(data['open_price'].iloc[-3], data['close_price'].iloc[-3])
    if third_day_uptail < 2 * third_day_entity or third_day_uptail<third_day_tail:
        return None

    # 检查后两天是否都是上涨
    for i in range(-2, 0):
        if data['close_price'].iloc[i] >= data['open_price'].iloc[i]:
            return None

    return {'EntryTime':data['datetime'].iloc[-1],'StartTime':data['datetime'].iloc[-5],'MatchingScore':1}