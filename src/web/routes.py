from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import httpx  # Remplace requests pour async

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

@router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/guild/{guild_id}")
async def guild_page(request: Request, guild_id: int):
    # Exemple d'appel HTTP async
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/guilds/{guild_id}")
        data = response.json()
    
    return templates.TemplateResponse("guild.html", {
        "request": request,
        "guild": data
    })

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})