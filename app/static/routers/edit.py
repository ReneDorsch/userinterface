from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database.database import db
from app.internal.internal_datamodels import Document, OptionSelection, KnowledgeObject
from pydantic import BaseModel, Field
from typing import Dict, List
from fastapi.encoders import jsonable_encoder

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/edit",
    responses={404: {"description": "Not found"}},
)

class Item(BaseModel):
    document_id: str
    type: str
    num: str = Field(default='')
    data: Dict

class AnnotationItem(BaseModel):
    document_id: str
    data: Dict

def kObjs_as_html(kObjs: List[KnowledgeObject]) -> str:
    res = """<thead>
                <th> ID </th>
                <th> Category </th>
                <th> Labels </th>
            </thead> \n"""
    for kObj in kObjs:
        res += f"""<tr>
                        <td>{kObj.id} </td>
                        <td>{kObj.category} </td>
                        <td>{", ".join(kObj.labels)} </td>
                    </tr>\n
        """
    return res

def table_as_html(table) -> str:

    def get_row(cell, type, editable: bool = True):
        return f"<{type} {'contenteditable'if editable else ''}> {cell} </{type}>\n"
    res = f"""<thead> 
               {"".join([get_row(_.text, "th") for _ in table.table_header.cells])}
            </thead> \n"""
    for row in table.rows:
        res += "<tr>"
        res += "".join([get_row(_.text, "td") for _ in row.cells])
        res += "</tr>"
    return res




@router.put("/annotation/annotation_merge")
async def merge_annotations(document_id: str, data: AnnotationItem, background_tasks: BackgroundTasks):
    file = db.get_file('annotate', document_id, False)
    if file is not None:
        doc = Document(**file)
        doc.merge_kObjs(data.data)

    background_tasks.add_task(update_file, doc)
    file = db.get_file('annotate', document_id, False)
    doc = Document(**file)
    kObjs = doc.get_knowledgeObjects()

    return {"template": kObjs_as_html(kObjs)}



@router.put("/annotation/annotation_remove")
async def remove_annotations(document_id: str, data: AnnotationItem, background_tasks: BackgroundTasks):
    file = db.get_file('annotate', document_id, False)
    if file is not None:
        doc = Document(**file)
        doc.remove_KObjs(data.data)

    background_tasks.add_task(update_file, doc)
  #  file = db.get_file('annotate', document_id, False)
  #  doc = Document(**file)
    kObjs = doc.get_knowledgeObjects()


    return {"template": kObjs_as_html(kObjs)}

def update_file(document):
    """ Updates the document. """
    db.update_file(document)

@router.put("/annotation/annotation_split")
async def split_annotations(document_id: str, data: AnnotationItem, background_tasks: BackgroundTasks):
    file = db.get_file('annotate', document_id, False)
    if file is not None:
        doc = Document(**file)
        doc.split_kObj(data.data)
    background_tasks.add_task(update_file, doc)

  #  file = db.get_file('annotate', document_id, False)
  #  doc = Document(**file)
    kObjs = doc.get_knowledgeObjects()

    return {"template": kObjs_as_html(kObjs)}

@router.put("/annotation/change_category_annotations")
async def change_category_annotations(document_id: str, data: AnnotationItem, background_tasks: BackgroundTasks):
    file = db.get_file('annotate', document_id)
    if file is not None:
        doc = Document(**file)
        doc.update_kObj(data.data['id'], data.data)

    background_tasks.add_task(update_file, doc)
   # file = db.get_file('annotate', document_id, False)
   # doc = Document(**file)
    kObjs = doc.get_knowledgeObjects()

    return {"template": kObjs_as_html(kObjs)}

@router.put("/update_document", response_model=Item)
async def update_data(itemid: str, item: Item):
    file = db.get_file('extract', itemid, False)
    if file is not None:
        doc = Document(**file)
        if item.num.isnumeric():
            num = int(item.num)
        else:
            num = -1
        if item.type == "table":
            if 0 <= num < len(doc.tables):
                doc.tables[num].update_table(item.data, doc)
        elif item.type == "image":
            if 0 <= num < len(doc.images):
                doc.images[num].update_image(item.data['table'], doc)
        elif item.type == "text":
            doc.text.update_text(item.data['text'], doc)
    db.update_file(doc)
    #db.get_file('extract', itemid, False)
    return jsonable_encoder(item)


@router.get("/edit_document", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    file = db.get_file('extract', id, cached=False)
    state = file is not None
    has_images = False
    has_tables = False
    name = ''
    if state:
        doc = Document(**file)
        has_images = len(doc.images) > 0
        has_tables = len(doc.tables) > 0
        name = doc.file_name
    return templates.TemplateResponse("edit_document.html",
                                       {"request": request,
                                        "active": state,
                                        "has_images": has_images,
                                        "has_tables": has_tables,
                                        "id": id,
                                        "name": name,
                                        "num": -1,
                                        "step": 2

                                        })




@router.get("/edit_text", response_class=HTMLResponse)
async def read_item(request: Request, id: str):

    file = db.get_file('extract', id)
    doc = Document(**file)
    path = doc.get_path_to_file()
    return templates.TemplateResponse("edit_text.html",
                                      {"request": request,
                                       "id": id,
                                       "title": "Item",
                                       "active": True,
                                       "pdf_file": path,
                                       "text": doc.get_fulltext(),
                                       "type": 'text',
                                       "step": 2})


@router.get("/edit_images", response_class=HTMLResponse)
async def read_item(request: Request, id: str, num: int = 0):

    file = db.get_file('extract', id, False)
    doc = Document(**file)
    image = doc.get_image(num)
    image_base_64 = image.get_path_to_file()

    return templates.TemplateResponse("edit_images.html",
                                      {"request": request,
                                       "id": id,
                                       "title": "Item",
                                       "active": True,
                                       "image_base_64": image_base_64,
                                       "num": num,
                                       "type": "image",
                                       "step": 2})


@router.get("/edit_tables", response_class=HTMLResponse)
async def read_item(request: Request, id: str, num: int = 0):
    file = db.get_file('extract', id, False)
    doc = Document(**file)
    table = doc.get_table(num)

    num = abs(num) % len(doc.tables)

    image_base_64 = table.get_path_to_file()

    table_html = table_as_html(table)
    return templates.TemplateResponse("edit_table.html", {"request": request,
                                                          "id": id,
                                                          "title": "Item",
                                                          "active": True,
                                                          "image_base_64": image_base_64,
                                                          "table_html": table_html,
                                                          "rows": len(table.rows),
                                                          "columns": len(table.rows[0].cells) - 1,
                                                          "num": num,
                                                          "type": "table",
                                                          "step": 2})


@router.get("/edit_annotations", response_class=HTMLResponse)
async def read_item(request: Request, id: str, reload: str = ''):

    file = db.get_file('annotate', id, False)



    doc = Document(**file)

    knowledgeObjects: List[KnowledgeObject] = doc.get_knowledgeObjects()


    return templates.TemplateResponse("edit_annotations.html",
                                       {"request": request,
                                        "id": id,
                                        "active": True,
                                        "step": 3,
                                        "knowledgeObjects": knowledgeObjects,
                                      })
