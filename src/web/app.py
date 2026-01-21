from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="GuildGreeter Dashboard")

# Templates et fichiers statiques
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Import des routes
from .routes import router
app.include_router(router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})