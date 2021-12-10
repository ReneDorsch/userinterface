from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import db
from app.internal.tasks.document_analysis import create_annotation_graph, create_context_graph
from app.internal.internal_datamodels import Document
templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/analysis",
    responses={404: {"description": "Not found"}},
)

@router.get("/annotation_graph", response_class=HTMLResponse)
async def read_item(request: Request):
    id = "a54cf1b8-dc12-44f0-a5f3-c6de60033e31"

    file = db.get_file('annotate', id)
    doc = Document(**file)

    graph = create_annotation_graph(doc)
    return templates.TemplateResponse("annotation_graph.html", {"request": request, "id": id, "graph": str(graph), "active": True})

@router.get("/context_graph", response_class=HTMLResponse)
async def read_item(request: Request):
    id = "a54cf1b8-dc12-44f0-a5f3-c6de60033e31"

    file = db.get_file('analyse', id)
    doc = Document(**file)

    graph = create_context_graph(doc)
    return templates.TemplateResponse("context_graph.html", {"request": request, "id": id, "graph": graph, "active": True})
