#输入为一个包含了开盘价和收盘价列的dataframe，dataframe的长度不低于20行，即最新的20行行情数据，满足返回入选时间,形态开始时间，匹配度，否则返回None
def CSFR(data):
    if len(data) < 20:
        return '传入数据不足'


    l=20
    s=5
    m=10

    close =data['close_price'].iloc[-1]
    open = data['open_price'].iloc[-1]
    ma_s = data['close_price'].rolling(window=s).mean().iloc[-1]
    ma_m = data['close_price'].rolling(window=m).mean().iloc[-1]
    ma_l = data['close_price'].rolling(window=l).mean().iloc[-1]

    # 判断A、B和CC条件是否成立
    A = (close> open)
    B = (A and close > ma_s and close > ma_m and close > ma_l)
    CC = (B and open < ma_m and open < ma_l)

    # 计算CSFR指标是否满足条件,满足条件则返回data最后一根bar的datatime，否则返回None

    if CC:
        return {'EntryTime':data['datetime'].iloc[-1],'StartTime':data['datetime'].iloc[-20],'MatchingScore':1}
    else:
        return None
