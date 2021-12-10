from __future__ import annotations
from pydantic import BaseModel, Field, validator
from app.internal.internal_datamodels import Metadata, Text, Table, Image
from typing import List, Union, Optional, Tuple, Any


class ExtractionTask(BaseModel):
    document_id: str


class AnnotationTask(BaseModel):
    document_id: str


class AnalysesTask(BaseModel):
    document_id: str


class ExtractionInput(BaseModel):
    file: str = Field(alias="base64_file")
    document_id: str = Field(alias="id")

    class Config:
        allow_population_by_field_name = True


class Cell(BaseModel):
    text: str
    category: str = Field(default='')
    type: str = Field(default='')


class Line(BaseModel):
    cells: List[Cell] = Field(description="A list of cells at their position in the Line ")


class Row(Line):
    cells: List[Cell] = Field(description="A list of Cells in the row. ")
    type: str = Field(default='')


class Column(Line):
    cells: List[Cell] = Field(description="A list of Cells in the column. ")
    type: str = Field(default='')


class Table(BaseModel):
    rows: List[Row] = Field(description="A list of rows for the table. ")
    columns: List[Column] = Field(description="A list of columns for the table. ")
    table_header: Union[Column, Row] = Field(default=None, description="A Line that corresponds to the header.")
    units: List[str] = Field(default=[])


class Sentence(BaseModel):
    text: str = Field(default='', description="The text from this sentence")


class Paragraph(BaseModel):
    sentences: List[Sentence] = Field(description="A list of sentences identified for this chapter. ")


class Chapter(BaseModel):
    paragraphs: List[Paragraph] = Field(description="A list of paragraphs identified for this chapter. ")


class AnnotationInput(BaseModel):
    id: str
    text: Text = Field(description='The actual textual information of the document.')
    metadata: Metadata = Field(default=None,
                               description='The Abstract of the document. ')
    tables: List[Table] = Field(description='The Tables of the document.', default=[])


class InputWord(BaseModel):
    id: int
    word: str
    normalized_word: str
    longform_word: str
    start_pos: int
    end_pos: int
    whitespace_after_word: int
    prev_word: Optional[int]
    knowledgeObject_reference: Optional[int]


class InputKnowledgeObject(BaseModel):
    id: int
    category: str
    labels: List[str]


class InputSentence(BaseModel):
    words: List[InputWord]
    knowledgeObject_references: List[int]


class InputParagraph(BaseModel):
    sentences: List[InputSentence]
    knowledgeObject_references: List[int]


class InputChapter(BaseModel):
    paragraphs: List[InputParagraph]
    knowledgeObject_references: List[int]


class InputCell(BaseModel):
    text: str
    category: str
    knowledgeObject_references: Optional[List[int]]


class InputLine(BaseModel):
    cells: List[InputCell]


class InputTable(BaseModel):
    # textual_representation: List[InputSentence]
    knowledgeObject_references: List[int]
    description: Optional[str]
    table_header: InputLine
    data: List[InputLine]
    units: List[str]


class AnalysisInput(BaseModel):
    document_id: str
    chapters: List[InputChapter]
    knowledgeObjects: List[InputKnowledgeObject]
    abstract: Optional[InputChapter]
    tables: Optional[List[InputTable]]
    id: str = ''
    file_name: str = ''
    file_path: str = ''


class documenTuple(BaseModel):
    answerDocument_id: int
    answer_id: int


class AnswerDocument(BaseModel):
    id: int
    final_result: str
    final_answer: List
    type: str
    question_template: Tuple[str, str]
    final_answer_knowledgeObject_table_ids: List[int]
    final_answer_knowledgeObject_text_ids: List[int]
    final_answer_textual_representation_text: Any
    final_answer_textual_representation_table: Any
    final_result_knowledgeobject_text: str
    final_result_knowledgeobject_table: str
    table_answer_ids: List[int]
    text_answer_ids: List[int]


class Question(BaseModel):
    id: int
    question: str


class Context(BaseModel):
    id: int
    textual_representation: str
    knowledgeObject_ids: List[int]


class Hypothesis(BaseModel):
    answer_document_tuples: List[documenTuple] = Field(default=[])


class AnswerDocumentList(BaseModel):
    answer_documents: List[AnswerDocument]
    document_id: str


class HypothesisList(BaseModel):
    hypothesis: List[Hypothesis]
    answer_documents: List[AnswerDocument]
    document_id: str
    file_path: str = ''
    file_name: str = ''
    id: str = ''

    def to_json(self):
        return self.json()


class Answer(BaseModel):
    id: int
    textual_representation: str
    question_id: int
    knowledgeObject_ids: List[int]
    context_id: int
    answer_source: str


class KnowledgeObject(BaseModel):
    id: int
    category: str
    labels: List[str]


class LogFile(BaseModel):
    answer_documents: List[AnswerDocument] = Field(
        description="A list of answers corresponding to the questiontemplates. ")
    hypothesis: List[Hypothesis] = Field(description="A List of Hypothesis that has been identified in the document. ")
    answers: List[Answer] = Field(description="A list of all generated answers for all the questions in the document. ")
    contexts: List[Context] = Field(description="A list of contexts corresponding to the answers and questions. ")
    questions: List[Question] = Field(description="A list of questions generated for the answer documents. ")
    knowledgeObjects: List[KnowledgeObject]
    document_id: str = ''
    id: str = ''
    file_name: str = ''
    file_path: str = ''

    def to_json(self):
        return self.json()