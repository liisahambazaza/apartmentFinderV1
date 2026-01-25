from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

from . import data as data_module

app = FastAPI(title="NYC Apartment Recommender")

templates = Jinja2Templates(directory="templates")

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    # static directory may not exist in the starter scaffold
    pass

 
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Adding budget-based recommendations back to the website
@app.get("/api/recommend")
async def recommend(max_rent: int = 3000, top_n: int = 5, restaurant_importance: int = 0):
    recommendations = data_module.get_recommendations(max_rent=max_rent, top_n=top_n, restaurant_importance=restaurant_importance)
    return {"recommendations": recommendations}
