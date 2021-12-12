import base64
import os.path
from uuid import uuid4

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import db
from app.internal.internal_datamodels import Document, OptionSelection
import starlette.datastructures as star_data
from app.config import DATABASE_PATHS
from app.internal.tasks import document_enrichment as enrichment
from pydantic import BaseModel

from typing import List

enrichment_templates = Jinja2Templates(directory="static/templates/enrichment")
templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/enrichment",
    responses={404: {"description": "Not found"}},
)


class Task(BaseModel):
    document_id: str

@router.get("/start_page", response_class=HTMLResponse)
async def read_item(request: Request):
    """ Loads the Upload Page. """
    return enrichment_templates.TemplateResponse("start_page.html",
                                      {"request": request,
                                       "id": id,
                                       "active": True,
                                       "step": 0})


@router.get("/upload_files", response_class=HTMLResponse)
async def read_item(request: Request):
    """ Loads the Upload Page. """
    return enrichment_templates.TemplateResponse("file_upload.html",
                                      {"request": request,
                                       "id": id,
                                       "active": True,
                                       "step": 0})



@router.get("/options", response_class=HTMLResponse)
async def read_item(request: Request):
    """ Loads the Option Page that lists all avaible options for the enrichment process. """
    docs: List[Document] = [Document(**_) for _ in db.get_all_files('upload', False)]
    return enrichment_templates.TemplateResponse("options.html",
                                      {"request": request,
                                       "id": id,
                                       "active": True,
                                       "step": 1,
                                       "documents": docs})

@router.post("/upload_file", )
async def upload_file(request: Request):
    ''' Uploads a document file to the server. '''
    form = await request.form()
    for item in form.multi_items():

        upload_file = item[1]
        is_uploadfile: bool = isinstance(upload_file, star_data.UploadFile)
        is_pdf: bool = upload_file.content_type == 'application/pdf'

        if is_uploadfile and is_pdf:
            id = str(uuid4())
            file = await upload_file.read()

            doc = Document(**{
                "file_name": upload_file.filename,
                "base64_file": base64.urlsafe_b64encode(file).decode('utf-8'),
                "id": id,
                "file_path": os.path.join(DATABASE_PATHS['upload'], f"{id}.json")
            })
            db.add_file(doc, 'upload')
        else:
            return {'result': 500}

    return {'document_id': id}


@router.post("/options_result")
def option_result_interpretation(request: Request, option_selection: OptionSelection, background_tasks: BackgroundTasks):
    if option_selection.mode == 'fast':
        # Add a background task that checks every second if the task was already executed.
        background_tasks.add_task(enrichment.execute_enrichment_tasks, id=option_selection.id)
        return {'url': f"../edit/start_page"}
    else:
        background_tasks.add_task(enrichment.start_extraction, id=option_selection.id)
        return {'url': f"../edit/start_page"}


@router.post("/extraction_task")
def option_result_interpretation(request: Request, task: Task, background_tasks: BackgroundTasks):
    """ Adds a background task that calls the extraction process. """
    document_id = task.document_id.rstrip().lstrip()
    background_tasks.add_task(enrichment.start_extraction, id=document_id)
    return {'url': f"../edit/start_page"}

@router.post("/annotation_task")
def option_result_interpretation(request: Request, task: Task,  background_tasks: BackgroundTasks):
    """ Adds a background task that calls the annotation process. """
    document_id = task.document_id.rstrip().lstrip()
    background_tasks.add_task(enrichment.start_annotation, id=document_id)
    return {'url': f"../edit/start_page"}


@router.post("/analysis_task")
def option_result_interpretation(request: Request, task: Task,  background_tasks: BackgroundTasks):
    """ Adds a background task that calls the annotation process. """
    document_id = task.document_id.rstrip().lstrip()
    background_tasks.add_task(enrichment.start_analysis, id=document_id)
    return {'url': f"../analysis/start_page"}







