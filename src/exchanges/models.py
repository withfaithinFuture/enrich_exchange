from sqlalchemy.orm import declarative_base, Mapped
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.testing.schema import mapped_column
from src.db.base_service import Base


class ExchangeModel(Base):
    __tablename__ = 'exchanges'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    exchange_name: Mapped[str] = mapped_column(sa.String())
    trust_score: Mapped[int] = mapped_column(sa.Integer())


    btc_price: Mapped[float] = mapped_column(sa.Float)
    eth_price: Mapped[float] = mapped_column(sa.Float)
    sol_price: Mapped[float] = mapped_column(sa.Float)