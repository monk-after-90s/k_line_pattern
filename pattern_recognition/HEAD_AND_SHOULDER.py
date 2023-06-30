'''
用法示例：
result = find_head_and_shoulders(data,interval)
传入的data长度不小于150，即最近的150根K线，格式为dataframe;interval默认d,可填写4个周期，d,4h,1h,30m
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

def generate_head_and_shoulders(length=10, shoulder_height_ratio=0.6, head_height_ratio=1.0):
    assert 0 < shoulder_height_ratio < head_height_ratio, "Shoulder height ratio must be less than head height ratio."

    # 分配长度
    left_shoulder_length =int(length*0.8)
    head_length = length
    right_shoulder_length =int(length*0.8)

    # 左肩上升和下降阶段
    left_shoulder_rise = np.linspace(0, shoulder_height_ratio, left_shoulder_length)
    left_shoulder_fall = np.linspace(shoulder_height_ratio, 0, left_shoulder_length)

    # 头部上升和下降阶段
    head_rise = np.linspace(0, head_height_ratio, head_length)
    head_fall = np.linspace(head_height_ratio, 0, head_length)

    # 右肩上升和下降阶段
    right_shoulder_rise = np.linspace(0, shoulder_height_ratio, right_shoulder_length)
    right_shoulder_fall = np.linspace(shoulder_height_ratio, 0, right_shoulder_length)

    # 拼接形态
    head_and_shoulders = np.concatenate((left_shoulder_rise, left_shoulder_fall, head_rise, head_fall, right_shoulder_rise, right_shoulder_fall))


    return head_and_shoulders

def find_head_and_shoulders(data,interval='d'):

    if len(data) < 150:
        return '传入数据不足'
    # 计算50天的涨幅
    min_pattern_length = 10
    max_pattern_length = 21
    correlation_threshold = 0.7

    min_distance = float('inf')
    min_pattern_length_for_i = -1

    if interval == 'd':
        yuzhi = 1.05
    elif interval == '4h':
        yuzhi = 1.035
    elif interval == '1h':
        yuzhi = 1.02
    elif interval == '30m':
        yuzhi = 1.01


    # 满足上涨条件后，接下来的pattern_length天内寻找M顶形态
    for pattern_length in range(min_pattern_length, max_pattern_length,5):
        price_increase=data['close_price'].iloc[-105]/data['close_price'].iloc[-150]

        if price_increase>=yuzhi:
            window_data = data['close_price'].iloc[-105:-105 + int(5.2*pattern_length)].to_numpy()
            window_data = normalize_series(window_data)  # reshape the data to 2D

            head_shoulder = generate_head_and_shoulders(pattern_length)
            head_shoulder = normalize_series(head_shoulder)

            distance, _ = fastdtw(head_shoulder, window_data, dist=euclidean)
            # 如果距离小于当前最小距离，更新最小距离和对应的模式长度
            if distance < min_distance:
                min_distance = distance
                min_pattern_length_for_i = pattern_length
        else:
            return None

    # 将每个 i 对应的最小距离和模式长度添加到结果列表
    window_data = data['close_price'].iloc[
                  -105:-105 + int(5.2*min_pattern_length_for_i)].to_numpy()

    head_shoulder_for_correlation = generate_head_and_shoulders(min_pattern_length_for_i)

    correlation, _ = pearsonr(window_data, head_shoulder_for_correlation)

    # 如果相关性大于阈值，将每个 i 对应的最小距离和模式长度添加到结果列表
    if correlation > correlation_threshold:
        datetime_end = data['datetime'].iloc[-105 + int(5.2*min_pattern_length_for_i) - 1]
        datetime_start=data['datetime'].iloc[-105]
        # 有符合条件的形态则返回datetime,和匹配度，否则返回None
        return  {'EntryTime':datetime_end,'StartTime':datetime_start,'MatchingScore':correlation}

    return None