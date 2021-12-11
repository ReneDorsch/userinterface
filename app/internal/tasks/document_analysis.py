from app.internal.internal_datamodels import Document
from app.internal.parser.parsers import AnswerParser, AnnotationGraphParser, ContextGraphParser, QuestionTemplateParser
from app.internal.agent.graph_agent import GraphAgent
from typing import List
from app.config import PATH_TO_TRIPLEFILE, PATH_TO_QUESTIONTEMPLATE, PATH_TO_TMP
import os
import json

annotation_parser = AnnotationGraphParser()
context_parser = ContextGraphParser()
answer_parser = AnswerParser()
question_template_parser = QuestionTemplateParser()

def create_annotation_graph(document: Document):
    return annotation_parser.read_document(document)


def create_context_graph(document: Document):


    def to_dot(triples):
        class Node:
            def __init__(self, name):
                self.name: str = name
                self.colorscheme: List[str] = []

            def get_color(self):
                if "http:" not in self.name:
                    return "#66789f"
                if len(self.colorscheme) > 0:
                    return "#dce4f5"
                else:
                    return '#dddddd'

        class Edge:
            def __init__(self, name, fNode, sNode):
                self.name: str = name
                self.first_node: Node = fNode
                self.second_node: Node = sNode
                self.is_type: bool = "type" in name
                self.is_label: bool = "label" in name

            def __str__(self):
                def encode(name) -> str:
                    name = id(name)
                    return name

                f_name = encode(self.first_node.name)
                s_name = encode(self.second_node.name)
                f_color = self.first_node.get_color()
                s_color = self.second_node.get_color()
                f_label = "" if "http" in self.first_node.name else self.first_node.name
                s_label = "" if "http" in self.second_node.name else self.second_node.name
                e_label = edge.name.split("/")[-1]
                return f"""
{f_name}[label="{f_label}", color={f_color}, shape={"dot" if f_label == "" else "triangle"}]; 
{s_name}[label="{s_label}", color={s_color}, shape={"dot" if s_label == "" else "triangle"}]; 
{f_name} -> {s_name}[label="{e_label}", color=gray];"""

        zwerg = []
        dic = {}
        for triple in json.loads(triples):

            firstNode = triple[0]
            secondNode = triple[2]
            if firstNode not in dic:
                fNode = Node(firstNode)
                dic[firstNode] = fNode
            else:
                fNode = dic[firstNode]
            if secondNode not in dic:
                sNode = Node(secondNode)
                dic[secondNode] = sNode
            else:
                sNode = dic[secondNode]

            edge = Edge(triple[1], fNode, sNode)
            zwerg.append(edge)

        zwerg_2 = []
        for edge in zwerg:
            if edge.is_type:
                edge.first_node.colorscheme.append(edge.second_node.name)
            elif edge.is_label:
                edge.first_node.name = edge.second_node.name
            else:
                zwerg_2.append(edge)

        dic = {}
        res = ""
        for edge in zwerg_2:
            print(edge)
            res += str(edge)
        return res
        print("ok")
    answers = document.file_path
    g = GraphAgent(path_to_qt=PATH_TO_QUESTIONTEMPLATE,
                   path_to_graph=PATH_TO_TRIPLEFILE)
    res = g.get_graph(answers, linked_data_format=False)

    return "digraph { " + to_dot(res) + " }"

    print("ok")

def get_download_link(document: Document) -> str:
    """ Creates a path to the graph file. """
    answers = document.file_path
    g = GraphAgent(path_to_qt=PATH_TO_QUESTIONTEMPLATE,
                   path_to_graph=PATH_TO_TRIPLEFILE)

    res = g.get_graph(answers, linked_data_format=True)

    file_path = os.path.join(PATH_TO_TMP, f"{document.id}.json_ld")
    with open(file_path, "w") as file:
        file.write(res)

    return file_path
