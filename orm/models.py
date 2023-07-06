from typing import List
from utilities import TimestampWithTimezone, DatetimeWithTimezone
from sqlalchemy import Column, Float, Index, JSON, String, Table, text, ForeignKey, Integer
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class CommonColumn(Base):
    __abstract__ = True

    id = mapped_column(INTEGER, primary_key=True)
    is_delete = mapped_column(TINYINT(1), nullable=False, server_default=text("'0'"),
                              comment='删除标识 0:未删除 1:已删除')
    create_id = mapped_column(INTEGER, nullable=False, server_default=text("'0'"), comment='创建用户ID')
    create_ts = mapped_column(TimestampWithTimezone, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                              comment='创建时间戳')
    update_id = mapped_column(INTEGER, nullable=False, server_default=text("'0'"), comment='更新用户ID')
    update_ts = mapped_column(TimestampWithTimezone, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                              comment='更新时间戳')


t_k_pattern_and_group = Table(
    'k_pattern_and_group_mapping', CommonColumn.metadata,
    Column('k_pattern_id', INTEGER, ForeignKey('k_pattern.id'), nullable=False, comment='K线形态id'),
    Column('k_pattern_group_id', INTEGER, ForeignKey('k_pattern_group.id'), nullable=False, comment='K线形态组id'),
    comment='K线形态和形态组映射关系'
)


class KPattern(CommonColumn):
    __tablename__ = 'k_pattern'
    __table_args__ = {'comment': 'K线形态'}

    name = mapped_column(String(128, 'utf8mb4_bin'), nullable=False, comment='名')
    description = mapped_column(String(512, 'utf8mb4_bin'), comment='描述')
    imageUrl = mapped_column(String(255, 'utf8mb4_bin'), comment='图片URL')
    # groups = relationship("KPatternGroup", secondary=t_k_pattern_and_group, backref="k_patterns")
    # groups: Mapped[List["KPatternGroup"]] = relationship(secondary=t_k_pattern_and_group, backref='k_patterns')


class KPatternGroup(CommonColumn):
    __tablename__ = 'k_pattern_group'
    __table_args__ = {'comment': 'K线形态组'}

    name = mapped_column(String(128, 'utf8mb4_bin'), nullable=False, comment='形态组名')
    description = mapped_column(String(512, 'utf8mb4_bin'), comment='描述')
    # k_patterns = relationship("KPattern", secondary=t_k_pattern_and_group, backref="groups")
    k_patterns: Mapped[List["KPattern"]] = relationship(secondary=t_k_pattern_and_group, backref='groups')


class PatternRecognizeRecord(CommonColumn):
    __tablename__ = 'pattern_recognize_record'
    __table_args__ = (
        Index('unique_recognization_idx', 'patternId', 'symbol_type', 'symbol', 'kInterval', 'patternStart',
              'patternEnd', unique=True),
        {'comment': '形态识别记录'}
    )

    exchange = mapped_column(String(32, 'utf8mb4_bin'), nullable=False, comment='交易所：如 币安,BINANCE')
    symbol_type = mapped_column(String(16, 'utf8mb4_bin'), nullable=False, comment='市场类型:spot、futures')
    symbol = mapped_column(VARCHAR(128), nullable=False, comment='市场符号，如BTC/USDT')
    kInterval = mapped_column(VARCHAR(10), nullable=False, comment='K线Interval，如1d，4h')
    patternId = mapped_column(INTEGER, nullable=False, comment='匹配的形态id ')
    patternStart = mapped_column(TimestampWithTimezone, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                                 comment='形态匹配的起始K线开盘时间戳')
    patternEnd = mapped_column(TimestampWithTimezone, nullable=False, server_default=text('CURRENT_TIMESTAMP'),
                               comment='形态匹配的终止K线开盘时间戳')
    matchScore = mapped_column(Float, nullable=False, comment='匹配度 ')
    extra = mapped_column(JSON, comment='匹配形态结果的其他返回值')


class Dbbardata(Base):
    __tablename__ = 'dbbardata'
    __table_args__ = (
        Index('dbbardata_symbol_exchange_interval_datetime', 'symbol', 'exchange', 'interval', 'datetime', unique=True),
    )

    id = mapped_column(Integer, primary_key=True)
    symbol = mapped_column(String(255, 'utf8mb4_bin'), nullable=False)
    exchange = mapped_column(String(255, 'utf8mb4_bin'), nullable=False)
    datetime = mapped_column(DatetimeWithTimezone, nullable=False)
    interval = mapped_column(String(255, 'utf8mb4_bin'), nullable=False)
    volume = mapped_column(Float, nullable=False)
    turnover = mapped_column(Float, nullable=False)
    open_interest = mapped_column(Float, nullable=False)
    open_price = mapped_column(Float, nullable=False)
    high_price = mapped_column(Float, nullable=False)
    low_price = mapped_column(Float, nullable=False)
    close_price = mapped_column(Float, nullable=False)
    is_checked = mapped_column(TINYINT(1), server_default=text("'0'"), comment='是否已经检查过')


class Dbbaroverview(Base):
    __tablename__ = 'dbbaroverview'
    __table_args__ = (
        Index('dbbaroverview_symbol_exchange_interval', 'symbol', 'exchange', 'interval', unique=True),
    )

    id = mapped_column(Integer, primary_key=True)
    symbol = mapped_column(String(255, 'utf8mb4_bin'), nullable=False)
    exchange = mapped_column(String(255, 'utf8mb4_bin'), nullable=False)
    interval = mapped_column(String(255, 'utf8mb4_bin'), nullable=False)
    count = mapped_column(Integer, nullable=False)
    start = mapped_column(DatetimeWithTimezone, nullable=False)
    end = mapped_column(DatetimeWithTimezone, nullable=False)
