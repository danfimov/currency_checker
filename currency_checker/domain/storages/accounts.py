from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from currency_checker.domain.exceptions import AccountsNotFound
from currency_checker.domain.models import Account
from currency_checker.infrastructure.postgres import Accounts
from currency_checker.infrastructure.settings import PostgresSettings


class AbstractAccountStorage(ABC):
    @abstractmethod
    async def get_active_account(self, source: str) -> Account:
        ...


class PostgresAccountStorage(AbstractAccountStorage):
    def __init__(self, postgres_settings: PostgresSettings) -> None:
        dsn = f'postgresql+asyncpg://{postgres_settings.user}:{postgres_settings.password}@{postgres_settings.host}:{postgres_settings.port}/{postgres_settings.database}'
        print('DSN: ', dsn)
        self._engine: AsyncEngine = create_async_engine(
            dsn,
            echo=False,
            connect_args={
                'ssl': postgres_settings.ssl_mode,
                'statement_cache_size': 0,
            }
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def get_active_account(self, source: str) -> Account:
        session: AsyncSession = self._sessionmaker()
        query = select(Accounts.token).where(Accounts.source == source).limit(1)
        query_result = await session.execute(query)
        if query_result is None:
            raise AccountsNotFound
        return Account.from_orm(query_result.fetchone())
