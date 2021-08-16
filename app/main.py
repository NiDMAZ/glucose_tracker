import pytz
import models

import datetime
from fastapi import FastAPI, Depends, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from database import SessionLocal, engine
from models import GlucoseLevel, Meal, User

from sqlalchemy.orm import Session


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


class GlucoseEntry(BaseModel):
    user: str
    time: datetime.datetime
    value: int
    unit: str = 'mg/dL'
    note: str = ''
    meal: str = ''


class SingleGlucoseEntry(BaseModel):
    id: int


class MealEntry(BaseModel):
    name: str = ''

class UserModel(BaseModel):
    first_name: str
    last_name: str
    email: str = ''


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, value: str = 0, meal: str = None, db: Session = Depends(get_db)):
    entries = db.query(GlucoseLevel).order_by(GlucoseLevel.time.desc())
    meals = db.query(Meal)
    users = db.query(User)

    if value:
        entries = entries.filter(GlucoseLevel.value >= value)

    if meal:
        entries = entries.filter(GlucoseLevel.meal == meal)

    format_entries = []

    for i in entries.all():
        i.user = i.user.title()

        time = i.time
        time = time.replace(tzinfo=pytz.utc)
        time = time.astimezone(pytz.timezone('America/New_York'))
        i.time = time.strftime("%a %b %d %Y, %I:%M %p")
        format_entries.append(i)
        

    return templates.TemplateResponse("home.html", {
        "request": request, 
        "glucose_entries": format_entries,
        "meals": meals.all(),
        "users": users.all(),
        "meal": meal,
        "value": value
    })


@app.get("/meal")
def meal(request: Request, db: Session = Depends(get_db)):
    meals = db.query(Meal).order_by(Meal.name)

    return templates.TemplateResponse("meals.html", {
        "request": request, 
        "meals": meals.all()
    })


@app.get("/api/glucose/{id}")
async def get_single_glucose(id: str, db: Session = Depends(get_db)):
    entry = db.query(GlucoseLevel).filter(GlucoseLevel.id == id).first()

    return entry

@app.get("/api/glucose")
async def get_all_glucose_entry(request: Request, db: Session = Depends(get_db)):
    entries = db.query(GlucoseLevel)

    return entries.all()


@app.post("/api/glucose")
async def add_glucose_entry(glucose_entry: GlucoseEntry, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    glucose = GlucoseLevel()
    glucose.user = glucose_entry.user.lower()
    glucose.time = glucose_entry.time
    glucose.value = glucose_entry.value
    glucose.unit = glucose_entry.unit
    glucose.note = glucose_entry.note
    glucose.meal = glucose_entry.meal

    db.add(glucose)
    db.commit()
	
    return {
	"code": "success",
	"message": "Entry was added successfully"

   }

@app.get("/api/meal")
async def get_meals(request: Request, db: Session = Depends(get_db)):
    entries = db.query(Meal)

    return entries.all()

@app.get("/api/meal/{id}")
async def get_single_meal(id: str, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()

    return entry

@app.post("/api/meal")
async def add_meal(meal: MealEntry, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    meal_ = Meal()
    meal_.name = meal.name

    db.add(meal_)
    db.commit()
	
    return {
	"code": "success",
	"message": "Entry was added successfully"

   }

@app.get("/api/user")
async def get_user(request: Request, db: Session = Depends(get_db)):
    entries = db.query(User)

    return entries.all()

@app.get("/api/user/{id}")
async def get_single_user(id: str, db: Session = Depends(get_db)):
    entry = db.query(User).filter(User.id == id).first()

    return entry

@app.post("/api/user")
async def add_user(user: UserModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    user_ = User()
    user_.first_name = user.first_name.lower()
    user_.last_name = user.last_name.lower()
    user_.email = user.email.lower()


    db.add(user_)
    db.commit()
	
    return {
	"code": "success",
	"message": "Entry was added successfully"

   }