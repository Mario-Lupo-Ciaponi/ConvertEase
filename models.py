from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, DECIMAL
from sqlalchemy.orm import declarative_base

from datetime import datetime


connection_string = "postgresql+psycopg2://postgres:Ps1029384756,.@localhost/convert_ease_db"

engine = create_engine(connection_string)
Base = declarative_base()


class ConvertionHistory(Base):
    __tablename__ = "convertion_history"

    id = Column(
        Integer,
        primary_key=True,
    )
    from_currency = Column(
        String(3),
        nullable=False,
    )
    to_currency = Column(
        String(3),
        nullable=False,
    )
    amount = Column(
        DECIMAL(10, 2),
        nullable=False,
    )
    result = Column(
        Numeric(10, 2),
        nullable=False,
    )
    date_of_creation = Column(
        DateTime,
        default=datetime.now
    )

