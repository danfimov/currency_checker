from abc import ABC, abstractmethod
from itertools import cycle

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from currency_checker.domain.exceptions import AccountsNotFound
from currency_checker.domain.models import Account
from currency_checker.infrastructure.postgres import Accounts
from currency_checker.infrastructure.settings import PostgresSettings


class AbstractAccountStorage(ABC):
    @abstractmethod
    async def cache_all_active_accounts(self, source: str) -> None:
        ...

    @abstractmethod
    def get_active_account(self, source: str) -> Account:
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

        self._active_accounts: dict[str, cycle[Account]] = {}

    async def cache_all_active_accounts(self, source: str) -> None:
        session: AsyncSession = self._sessionmaker()
        query = select(Accounts.token).where(Accounts.source == source, Accounts.active.is_(True))
        query_result = await session.execute(query)
        if query_result is None:
            raise AccountsNotFound
        self._active_accounts[source] = cycle([Account.from_orm(account) for account in query_result.fetchall()])

    def get_active_account(self, source: str) -> Account:
        return next(self._active_accounts.get(source))  # type: ignore
