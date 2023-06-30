#输入为一个包含了开盘价和收盘价列的dataframe，dataframe的长度不低于20行，即最新的20行行情数据，满足返回入选时间、开始时间，匹配度，否则返回None
def DTZD(data):

    if len(data) < 20:
        return '传入数据不足'

    l = 20
    s = 5
    m = 10

    curr_open = data['open_price'].iloc[-1]
    curr_close = data['close_price'].iloc[-1]

    ma_s = data['close_price'].rolling(window=s).mean().iloc[-1]
    ma_m = data['close_price'].rolling(window=m).mean().iloc[-1]
    ma_l = data['close_price'].rolling(window=l).mean().iloc[-1]

    # Check for Guillotine
    A = (curr_open > curr_close)
    B = (A and curr_open > ma_s and curr_open > ma_m and curr_open > ma_l)
    result = (B and curr_close < ma_s and curr_close < ma_m and curr_close < ma_l)

    if result:
        return {'EntryTime':data['datetime'].iloc[-1],'StartTime':data['datetime'].iloc[-20],'MatchingScore':1}
    else:
        return None