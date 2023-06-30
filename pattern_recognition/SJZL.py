'''
调用方法如下：
pattern_analyzer = SanJiaoZhengLi(data，interval)
pattern_analyzer.analyse_pattern()

data为dataframe格式，最小行数为35行，即最近的35根K线数据
如果不符合条件则返回None,如果符合则返回5个值，第一个值为入选时间datetime，第二个值为开始时间，，第三个值为匹配度，第四个值为上边界线两点datetime，第五个值为下边界线两点datetime

'''
import numpy as np
from scipy.signal import argrelextrema
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

class SanJiaoZhengLi:
    def __init__(self, data,interval='d'):
        scaler = MinMaxScaler()
        normalized_high = scaler.fit_transform(data['high_price'].values.reshape(-1, 1)).flatten()
        normalized_low = scaler.fit_transform(data['low_price'].values.reshape(-1, 1)).flatten()

        self.normalized_data = pd.DataFrame({'high_price': normalized_high, 'low_price': normalized_low, 'datetime': data['datetime']})
        self.normalized_data.index = data.index
        self.data=data.iloc[-35:]
        self.normalized_data=self.normalized_data.iloc[-35:]
        self.order = 2
        if interval=='d':
            self.tolerance = 0.015
        elif interval=='4h':
            self.tolerance=0.0025
        elif interval=='1h':
            self.tolerance=0.0015
        elif interval=='30m':
            self.tolerance=0.0015

    def find_extrema(self):
        highs = self.normalized_data['high_price']
        lows = self.normalized_data['low_price']

        maxima_indices = argrelextrema(highs.values, np.greater, order=self.order)[0]
        minima_indices = argrelextrema(lows.values, np.less, order=self.order)[0]

        # If we haven't found enough extrema, return None
        if len(maxima_indices) < 2 or len(minima_indices) < 2:
            return None,None

        top_two_highs = sorted([(i, highs.iloc[i]) for i in maxima_indices], key=lambda x: x[1], reverse=True)[:2]
        top_two_lows = sorted([(i, lows.iloc[i]) for i in minima_indices], key=lambda x: x[1])[:2]

        return top_two_highs, top_two_lows

    def analyse_pattern(self):
        top_two_highs, top_two_lows = self.find_extrema()

        if top_two_highs is None or top_two_lows is None:
            return None

        if len(self.normalized_data)<35:
            return None

        highs = self.normalized_data['high_price']
        lows = self.normalized_data['low_price']

        line_high_normalized = np.poly1d(np.polyfit([x[0] for x in top_two_highs], [x[1] for x in top_two_highs], 1))
        line_low_normalized = np.poly1d(np.polyfit([x[0] for x in top_two_lows], [x[1] for x in top_two_lows], 1))

        for x in range(len(highs)):
            if highs.iloc[x] > line_high_normalized(x) * (1 + self.tolerance):
                return None

        for x in range(len(lows)):
            if lows.iloc[x] < line_low_normalized(x) * (1 - self.tolerance):
                return None

        slope_high = line_high_normalized[1]
        slope_low = line_low_normalized[1]

        if slope_high <= -0.005 and slope_low >= 0.005:

            high_index = [self.data['datetime'].iloc[x[0]] for x in top_two_highs]
            low_index = [self.data['datetime'].iloc[x[0]] for x in top_two_lows]

            return {'EntryTime': self.data['datetime'].iloc[-1], 'StartTime': self.data['datetime'].iloc[-20],
                    'MatchingScore': 1,
                    'UpperBound': (high_index[0], high_index[1]), 'Lower Bound': (low_index[0], low_index[1])}
        else:
            return None