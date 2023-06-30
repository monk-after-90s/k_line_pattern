#双K线模式，输入为最新的两行dataframe格式行情数据，返回为入选时间和开始时间和匹配度
def WYGD(data):
    if len(data) < 2:
        return '传入数据不足'

    prev_close = data['close_price'].iloc[-2]
    prev_open = data['open_price'].iloc[-2]
    curr_close = data['close_price'].iloc[-1]
    curr_open = data['open_price'].iloc[-1]

    if prev_close / prev_open > 1.03 \
            and curr_close / curr_open < 0.97 \
            and curr_open > prev_close \
            and  curr_close <= (prev_close + prev_open) / 2:

        return {'EntryTime':data['datetime'].iloc[-1],'StartTime':data['datetime'].iloc[-2],'MatchingScore':1}


    else:
        return None