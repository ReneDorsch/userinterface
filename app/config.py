import os.path

import app as main


###############################################################################
###############################################################################
###############################################################################
# IP-Adresses:
# The IP-Adresses to other known modules.
EXTRACTION_MODULE_API = {
    "BASEURI" : "http://127.0.0.1:8002",
    "send_to": "/extraction/transform_pdf_to_data",
    "has_results": "/extraction/has_extraction/?document_id=",
    "get_results": "/extraction/get_task_extraction/?document_id="
                         }
ANNOTATION_MODULE_API = {
    "BASEURI" : "http://127.0.0.1:8003",
    "send_to": "/annotation/extract_annotations",
    "has_results": "/annotation/has_results/?document_id=",
    "get_results": "/annotation/get_task_results/?document_id="
                         }
ANALYSIS_MODULE_API = {
    "BASEURI" : "http://127.0.0.1:8007",
    "send_to": "/api/contextualize_data",
    "has_results": "/analysis/has_results/?document_id=",
    "get_results": "/annotation/get_full_logs/?document_id="
                         }

###############################################################################
###############################################################################
###############################################################################
# Database:
# These are the folders where the files will be saved.
# 
database_folders = {
            'upload': 'database/files/uploaded',
            'extract': 'database/files/extracted',
            'annotate': 'database/files/annotated',
            'analyse': 'database/files/analysed',
            'question_template': 'database/files/question_templates',
            'triple_template': 'database/files/triple_templates'
        }

###############################################################################
###############################################################################
###############################################################################
# Indexs:
# The Indexs are part of the database. These helps to identify fast different 
# documents

indexs = {
            'upload': 'database/files/indexes/uploaded.json',
            'extract': 'database/files/indexes/extracted.json',
            'annotate': 'database/files/indexes/annotated.json',
            'analyse': 'database/files/indexes/analysed.json',
            'question_template': 'database/files/indexes/question_templates.json',
            'triple_template': 'database/files/indexes/triple_templates.json'
        }

##################
# Paths

PATH_TO_APP = os.path.abspath(main.__file__).replace("__init__.py", "")
DATABASE_PATHS = {type: os.path.join(PATH_TO_APP, rel_path) for type, rel_path in database_folders.items()}
PATH_TO_TMP = os.path.join(PATH_TO_APP, "static/tmp")
PATH_TO_QUESTIONTEMPLATE = os.path.join(PATH_TO_APP, "files/question_templates.json")
PATH_TO_TRIPLEFILE = os.path.join(PATH_TO_APP, "files/test_triple.txt")