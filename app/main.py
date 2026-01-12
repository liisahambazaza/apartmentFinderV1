from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
    prefs = payload.get("preferences", {}) if isinstance(payload, dict) else {}
    top_n = int(payload.get("top_n", 5)) if isinstance(payload, dict) else 5
    recs = data_module.get_recommendations(prefs, top_n=top_n)
    return JSONResponse(content={"recommendations": recs})
