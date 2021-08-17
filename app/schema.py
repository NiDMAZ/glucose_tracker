import datetime
from pydantic import BaseModel


class GlucoseEntry(BaseModel):

    user_id: int
    meal_id: int
    date: datetime.datetime
    amount: int
    unit: str = 'mg/dL'
    note: str = ''


class SingleGlucoseEntry(BaseModel):
    id: int


class MealEntry(BaseModel):
    name: str = ''


class UserModel(BaseModel):
    first_name: str
    last_name: str
    email: str = ''
