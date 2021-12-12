from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from database.database import db
from app.internal.tasks.document_analysis import create_annotation_graph, create_context_graph, get_download_link
from app.internal.internal_datamodels import Document
from typing import List
templates = Jinja2Templates(directory="static/templates")
analysis_templates = Jinja2Templates(directory="static/templates/analysis")
router = APIRouter(
    prefix="/analysis",
    responses={404: {"description": "Not found"}},
)


@router.get("/start_page", response_class=HTMLResponse)
async def read_item(request: Request):
    extracted_files = db.get_all_index_data('extract')
    annotated_files = db.get_all_index_data('annotate')
    analysed_files = db.get_all_index_data('analyse')
    res = []
    for file in extracted_files:
        state = 'extracted'
        if file in annotated_files:
            state = 'annotated'
            if file in analysed_files:
                state = 'analysed'
        res.append({file: state})
    return analysis_templates.TemplateResponse("start_analysis.html",
                                               {"request": request,
                                                "status": res}
                                               )


@router.get("/annotation_graph", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('annotate', id)
    doc = Document(**file)

    graph = create_annotation_graph(doc)
    return analysis_templates.TemplateResponse("annotation_graph.html",
                                      {"request": request, "id": id, "graph": str(graph), "active": True})


@router.get("/context_graph", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('analyse', id)
    doc = Document(**file)

    graph = create_context_graph(doc)
    return analysis_templates.TemplateResponse("context_graph.html",
                                      {"request": request, "id": id, "graph": graph, "active": True})


@router.get("/download_data", response_class=FileResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('analyse', id)
    doc = Document(**file)
    path = get_download_link(doc)
    return path
