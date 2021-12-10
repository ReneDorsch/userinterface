from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import db

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/advanced",
    responses={404: {"description": "Not found"}},
)

@router.get("/questiontemplate", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("questiontemplate.html", {"request": request, "id": id, "title": "Item", "active": True})

@router.get("/question_answering_model", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("edit_question_answering_models.html", {"request": request, "id": id, "title": "Item", "active": True})

@router.get("/named_entity_model", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("edit_named_entity_model.html", {"request": request, "id": id, "title": "Item", "active": True})
