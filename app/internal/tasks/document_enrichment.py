import time

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from database.database import db
from app.internal.utils import post_file, get_response_code, get_response
from app.config import EXTRACTION_MODULE_API, ANNOTATION_MODULE_API, ANALYSIS_MODULE_API, DATABASE_PATHS
from app.static.routers.requestTypes import ExtractionInput, AnalysisInput, AnnotationInput, LogFile, HypothesisList, Image, Row, Column
from app.internal.internal_datamodels import Document, Author, Reference, Metadata
import os
from typing import Dict, Union, Callable

templates = Jinja2Templates(directory="static/templates")
router = APIRouter(
    prefix="/semantic_enrichment",
    responses={404: {"description": "Not found"}},
)

def wait_for_response(id: str, API: Dict):
    # Waits until the microservice has created the file
    api_call = API['BASEURI'] + API['has_results'] + f"{id}"
    while True:
        response_code: int = get_response_code(api_call)
        if response_code == 201:
            break
        else:
            time.sleep(1)


def execute_enrichment_tasks(id: str):

    file = start_extraction(id)
    file = start_annotation(id, file)
    start_analysis(id, file)
    print("ok")


def start_task(document_id: str, index: str, API: str, REQUESTFORMAT, previous_document: Union[Dict, None] = None,
               mapping_func: Callable = None):

    api_call = API['BASEURI'] + API['send_to']
    if previous_document is None:
        file = db.get_file(index, document_id)
    else:
        file = previous_document.dict()

    if mapping_func is not None:
        request = REQUESTFORMAT(**mapping_func(file))
    else:
        request = REQUESTFORMAT(**file)
    post_file(request, api_call)
    return file




def get_data(id: str, API: Dict):
    api_call = API['BASEURI'] + API['get_results'] + f"{id}"
    data = get_response(api_call)
    return data

def start_extraction(id: str, mapping_func: Callable = None):

    def update_document(doc: Document, file: Dict):
        doc.base64_file = file["base64_file"]
        return doc

    file = start_task(id, 'upload', EXTRACTION_MODULE_API, ExtractionInput, mapping_func)
    wait_for_response(id, EXTRACTION_MODULE_API)
    data = get_data(id, EXTRACTION_MODULE_API)

    file_path = os.path.join(DATABASE_PATHS['extract'], f"{id}.json")
    data.update({'file_name': file['file_name'],
                 'file_path': file_path})


    doc = Document(**data)

    doc = update_document(doc, file)
    db.add_file(doc, 'extract')
    db.save_indexes()

    return doc



def start_annotation(id: str, document: Union[Document, None] = None, mapping_func: Callable = None):

    def update_document(doc: Document, file: Union[Dict, Document]):
        if not isinstance(file, dict):
            file = file.dict()
        doc.base64_file = file["base64_file"]
        doc.images = [Image(**_) for _ in file['images']]
        for table, _table_data in zip(doc.tables, file['tables']):
            units = table.units

            header = _table_data['table_header']

            if header['type'] == 'row':
                header = Row(**header)
            else:
                header = Column(**header)
            table.table_header = header
            table.base64_file = _table_data['base64_file']
            table.name = _table_data['name']
            table.description = _table_data['description']
            table.units = units if len(units) != 0 else ["" for _ in header.cells]

        doc.metadata = Metadata()
        doc.metadata.references = [Reference(**_) for _ in file['metadata']['references']]
        doc.metadata.issn = file['metadata']['issn']
        doc.metadata.journal = file['metadata']['journal']
        doc.metadata.title = file['metadata']['title']
        doc.metadata.subtitle = file['metadata']['subtitle']
        doc.metadata.publisher = file['metadata']['publisher']
        doc.metadata.authors = [Author(**_) for _ in file['metadata']['authors']]
        doc.metadata.doi = file['metadata']['doi']


        doc.metadata.abstract = doc.text.abstract
        doc.text.authors = [Author(**_) for _ in file['metadata']['authors']]
        doc.text.title = file['metadata']['title']

        return doc



    file = start_task(id, 'extract', ANNOTATION_MODULE_API, AnnotationInput, document, mapping_func)
    wait_for_response(id, ANNOTATION_MODULE_API)
    data = get_data(id, ANNOTATION_MODULE_API)

    file_path = os.path.join(DATABASE_PATHS['annotate'], f"{id}.json")
    data.update({'file_name': file['file_name'],
                 'file_path': file_path})


    doc = Document(**data)

    doc = update_document(doc, file)
    db.add_file(doc, 'annotate')
    db.save_indexes()

    return doc

def start_analysis(id: str, document: Union[Document, None] = None, mapping_func: Callable = None):

    file = start_task(id, 'annotate', ANALYSIS_MODULE_API, AnalysisInput, document, _map_data_for_analysis)
    wait_for_response(id, ANALYSIS_MODULE_API)
    data = get_data(id, ANALYSIS_MODULE_API)

    file_path = os.path.join(DATABASE_PATHS['analyse'], f"{id}.json")

    doc = LogFile(**data)
    doc.id = doc.document_id
    doc.file_name = file['file_name']
    doc.file_path = file_path




    db.add_file(doc, 'analyse', True)
    db.save_indexes()


def _map_data_for_analysis(data: Dict) -> Dict:

    data['document_id'] = data['id']

    # get all kObjs
    kObjs = data['knowledgeObjects']
    kObjDict = {}
    for kObj in kObjs:
        id_ = kObj['id']
        for anno in kObj['annotation_ids']:
            kObjDict[anno] = id_

    data['knowledgeObjects'] = kObjs

    # Update the table
    for table in data['tables']:
        knowledgeObjects_in_table = []
        if table['table_header']['type'] == "row":
            lines = table['rows']
        else:
            lines = table['columns']

        _lines = []
        for line in lines:
            _line = []
            for cell in line['cells']:

                if cell['annotation_ids'] != []:
                    kObj_ids = []
                    for id in cell['annotation_ids']:
                        kObj_ids.append(kObjDict[id])
                    cell.update({'knowledgeObject_references': kObj_ids})
                    knowledgeObjects_in_table.extend(kObj_ids)
                _line.append(cell)
            _lines.append({'cells': _line})
        table['data'] = _lines
        table['knowledgeObject_references'] = knowledgeObjects_in_table

    # Update the id, whitespace, next_word, and kobjref

    for chapter in data['text']['chapters'] + [data['text']['abstract']]:
        kObjs_in_chapter = []
        for paragraph in chapter['paragraphs']:
            kObjs_in_paragraph = []
            for sentence in paragraph['sentences']:
                prev_word = None
                kObjs_in_sentence = []
                for num, word in enumerate(sentence['words'][:-1]):
                    next_word = sentence['words'][num + 1]
                    a_id = word["annotation_id"]
                    word.update({
                        "knowledgeObject_reference": kObjDict[a_id] if a_id != -1 else None,
                        "whitespace_after_word": next_word["start_pos"] - word["end_pos"] > 0,
                        "prev_word": word['prev_word_id'],
                        "normalized_word": word['normalized_text'],
                        "word": word['text'],
                        "longform_word": word['enriched_text']
                    })
                    if a_id != -1:
                        kObjs_in_sentence.append(kObjDict[a_id])

                sentence['knowledgeObject_references'] = list(set(kObjs_in_sentence))
                kObjs_in_paragraph.extend(kObjs_in_sentence)
                if len(sentence["words"]) > 0:
                    last_word = sentence['words'][-1]
                    a_id = last_word["annotation_id"]
                    last_word.update({
                        "knowledgeObject_reference": kObjDict[a_id] if a_id != -1 else None,
                        "whitespace_after_word": 0,
                        "prev_word": last_word['prev_word_id'],
                        "normalized_word": last_word['normalized_text'],
                        "word": last_word['text'],
                        "longform_word": last_word['enriched_text']
                    })



            paragraph['knowledgeObject_references'] = list(set(kObjs_in_paragraph))
            kObjs_in_chapter.extend(kObjs_in_paragraph)
        chapter['knowledgeObject_references'] = list(set(kObjs_in_chapter))

    data['chapters'] = data['text']['chapters']
    data['abstract'] = data['text']['abstract']
    return data