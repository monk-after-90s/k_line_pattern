'''
用法示例：
result = find_w_bottom(data,interval)
传入的data长度不小于100，即最近的100根K线，格式为dataframe;interval默认d,可填写4个周期，d,4h,1h,30m
满足返回3个值:
第一个值为入选时间，第二个值为开始时间，第三个值为匹配度，否则返回None
'''
import numpy as np
from scipy.stats import pearsonr
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

def normalize_series(series):
    a=(series - series.min()) / (series.max() - series.min())
    a=np.array(a)
    a=np.reshape(a, (-1, 1))
    return a

def generate_w_bottom(length=10, amplitude=1.0, start_phase=0.5* np.pi, end_phase=4.5 * np.pi):
    x = np.linspace(start_phase, end_phase, length)
    y = amplitude * np.sin(x)
    w_bottom = y - y.min()
    return w_bottom

def find_w_bottom(data,interval='d'):

    if len(data) < 100:
        return '传入数据不足'
    # 计算50天的涨幅
    min_pattern_length = 24
    max_pattern_length = 50
    correlation_threshold = 0.7

    min_distance = float('inf')
    min_pattern_length_for_i = -1



    if interval=='d':
        yuzhi=0.95
    elif interval=='4h':
        yuzhi=0.965
    elif interval=='1h':
        yuzhi=0.98
    elif interval=='30m':
        yuzhi=0.99


    # 满足上涨条件后，接下来的pattern_length天内寻找M顶形态
    for pattern_length in range(min_pattern_length, max_pattern_length):
        price_increase=data['close_price'].iloc[-max_pattern_length]/data['close_price'].iloc[-2*max_pattern_length]

        if price_increase<=yuzhi:
            window_data = data['close_price'].iloc[-max_pattern_length:-max_pattern_length + pattern_length].to_numpy()
            window_data = normalize_series(window_data)  # reshape the data to 2D

            w_bottom = generate_w_bottom(pattern_length)
            w_bottom = normalize_series(w_bottom)

            distance, _ = fastdtw(w_bottom, window_data, dist=euclidean)
            # 如果距离小于当前最小距离，更新最小距离和对应的模式长度
            if distance < min_distance:
                min_distance = distance
                min_pattern_length_for_i = pattern_length
        else:
            return None

    # 将每个 i 对应的最小距离和模式长度添加到结果列表
    window_data = data['close_price'].iloc[
                  -max_pattern_length:-max_pattern_length + min_pattern_length_for_i].to_numpy()

    w_bottom_for_correlation = generate_w_bottom(min_pattern_length_for_i)
    correlation, _ = pearsonr(window_data, w_bottom_for_correlation)

    # 如果相关性大于阈值，将每个 i 对应的最小距离和模式长度添加到结果列表
    if correlation > correlation_threshold:
        datetime_end = data['datetime'].iloc[-max_pattern_length + min_pattern_length_for_i - 1]
        datetime_start = data['datetime'].iloc[-max_pattern_length]
        # 有符合条件的形态则返回datetime,和匹配度，否则返回None
        return  {'EntryTime':datetime_end,'StartTime':datetime_start,'MatchingScore':correlation}

    return None