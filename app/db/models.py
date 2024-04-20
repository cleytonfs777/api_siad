from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserModel(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column('username', String, nullable=False)
    email = Column('email', String, nullable=False, unique=True)
    password = Column('password', String, nullable=False)


class ReseterNeed(Base):
    __tablename__ = 'reseter_need'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column('username', String, nullable=False, unique=True)
    email = Column('email', String, nullable=False, unique=True)


class Codes(Base):
    __tablename__ = 'codes'
    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column('email', String, nullable=False, unique=True)
    reset_code = Column('reset_code', String, nullable=False, unique=True)
    status = Column('status', String, nullable=False)
    expires_at = Column('expires_at', DateTime, nullable=False)