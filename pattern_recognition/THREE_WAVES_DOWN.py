'''
用法示例：
extractor = ThreeWavesDown()
result = extractor.update_bar(data)
只需传入最新的一行数据即可,返回值为形态入选时间和开始时间和匹配度
'''
from collections import deque


class ThreeWavesDown:
    def __init__(self):
        self.bars = deque()  # 用来存储最近的bars以计算趋势
        self.trend = "down"  # 初始趋势设为上涨
        self.segments = deque(maxlen=3)  # 用来存储最近的三个趋势段
        self.segment_trends = deque(maxlen=3)  # 用来存储最近三个趋势段的趋势
        self.segments_indices = deque(maxlen=3)
        self.current_trend=0

    def update_bar(self, bar):
        self.bars.append(bar)
        segment_end = False

        # 如果bars中至少有三个元素，我们可以检查趋势是否改变
        if len(self.bars) > 2:
            self.current_trend = self.trend
            if self.trend == 'up' and self.bars[-1].close_price.iloc[0] < self.bars[-2].close_price.iloc[0] and self.bars[
                -2].close_price.iloc[0] < self.bars[-3].close_price.iloc[0]:
                self.trend = 'down'
                segment_end = True
            elif self.trend == 'down' and self.bars[-1].close_price.iloc[0] > self.bars[-2].close_price.iloc[0] and self.bars[
                -2].close_price.iloc[0] > self.bars[-3].close_price.iloc[0]:
                self.trend = 'up'
                segment_end = True

        if segment_end and len(self.bars) >= 3:
            # 趋势已改变，计算这一段的动量，成交额，以及bar的数量
            momentum = self.bars[-3].close_price.iloc[0] / self.bars[0].open_price.iloc[0] - 1
            turnover = sum(bar.turnover.iloc[0] for bar in list(self.bars)[:-2])  # 不包含最后两个bars，因为它们是新趋势的开始
            bar_num = len(self.bars) - 2  # 同上
            self.segments_indices.append((self.bars[0].datetime.iloc[0], self.bars[-3].datetime.iloc[0]))

            # 将特征和趋势添加到segments和segment_trends中
            self.segments.append((momentum, turnover, bar_num))
            self.segment_trends.append(self.current_trend)
            self.bars = deque(list(self.bars)[-2:])# 清空bars，只保留新趋势的开始的两个bars


            # 如果segments中已经有三个趋势段的特征，将其作为一个元组返回
            if len(self.segments) == 3 and list(self.segment_trends) == ['down', 'up', 'down']:
                if self.segments[0][2] >= 6 and self.segments[1][2] >= 3 and self.segments[2][2] >= 6:
                    if abs(self.segments[0][0])>1.1*abs(self.segments[1][0]) and abs(self.segments[2][0])>1.1*abs(self.segments[1][0]):
                        self.segments.clear()
                        self.segment_trends.clear()
                        return {'EntryTime':list(self.segments_indices)[-1][-1],'StartTime':list(self.segments_indices)[0][0],'MatchingScore':1}

        return None
