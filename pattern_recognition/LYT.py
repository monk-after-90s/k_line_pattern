'''
用法示例：
result = find_duck_head(data)
传入的data长度不小于105，即最近的105根K线，格式为dataframe,满足返回3个值，
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

def generate_duck_head(length=10, amplitude=1.0):
    # 颈部: 二次函数，斜率逐渐增大
    x1 = np.linspace(0, 1, length)
    neck = amplitude * (x1 ** 2)

    # 头部: 半圆弧
    x2 = np.linspace(0, np.pi, length)
    head = amplitude * np.sin(x2) + neck[-1]

    # 嘴部: 二次函数
    x3 = np.linspace(0, 1, length)
    mouth = 2 * amplitude * (x3 ** 2) + head[-1]

    # 将三个部分连接在一起
    duck_head = np.concatenate((neck, head, mouth))

    return duck_head

def find_duck_head(data):

    if len(data) < 105:
        return '传入数据不足'

    min_pattern_length=10
    max_pattern_length=35
    correlation_threshold=0.7

    # 初始化一个变量来跟踪最小距离和对应的模式长度
    min_distance = float('inf')
    min_pattern_length_for_i = -1

    # 满足上涨条件后，接下来的pattern_length天内寻找M顶形态
    for pattern_length in range(min_pattern_length, max_pattern_length):
        window_data = data['close_price'].iloc[-max_pattern_length*3:-max_pattern_length*3+pattern_length*3].to_numpy()
        window_data = normalize_series(window_data)  # reshape the data to 2D

        duck_head = generate_duck_head(pattern_length)
        duck_head = normalize_series(duck_head)

        distance, _ = fastdtw(duck_head, window_data, dist=euclidean)
        distance=distance/pattern_length
        # 如果距离小于当前最小距离，更新最小距离和对应的模式长度
        if distance < min_distance:
            min_distance = distance
            min_pattern_length_for_i = pattern_length

    # 将每个 i 对应的最小距离和模式长度添加到结果列表
    window_data = data['close_price'].iloc[-max_pattern_length*3:-max_pattern_length*3+min_pattern_length_for_i*3].to_numpy()
    duck_head_for_correlation = generate_duck_head(min_pattern_length_for_i)
    correlation, _ = pearsonr(window_data, duck_head_for_correlation)

    # 如果相关性大于阈值，将形态结束时间和匹配度返回
    if correlation > correlation_threshold:
        datetime_end= data['datetime'].iloc[-max_pattern_length*3+min_pattern_length_for_i*3-1]
        datetime_start=data['datetime'].iloc[-max_pattern_length*3]
        #有符合条件的形态则返回datetime,和匹配度，否则返回None
        return  {'EntryTime':datetime_end,'StartTime':datetime_start,'MatchingScore':correlation}

    return None