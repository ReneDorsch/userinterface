from __future__ import annotations
from .agent import ABCAgent
from ..parser.graph import Knowledgegraph, Triple
from app.internal.internal_datamodels import QuestionTemplateList, AnswerList
from typing import List, Union, Dict

from ..parser.parsers import ContextGraphParser, QuestionTemplateParser, AnswerParser
from rdflib import Graph, BNode

class GraphAgent(ABCAgent):

    def __init__(self, path_to_qt: str, path_to_graph: str):
        self.path_to_question_templates: str = path_to_qt
        self.question_templates: QuestionTemplateList = []
        self.graph: Knowledgegraph = Knowledgegraph()
        self.path_to_graph_structure = path_to_graph
        self.graph_structure: List = []


    def update_question_templates(self, path_to_qt: str) -> None:
        ''' Updates the questiontemplate according to the new path. '''
        self.path_to_question_templates = path_to_qt

    def update_question_templates(self, path_to_graph: str) -> None:
        ''' Updates the graph Structure according to the new path. '''
        self.path_to_graph_structure = path_to_graph


    def get_graph(self, answers: Union[str, Dict], linked_data_format: bool=True, format: str="json-ld"):
        ''' Returns the graph. '''
        self.question_templates = self._set_question_template(self.path_to_question_templates, answers)

        for questionTemplate in self.question_templates.templates:
            if questionTemplate.has_final_answer:
                triples: List[Triple] = questionTemplate.get_triples()
                self.graph.add_triples(triples)

        return self.graph.create_graph(linked_data_format, format)


    def _set_question_template(self, path_to_qTemplates, answers) -> QuestionTemplateList:
        ''' Reads the answers and maps the corresponding QuestionTemplates and GraphStructure to them.'''
        aParser = AnswerParser()
        qParser = QuestionTemplateParser()
        gParser = ContextGraphParser()
        answers: AnswerList = aParser.read_file(answers)
        graph = gParser.read_file(self.path_to_graph_structure)
        qTemplates: QuestionTemplateList = qParser.read_file(path_to_qTemplates)
        for answer in answers.answers:
            answer.update_questiontemplate(qTemplates)

        for qTemplate in qTemplates.templates:
            qTemplate.update_graph_structure(graph)
            qTemplate.update_references(answers.answers)

        return qTemplates
