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

from typing import List

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/enrichment",
    responses={404: {"description": "Not found"}},
)




@router.get("/upload_files", response_class=HTMLResponse)
async def read_item(request: Request):

    return templates.TemplateResponse("file_upload.html",
                                      {"request": request, "id": id, "active": True, "step": 0})



@router.get("/options", response_class=HTMLResponse)
async def read_item(request: Request):
    docs: List[Document] = [Document(**_) for _ in db.get_all_files('upload')]
    return templates.TemplateResponse("options.html",
                                      {"request": request, "id": id, "active": True, "step": 1,
                                       "documents": docs})


@router.post("/options_result")
def option_result_interpretation(request: Request, option_selection: OptionSelection, background_tasks: BackgroundTasks):
    if option_selection.mode == 'fast':
        # Add an background task that checks every second if the task was already executed.
        background_tasks.add_task(enrichment.execute_enrichment_tasks, id=option_selection.id)
        return {'url': f"../analysis/start/f{option_selection.id}"}
    else:
        background_tasks.add_task(enrichment.start_extraction, id=option_selection.id)
        return {'url': f"./edit_document/f{option_selection.id}"}




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

    return {'result': 200}



@router.get("/edit_document", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("edit_document.html",
                                       {"request": request, "id": id, "active": True, "step": 2})


@router.get("/edit_text", response_class=HTMLResponse)
async def read_item(request: Request):
    id = "9b0594fb-c54e-444f-b032-1ffa7b017ad2"

    file = db.get_file('extract', id)
    doc = Document(**file)
    path = doc.get_path_to_file()
    return templates.TemplateResponse("edit_text.html",
                                      {"request": request, "id": id, "title": "Item", "active": True, "pdf_file": path,
                                       "text": doc.get_fulltext(), "step": 2})


@router.get("/edit_images", response_class=HTMLResponse)
async def read_item(request: Request):
    id = "9b0594fb-c54e-444f-b032-1ffa7b017ad2"
    i = 1
    file = db.get_file('extract', id)
    doc = Document(**file)
    image = doc.get_image(i)
    image_base_64 = image.get_path_to_file()

    table_html = """
                    <table>
                        <tr>
                            <th>Company</th>
                            <th>Contact</th>
                            <th>Country</th>
                        </tr>
                        <tr>
                            <td>Alfreds Futterkiste</td>
                            <td>Maria Anders</td>
                            <td>Germany</td>
                        </tr>
                        <tr>
                            <td>Centro comercial Moctezuma</td>
                            <td>Francisco Chang</td>
                            <td>Mexico</td>
                        </tr>
                    </table>  
                """
    return templates.TemplateResponse("edit_images.html",
                                      {"request": request, "id": id, "title": "Item", "active": True,
                                       "image_base_64": image_base_64, "table_html": table_html, "step": 2})


@router.get("/edit_tables", response_class=HTMLResponse)
async def read_item(request: Request):
    id = "9b0594fb-c54e-444f-b032-1ffa7b017ad2"
    i = 1
    file = db.get_file('extract', id)
    doc = Document(**file)
    image = doc.get_table(i)
    image_base_64 = image.get_path_to_file()

    table_html = """
                    <table>
                        <tr>
                            <th>Company</th>
                            <th>Contact</th>
                            <th>Country</th>
                        </tr>
                        <tr>
                            <td>Alfreds Futterkiste</td>
                            <td>Maria Anders</td>
                            <td>Germany</td>
                        </tr>
                        <tr>
                            <td>Centro comercial Moctezuma</td>
                            <td>Francisco Chang</td>
                            <td>Mexico</td>
                        </tr>
                    </table>  
                """
    return templates.TemplateResponse("edit_table.html", {"request": request, "id": id, "title": "Item", "active": True,
                                                          "image_base_64": image_base_64, "table_html": table_html, "step": 2})


@router.get("/edit_annotations", response_class=HTMLResponse)
async def read_item(request: Request):
    table_html = """
                    <table>
                        <tr>
                            <th>Company</th>
                            <th>Contact</th>
                            <th>Country</th>
                        </tr>
                        <tr>
                            <td>Alfreds Futterkiste</td>
                            <td>Maria Anders</td>
                            <td>Germany</td>
                        </tr>
                        <tr>
                            <td>Centro comercial Moctezuma</td>
                            <td>Francisco Chang</td>
                            <td>Mexico</td>
                        </tr>
                    </table>  
                """
    return templates.TemplateResponse("edit_annotations.html",
                                       {"request": request, "id": id, "active": True, "step": 3,
                                       "table_html": table_html})
