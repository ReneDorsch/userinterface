from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import db

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/document_annotation",
    responses={404: {"description": "Not found"}},
)

@router.post("/recieves_data")
def recieves_data():
    print("ok")

@router.get("/send_data")
def send_data():
    print("ok")