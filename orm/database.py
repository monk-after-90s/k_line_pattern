from typing import Any
from sqlalchemy import Executable, Result, Select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.engine import URL
import config


class SoftLogicDelAsyncSession(AsyncSession):
    """如果有字段is_delete作为逻辑删除的标识，忽视被逻辑删除的条目的异步会话"""

    async def execute(
            self,
            statement: Executable,
            *args,
            **kw: Any,
    ) -> Result[Any]:
        if isinstance(statement, Select) and hasattr(statement.c, 'is_delete'):
            statement = statement.filter_by(is_delete=0)
        return await super().execute(statement, *args, **kw)


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
alrb_asess_fctry = async_sessionmaker(alpha_rabit_engine1, expire_on_commit=False, class_=SoftLogicDelAsyncSession)

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
bar_asess_fctry = async_sessionmaker(bar_engine, expire_on_commit=False, class_=SoftLogicDelAsyncSession)
