import pytz
import models

import datetime
from fastapi import FastAPI, Depends, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from database import SessionLocal, engine
from models import GlucoseLevel, Meal, User
from schema import GlucoseEntry, SingleGlucoseEntry, MealEntry, UserModel

from sqlalchemy.orm import Session


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, amount: str = 0, meal_id: str = None, db: Session = Depends(get_db)):
    entries = db.query(GlucoseLevel).order_by(GlucoseLevel.date.desc())
    meals = db.query(Meal)
    users = db.query(User)

    if amount:
        entries = entries.filter(GlucoseLevel.amount >= amount)

    if meal_id:
        entries = entries.filter(GlucoseLevel.meal_id == meal_id)

    format_entries = []

    for i in entries.all():

        date = i.date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York')).strftime("%Y-%m-%d")
        # date = date.replace(tzinfo=pytz.utc)
        # date = date.astimezone(pytz.timezone('America/New_York'))
        i.date = date
        format_entries.append(i)
        

    return templates.TemplateResponse("home.html", {
        "request": request, 
        "glucose_entries": format_entries,
        "meals": meals.all(),
        "users": users.all(),
        "meal_id": meal_id,
        "amount": amount
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

@app.delete("/api/glucose/{id}")
async def delete_glucose_entry(id: str, db: Session = Depends(get_db)):
    entry = db.query(GlucoseLevel).filter(GlucoseLevel.id == id).first()
    entry_time = entry.date
    entry_amount = entry.amount
    meal_name = entry.meal_id
    db.delete(entry)
    db.commit()

    return {
        "code": "success",
        "message": f"Deleted ID= {id} MealName={meal_name} Amount={entry_amount} EntryTime={entry_time}"
    }


@app.get("/api/glucose")
async def get_all_glucose_entry(request: Request, db: Session = Depends(get_db)):
    entries = db.query(GlucoseLevel)

    return entries.all()


@app.post("/api/glucose")
async def add_glucose_entry(glucose_entry: GlucoseEntry, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    glucose = GlucoseLevel()
    glucose.user_id = glucose_entry.user_id
    glucose.date = glucose_entry.date
    glucose.amount = glucose_entry.amount
    glucose.unit = glucose_entry.unit
    glucose.note = glucose_entry.note
    glucose.meal_id = glucose_entry.meal_id

    db.add(glucose)
    db.commit()
	
    return {
	"code": "success",
	"message": "Entry was added successfully",
    "id": glucose.id

   }

@app.get("/api/meal")
async def get_meals(request: Request, db: Session = Depends(get_db)):
    entries = db.query(Meal)

    return entries.all()

@app.get("/api/meal/{id}")
async def get_single_meal(id: str, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()

    return entry

@app.delete("/api/meal/{id}")
async def remove_meal(id: str, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()
    meal_name = entry.name
    db.delete(entry)
    db.commit()

    return {
        "code": "success",
        "message": f"Deleted ID= {id} Name={meal_name}"
    }


@app.post("/api/meal")
async def add_meal(meal: MealEntry, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    meal_ = Meal()
    meal_.name = meal.name

    db.add(meal_)
    db.commit()
	
    return {
	"code": "success",
	"message": "Entry was added successfully",
    "id": meal_.id
   }

@app.put("/api/meal{id}")
async def add_meal(meal: MealEntry, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()

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
	"message": "Entry was added successfully",
    "id": user_.id

   }

@app.delete("/api/user/{id}")
async def remove_user(id: str, db: Session = Depends(get_db)):
    entry = db.query(User).filter(User.id == id).first()
    db.delete(entry)
    db.commit()

    return {
        "code": "success",
        "message": f"Deleted ID= {id}"
    }
