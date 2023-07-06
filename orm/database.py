import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.engine import URL
import config

# alpha_rabit数据库 创建异步SQLAlchemy引擎
alpha_rabit_engine1: AsyncEngine = create_async_engine(
    URL.create("mysql+aiomysql",
               config.DB_USER,
               config.DB_PASSWD,
               config.DB_HOST,
               config.DB_PORT,
               config.DB),
    echo=True)
# alpha_rabit数据库的会话工厂
alrb_asess_fctry = async_sessionmaker(alpha_rabit_engine1, expire_on_commit=False)

# 查询K线的数据库 创建异步SQLAlchemy引擎
bar_engine: AsyncEngine = create_async_engine(
    URL.create("mysql+aiomysql",
               config.DB_USER1,
               config.DB_PASSWD1,
               config.DB_HOST1,
               config.DB_PORT1,
               config.DB1),
    echo=True)
# 查询K线的数据库的会话工厂
bar_asess_fctry = async_sessionmaker(bar_engine, expire_on_commit=False)
