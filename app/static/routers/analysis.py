from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from database.database import db
from app.internal.tasks.document_analysis import create_annotation_graph, create_context_graph, get_download_link
from app.internal.internal_datamodels import Document
from typing import List

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/analysis",
    responses={404: {"description": "Not found"}},
)


@router.get("/start_analysis", response_class=HTMLResponse)
async def read_item(request: Request):
    docs: List[Document] = [Document(**_) for _ in db.get_all_files('analyse', cached=False)]
    return templates.TemplateResponse("analysis.html", {"request": request, "id": id, "documents": docs})


@router.get("/annotation_graph", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('annotate', id)
    doc = Document(**file)

    graph = create_annotation_graph(doc)
    return templates.TemplateResponse("annotation_graph.html",
                                      {"request": request, "id": id, "graph": str(graph), "active": True})


@router.get("/context_graph", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('analyse', id)
    doc = Document(**file)

    graph = create_context_graph(doc)
    return templates.TemplateResponse("context_graph.html",
                                      {"request": request, "id": id, "graph": graph, "active": True})


@router.get("/download_data", response_class=FileResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('analyse', id)
    doc = Document(**file)
    path = get_download_link(doc)
    return path
