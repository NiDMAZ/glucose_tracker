import pytz
import models

import datetime
from fastapi import FastAPI, Depends, BackgroundTasks, Request, status
from fastapi.responses import JSONResponse
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


@app.get("/", status_code=status.HTTP_200_OK)
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

        i.date = i.date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York')).strftime("%Y-%m-%d")
        format_entries.append(i)
        

    return templates.TemplateResponse("home.html", {
        "request": request, 
        "glucose_entries": format_entries,
        "meals": meals.all(),
        "users": users.all(),
        "meal_id": meal_id,
        "amount": amount
    })


@app.get("/meal", status_code=status.HTTP_200_OK)
def meal(request: Request, db: Session = Depends(get_db)):
    meals = db.query(Meal).order_by(Meal.name)

    return templates.TemplateResponse("meals.html", {
        "request": request, 
        "meals": meals.all()
    })

@app.get("/api/glucose")
async def get_all_glucose_entry(request: Request, db: Session = Depends(get_db)):
    entries = db.query(GlucoseLevel)

    return entries.all()


@app.post("/api/glucose", status_code=status.HTTP_201_CREATED)
async def add_glucose_entry(glucose_entry: GlucoseEntry, db: Session = Depends(get_db)):
    try:
        glucose = GlucoseLevel()
        glucose.user_id = glucose_entry.user_id
        glucose.date = glucose_entry.date
        glucose.amount = glucose_entry.amount
        glucose.unit = glucose_entry.unit
        glucose.note = glucose_entry.note
        glucose.meal_id = glucose_entry.meal_id

        db.add(glucose)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content={
                'id': glucose.id, 
                'user_id': glucose.user_id,
                'meal_id' 
                'amount': glucose.amount,
                'message': 'success'})

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={
                'message': f'Error: {e}'})

@app.get("/api/glucose/{id}")
async def get_single_glucose(id: int, db: Session = Depends(get_db)):
    entry = db.query(GlucoseLevel).filter(GlucoseLevel.id == id).first()

    return entry

@app.delete("/api/glucose/{id}", status_code=status.HTTP_200_OK)
async def delete_glucose_entry(id: int, db: Session = Depends(get_db)):
    entry = db.query(GlucoseLevel).filter(GlucoseLevel.id == id).first()
    
    try:
        if entry:
            entry_time = entry.date
            entry_amount = entry.amount
            meal_name = entry.meal_id
            db.delete(entry)
            db.commit()

            status_code = status.HTTP_200_OK
            content = {'id': id, 'message': f'success: deleted {id}'}
        else:
            status_code = status.HTTP_404_NOT_FOUND
            content = {'id': id, 'message': f'error: not found in database {id}'}
    except Exception as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        content = {'message': f'Error: {e}'}
    finally:
        return JSONResponse(status_code=status_code, content=content)
        

@app.get("/api/meal", status_code=status.HTTP_200_OK)
async def get_meals(request: Request, db: Session = Depends(get_db)):
    entries = db.query(Meal)

    return entries.all()

@app.post("/api/meal", status_code=status.HTTP_201_CREATED)
async def add_meal(meal: MealEntry, db: Session = Depends(get_db)):

    meal_ = Meal()
    meal_.name = meal.name

    db.add(meal_)
    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={'id': meal_.id, 'name': meal_.name})

@app.get("/api/meal/{id}")
async def get_single_meal(id: int, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()

    return entry

@app.put("/api/meal/{id}", status_code=status.HTTP_200_OK)
async def add_meal(meal: MealEntry, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()

    meal_ = Meal()
    meal_.name = meal.name

    db.add(meal_)
    db.commit()
	
    return {
	"code": "success",
	"message": "Entry was added successfully"

   }

@app.delete("/api/meal/{id}", status_code=status.HTTP_200_OK)
async def remove_meal(id: int, db: Session = Depends(get_db)):
    entry = db.query(Meal).filter(Meal.id == id).first()
    if entry:
        meal_name = entry.name
        db.delete(entry)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                'message': 'Created successfully', 
                'id': id, 
                'name': meal_name})
        
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={
                'id': id, 
                'message': 'Error: ID not found in database.'
                })


@app.get("/api/user")
async def get_user(request: Request, db: Session = Depends(get_db)):
    entries = db.query(User)

    return entries.all()

@app.post("/api/user", status_code=status.HTTP_201_CREATED)
async def add_user(user: UserModel, db: Session = Depends(get_db)):

    # Normalizing the names
    first_name = user.first_name.lower()
    last_name = user.last_name.lower()

    entry = db.query(User).filter(User.first_name == first_name, User.last_name == last_name).first()
    if entry:
        status_code = status.HTTP_409_CONFLICT
        content = {'message': f"Error: User {first_name} {last_name} already exists in database", 'id': entry.id}
    else:
        user_ = User()
        user_.first_name = user.first_name.lower()
        user_.last_name = user.last_name.lower()
        user_.email = user.email.lower()
        db.add(user_)
        db.commit()

        status_code = status.HTTP_201_CREATED 
        content = {'id': user_.id, 'message': f"Success: User {first_name} {last_name} added"}

    return JSONResponse(status_code=status_code, content=content)
	
@app.delete("/api/user/{id}", status_code=status.HTTP_200_OK)
async def remove_user(id: int, db: Session = Depends(get_db)):
    entry = db.query(User).filter(User.id == id).first()
    if entry:
        first_name = entry.first_name
        last_name = entry.last_name
        db.delete(entry)
        db.commit()

        status_code = status.HTTP_200_OK
        content = {'id': id, 'message': f"Success: User {first_name} {last_name} deleted"}
    else:
        status_code = status.HTTP_404_NOT_FOUND
        content = {'id': id, 'message': f"Error: User ID={id} not found in database."}
        
    return JSONResponse(status_code=status_code, content=content)