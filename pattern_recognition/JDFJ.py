#输入的dataframe不小于5行，满足返回入选时间和开始时间和匹配度，否则返回None
def JDFJ(data):
    # 检查是否有至少5天的数据
    if len(data) < 5:
        return '传入数据不足'

    # 计算前四天是否下跌
    if data['close_price'].iloc[-2]>data['close_price'].iloc[-5]:
        return None

    # 检查前四天有至少3天是阴线
    down_days = sum(data['close_price'].iloc[i] < data['open_price'].iloc[i] for i in range(-5, -1))
    if down_days < 3:
        return None

        # 获取前四天的最大开盘价和最大收盘价
    max_open = max(data['open_price'].iloc[-5:-1])
    max_close = max(data['close_price'].iloc[-5:-1])

    # 判断第五天的收盘价是否大于这两个值
    if data['close_price'].iloc[-1] > data['open_price'].iloc[-1] and data['close_price'].iloc[-1] > max_open and data['close_price'].iloc[
        -1] > max_close:
        return {'EntryTime':data['datetime'].iloc[-1],'StartTime':data['datetime'].iloc[-5],'MatchingScore':1}
    else:
        return None
