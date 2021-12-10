from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import db

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/edit",
    responses={404: {"description": "Not found"}},
)


@router.get("/get_questiontemplates", response_class=HTMLResponse)
async def read_item(request: Request):
    #todo: Implement this function
    return 

@router.post("/edit_questiontemplate", response_class=HTMLResponse)
async def read_item(request: Request):
    #todo: Implement this function
    return

@router.put("create_questiontemplate_list")
async def read_item(request: Request):
    #todo: Implement this function
    return

@router.delete("delete_questiontemplate")
async def read_item(request: Request):
    #todo: Implement this function
    return
