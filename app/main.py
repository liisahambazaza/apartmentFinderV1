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


@app.post("/api/recommend")
async def recommend(payload: dict):
    max_rent = payload.get("max_rent") if isinstance(payload, dict) else None
    top_n = int(payload.get("top_n", 5)) if isinstance(payload, dict) else 5
    
    # Convert max_rent to float if provided
    if max_rent is not None:
        try:
            max_rent = float(max_rent)
        except (ValueError, TypeError):
            max_rent = None
    
    recs = data_module.get_recommendations(preferences=None, top_n=top_n, max_rent=max_rent)
    return JSONResponse(content={"recommendations": recs})
