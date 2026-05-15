from datetime import datetime
from sqlalchemy.orm import Mapped
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.testing.schema import mapped_column
from src.base_service import Base


class UserSharesModel(Base):
    __tablename__ = 'users_shares'

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String(), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(), nullable=False)
    shares_broker: Mapped[str] = mapped_column(sa.String(), nullable=False)
    broker_commission: Mapped[float] = mapped_column(sa.Float(), nullable=False)


class UserSharesMessages(Base):
    __tablename__ = 'user_shares_messages'

    message_id: Mapped[UUID] = mapped_column(primary_key=True)
    processed_time: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now())