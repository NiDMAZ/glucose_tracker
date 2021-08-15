import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base

class GlucoseLevel(Base):
    __tablename__ = "glucose"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    value = Column(Integer)
    unit = Column(String, default='mg/dL')
    meal = Column(String, default='')
    note = Column(String, default='')
    modified = Column(DateTime, default=datetime.datetime.utcnow)


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, default='')