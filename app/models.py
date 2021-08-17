import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, onupdate=func.now())



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, default='')
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, onupdate=func.now())



class GlucoseLevel(Base):
    __tablename__ = "glucose"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_id = Column(Integer, ForeignKey("meals.id"))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    amount = Column(Integer)
    unit = Column(String, default='mg/dL')
    note = Column(String, default='')
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, onupdate=func.now())

    user = relationship("User")
    meal = relationship("Meal")


