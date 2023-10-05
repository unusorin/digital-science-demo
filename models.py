import sqlalchemy
from sqlalchemy import String, DateTime
from database import database_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime
from typing import Optional


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_date: Mapped[datetime.datetime] = mapped_column(DateTime(), server_default=sqlalchemy.func.now())
    last_login_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(), nullable=True)


Base.metadata.create_all(database_engine)
