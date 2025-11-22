from database import Base
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class Expense(Base):

    __tablename__ = "expenses"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=False), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=False), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User")


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=False), nullable=False, server_default=text("now()")
    )
