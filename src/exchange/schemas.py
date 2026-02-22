from sqlalchemy.orm import declarative_base, Mapped
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.testing.schema import mapped_column


Base = declarative_base()

class ExchangeModel(Base):
    __tablename__ = 'exchange'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    exchange_name: Mapped[str] = mapped_column(sa.String())
    work_in_russia: Mapped[bool] = mapped_column(sa.Boolean())
    volume: Mapped[int] = mapped_column(sa.BigInteger())
    owner_first_name: Mapped[str] = mapped_column(sa.String())
    owner_last_name: Mapped[str] = mapped_column(sa.String())

    btc_price: Mapped[None | float] = mapped_column(sa.Float)
    eth_price: Mapped[None | float] = mapped_column(sa.Float)
    sol_price: Mapped[None | float] = mapped_column(sa.Float)