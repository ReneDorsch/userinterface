from __future__ import annotations

import time

from pydantic import BaseModel, Field, validator
from typing import List, Union, Tuple, Optional

from base64 import urlsafe_b64decode, urlsafe_b64encode
import fitz
import os
from PIL import Image as pilImage
import PIL as pil
from io import BytesIO
from app.config import PATH_TO_APP, PATH_TO_TMP


class OptionSelection(BaseModel):
    id: str
    mode: str


class Word(BaseModel):
    id: int
    text: str
    normalized_text: str
    enriched_text: str
    annotation_id: int
    start_pos: int
    end_pos: int
    prev_word_id: int

class WordAnalysis(BaseModel):
    id: int
    word: str = Field(alias='text')
    normalized_word: str = Field(alias='normalized_text')
    longform_word: str = Field(alias='enriched_text')
    start_pos: int
    end_pos: int
    whitespace_after_word: int
    prev_word: Optional[int]
    knowledgeObject_reference: Optional[int]




class Annotation(BaseModel):
    id: int
    words: List[Word] = Field(default=[])
    word_ids: List[int] = Field(default=[])
    category: str


class KnowledgeObject(BaseModel):
    id: int
    category: str
    labels: List[str]
    annotation_ids: List[int] = Field(default=[])
    annotations: List[Annotation] = Field(default=[])


class KnowledgeObjectList(BaseModel):
    knowledgeObjects: List[KnowledgeObject]


class Answer(BaseModel):
    ''' A single answer of the context analysis. '''
    pass


class QuestionTemplate(BaseModel):
    ''' A QuestionTemplate is a Template that can be used to define questions. '''
    pass


class Author(BaseModel):
    first_name: str
    last_name: str


class Sentence(BaseModel):
    words: List[Word] = Field(default=[])
    text: str

    def __str__(self) -> str:
        return self.text


class Paragraph(BaseModel):
    sentences: List[Sentence] = Field(default=[])

    def __str__(self) -> str:
        res = [str(_) for _ in self.sentences]
        return " ".join(res)



class Chapter(BaseModel):
    paragraphs: List[Paragraph] = Field(default=[])
    pages: List[int] = []
    header: Header = Field(default=None)

    def update_chapter(self, data) -> None:
        ''' Updates the chapter with the given data. '''
        # todo: implement the function
        pass

    def get_chapter_as_pdf(self, document: 'Document'):
        ''' Gets the chapter as pdf. '''
        has_page_position: bool = len(self.pages) > 0
        if has_page_position:

            path_to_chapter: str = os.path.join(os.get_cwd(), f"static/tmp/document/{id(self)}.pdf")

            # Create a new PDF for the area in which the chapter is
            new_doc = fitz.open(path_to_chapter)
            pdf = fitz.open(stream=document.decode_file(), filetype='pdf')
            new_doc.insertPDF(pdf, from_page=min(self.pages), to_page=max(self.pages))

            # mark the relevant area of the pages
            new_doc = self._mark_relevant_area(new_doc)

            # save it at the path
            new_doc.save(path_to_chapter)

        else:
            path_to_chapter = document.get_path_to_file()

        return path_to_chapter

    def _mark_relevant_area(self, document):
        ''' Marks the relevant area of the file. '''
        # todo: Implement the marking function
        return document

    def __str__(self) -> str:
        ''' Gets the chapter as a string. '''
        res = ''
        for paragraph in self.paragraphs:
            res += str(paragraph) + "\n"
        return res


class Text(BaseModel):
    chapters: List[Chapter] = Field(default=[])
    abstract: Chapter = Field(default=None)
    title: str = Field(default="")
    authors: List[Author] = Field(default=[])


class Header(BaseModel):
    name: str = Field(default="")


class Cell(BaseModel):
    text: str = Field(default='')
    category: str = Field(default='')
    type: str = Field(default='')
    annotation_ids: List[int] = Field(default=[])


class Line(BaseModel):
    cells: List[Cell] = Field(default='')


class Row(Line):
    type: str = Field(default='')


class Column(Line):
    type: str = Field(default='')


class Table(BaseModel):
    rows: List[Row] = Field(default=[])
    columns: List[Column] = Field(default=[])
    description: str = Field(default='')
    name: str = Field(default='')
    base64_file: str = Field(default='')
    table_header: Union[Row, Column] = Field(default=None)
    units: List[str] = Field(default=[])


    def update_table(self, data) -> None:
        ''' Updates the table according to the given data. '''
        # todo: implement the function.
        pass

    def decode_file(self) -> str:
        ''' Decodes the binary (base64) file. '''
        img_bytes: List[bytes] = urlsafe_b64decode(self.base64_file.encode('utf-8'))
        return img_bytes

    def get_path_to_file(self) -> str:
        ''' Returns the path to the file. '''

        path_to_file: str = os.path.join(os.getcwd(), f"static/tmp/imgs/{id(self)}.png")

        file_already_exists: bool = os.path.isfile(path_to_file)
        if not file_already_exists:
            img_bytes = self.decode_file()
            img = pilImage.open(BytesIO(img_bytes))
            img.save(path_to_file, 'png')

        return f"../static/tmp/imgs/{id(self)}.png"


    def __del__(self):
        path_to_file: str = os.path.join(os.getcwd(), f"static/tmp/imgs/1{id(self)}.png")

        file_exits: bool = os.path.isfile(path_to_file)
        if file_exits:
            os.remove(path_to_file)


class Image(BaseModel):
    base64_file: str = Field(default="", description="The image in an base64 format.")
    description: str = Field(default='')
    name: str = Field(default='')


    def get_image(self):
        return self.base64_file

    def decode_file(self) -> str:
        ''' Decodes the binary (base64) file. '''
        img_bytes: List[bytes] = urlsafe_b64decode(self.base64_file.encode('utf-8'))
        return img_bytes


    def get_path_to_file(self) -> str:
        ''' Returns the path to the file. '''

        path_to_file: str = os.path.join(PATH_TO_TMP, f"imgs/{id(self)}.png")
        print(path_to_file)
        file_already_exists: bool = os.path.isfile(path_to_file)
        if not file_already_exists:
            img_bytes = self.decode_file()
            img = pilImage.open(BytesIO(img_bytes))
            img.save(path_to_file, 'png')
            time.sleep(0.5)

        return f"../static/tmp/imgs/{id(self)}.png"

    def convert_img_to_table(self, data) -> Table:
        ''' Converts the file to an table. '''
        pass

    def __del__(self):
        path_to_file: str = os.path.join(os.getcwd(), f"static/tmp/imgs/1{id(self)}.png")

        file_exits: bool = os.path.isfile(path_to_file)
        if file_exits:
            os.remove(path_to_file)


class Reference(BaseModel):
    doi: str = Field(default='')
    authors: List[Author] = Field(default=[],
                                  description="A Reference that was mentioned in the text. E.g. a citation. ")
    title: str = Field(default="", description='A Title of an reference.')


class _Answer_(BaseModel):
    id: int
    textual_representation: str
    question_id: int
    knowledgeObject_ids: List[int]
    context_id: int
    answer_source: str
    knowledgeObjects: List[KnowledgeObject] = []

    def update_knowledgeObjects(self, kObjs: List[KnowledgeObject]):
        ''' Gets a direct reference to each identified knowledgeObject. '''
        res = []
        for kObj in kObjs:
            if kObj.id in self.knowledgeObject_ids:
                res.append(kObj)
        self.knowledgeObjects = res


class _AnswerList_(BaseModel):
    answers: List[_Answer_]


class QuestionTemplate(BaseModel):
    weak_dependency_to: List[str] = Field(default=[],
                                          description="A dependency to another questionTemplate that can be used to optimize the questions.")
    strong_dependency_to: List[str] = Field(default=[],
                                            description="A necessary dependency to another questionTemplate that has to be answered before this question can be answered. ")

    broader_questionType: str = Field(
        description="The type of question in the broader sense. E.g Operational Parameter.")
    specific_questionType: str = Field(description="The type of question in a specific sense. E.g. Normalload")

    question: List[str] = Field(description="A List of questions that corresponds to this questionTemplate.")
    expectedAnswerSpace: List[str] = Field(
        description=" A list of categories (use <CATEGORY_TYPE>) or terms (interpreted as regex) that can be used to define acceptable answers. ")

    preSearchSpace: List[str] = Field(
        description=" A list of categories (use <CATEGORY_TYPE>) or terms (interpreted as regex) that can be used as a starting point to answer the questions. ")

    normalState: str = Field(default="",
                             description="If no answer has been found, A predefined answer can be used instead. ")
    dependend_from_variables: List[str] = Field(default=[], description="One or more dependencies.")

    has_final_answer: bool = False
    final_answers: List[Union[KnowledgeObject, str]] = []
    graph_pattern: List['TriplePattern'] = []

    def update_references(self, answers: List[Answer]) -> None:
        if any([_.final_result for _ in self.final_answers]):
            self.has_final_answer = True

    def get_triples(self) -> List[Tuple]:
        ''' Returns a list of all Triples found in the document. '''
        triples = []
        for pattern in self.graph_pattern:
            for answer in self.final_answers:
                pattern.add_answer(answer)
                triples.extend(pattern.get_triples())
        return triples

    def update_graph_structure(self, graph):
        for qTemplate_name, graph_pattern in graph.items():
            categories = qTemplate_name.split("/")
            only_broad: bool = len(categories) == 1

            if self.broader_questionType in categories:
                if only_broad:
                    self.graph_pattern.append(graph_pattern)
                elif self.specific_questionType in categories:
                    self.graph_pattern.append(graph_pattern)


class QuestionTemplateList(BaseModel):
    templates: List[QuestionTemplate]


class Answer(BaseModel):
    final_answer: List[Union[int, _Answer_]] = Field(description="List of Ids for answers")
    question_template: List[Union[str, QuestionTemplate]] = Field(description="The name of the questiontemplate")
    final_result: str

    def update_answer(self, answers: _AnswerList_):
        ''' Updates the answers so there is a direct reference. '''
        res = []
        for answer in answers.answers:
            if answer.id in self.final_answer:
                res.append(answer)
        self.final_answer = res

    def update_questiontemplate(self, list: QuestionTemplateList):
        ''' Updates the question_template of the Answer so there is a direct reference. '''
        res = []
        for questionTemplate in list.templates:
            if questionTemplate.broader_questionType in self.question_template:
                if questionTemplate.specific_questionType in self.question_template:
                    res.append(questionTemplate)
                    questionTemplate.final_answers.append(self)
        self.question_template = res


class AnswerList(BaseModel):
    answers: List[Answer]


class Metadata(BaseModel):
    abstract: Chapter = Field(default=None)
    references: List[Reference] = Field(default=[])
    issn: str = Field(default='')
    journal: str = Field(default='')
    title: str = Field(default='')
    subtitle: str = Field(default='')
    publisher: str = Field(default='')
    authors: List[Author] = Field(default=[])
    doi: str = Field(default='')


class Document(BaseModel):
    ''' A Document is the '''
    text: Text = Field(default=None)
    tables: List[Table] = Field(default=[])
    images: List[Image] = Field(default=[])
    metadata: Metadata = Field(default=None)
    base64_file: str = Field(default='')
    file_name: str = Field(default='')
    id: str = Field(alias="document_id")
    file_path: str = Field(default='')
    knowledgeObjects: List[KnowledgeObject] = Field(default=[])
    annotations: List[Annotation] = Field(default=[])

    class Config:
        allow_population_by_field_name = True

    def get_fulltext(self) -> str:
        """ Returns the completly extracted text. """
        text = ""
        for chapter in self.text.chapters:

            for paragraph in chapter.paragraphs:
                for sentence in paragraph.sentences:
                    text += sentence.text + " "
                text += "\n"
            text += "\n\n"

        return text

    def get_image(self, id: int):
        id = id % len(self.images)
        return self.images[id]

    def get_table(self, id: int):
        id = id % len(self.tables)
        return self.tables[id]


    def to_json(self):
        return self.json()

    def decode_file(self) -> str:
        ''' Decodes the binary (base64) file. '''
        pdf_bytes: List[bytes] = urlsafe_b64decode(self.base64_file.encode('utf-8'))
        return pdf_bytes

    def get_path_to_file(self) -> str:
        ''' Returns the path to the file. '''

        path_to_file: str = os.path.join(PATH_TO_TMP, f"document/{id(self)}.pdf")
        print(path_to_file)
        file_already_exists: bool = os.path.isfile(path_to_file)
        if not file_already_exists:
            pdf_bytes = self.decode_file()
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            doc.save(path_to_file)

        return f"../static/tmp/document/{id(self)}.pdf"

    def __del__(self):
        if hasattr(self, "id"):

            path_to_file: str = os.path.join(PATH_TO_APP, f"static/tmp/document/{self.id}.png")

            file_exits: bool = os.path.isfile(path_to_file)
            if file_exits:
                os.remove(path_to_file)


class ExtractionTaskDocument(BaseModel):
    document_id: str = Field(description="An ID that helps to uniquely identify a document. ")
    metadata: Metadata = Field(default=None, description='Metadata identified by analysing the pdf-document.')
    text: Text = Field(default=None, description="The extracted textinformation of the document. ")
    tables: List[Table] = Field(default=[], description="A list of tables extracted from the document. ")
    images: List[Image] = Field(default=[], description="A list of images extracted from the document. ")


Document.update_forward_refs()
Metadata.update_forward_refs()
Image.update_forward_refs()
Table.update_forward_refs()
Text.update_forward_refs()
ExtractionTaskDocument.update_forward_refs()
Header.update_forward_refs()
Chapter.update_forward_refs()