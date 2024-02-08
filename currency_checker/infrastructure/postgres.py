from sqlalchemy import Column, MetaData, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


convention = {
    "all_column_names": lambda constraint, table: "_".join([column.name for column in constraint.columns.values()]),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": ("fk__%(table_name)s__%(all_column_names)s__" "%(referred_table_name)s"),
    "pk": "pk__%(table_name)s",
}

metadata = MetaData(naming_convention=convention)  # type: ignore
Base = declarative_base(metadata=metadata)


class UIdMixin:
    """
    Mixin with different approach of uuid generator.
    This generator is better generator, because it's built-in since Postgres 13 without any 'uuid-ossp' extensions
    """
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        doc='Unique index of element (type UUID)'
    )


class Accounts(Base, UIdMixin):
    __tablename__ = 'accounts'

    token = Column(String(256))
    source = Column(
        String(50),
        doc='Account source (like binance or coingecko)'
    )
