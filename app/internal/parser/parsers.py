import re
from abc import ABC
from collections import defaultdict
from typing import List, Dict, Union
from app.internal.internal_datamodels import QuestionTemplateList, QuestionTemplate, Answer, AnswerList, KnowledgeObject, KnowledgeObjectList, \
    _AnswerList_, Document
import json
from rdflib import BNode, Namespace, RDFS, Literal, URIRef


class ABCParser(ABC):

    def read_file(self, file: str):
        ''' Reads the file and interprets it. '''


class QuestionTemplateParser(ABCParser):

    def read_file(self, file: Union[str, Dict]) -> QuestionTemplateList:
        res: List[QuestionTemplate] = []
        if isinstance(file, str):
            with open(file, 'r') as file:
                templates = json.load(file)
        else:
            templates = file

        res = QuestionTemplateList(templates=templates)

        return res


class AnswerParser(ABCParser):

    def read_file(self, file: Union[str, Dict]) -> AnswerList:
        res: List[Answer] = []
        if isinstance(file, str):
            with open(file, 'r') as file:
                data = json.load(file)
        else:
            data = file

        kObjs = KnowledgeObjectList(knowledgeObjects=data['knowledgeObjects'])
        answers = AnswerList(answers=data['answer_documents'])
        _answers = _AnswerList_(answers=data['answers'])

        for _answer in _answers.answers:
            _answer.update_knowledgeObjects(kObjs.knowledgeObjects)

        for answer in answers.answers:
            answer.update_answer(_answers)

        return answers


COLORSCHEMA = {
    'ManufacturingProcess': '#d8cef6',
    'OperationalParameter': '#dce4f5',
    'KinematicParameter': '#fbe4d5',
    'Specification': '#cd9bfb',
    'TestMethod': '#abd091',
    'Bodystructure': '#edb089',
    'CompositeElement': "#66789f",
    'table': '#dddddd',
    'paragraph': '#dddddd',
    'chapter': '#dddddd',
    'color' : '#888888'
}

class AnnotationGraphParser(ABCParser):

    def read_file(self, file: str):

        pass


    def read_document(self, doc: Document) -> List:

        class P:
            id = 1
            def __init__(self, paragraph):
                self.sentences = paragraph.sentences
                self.id = P.id
                P.id += 1
            def __str__(self):
                return f"""p_{self.id}[label="Paragraph {self.id}", shape=triangle, color={COLORSCHEMA['paragraph']}]"""

        class Triple:
            def __init__(self, kObj):
                self.id = kObj.id
                self.annotation_ids = kObj.annotation_ids
                self.labels = kObj.labels
                self.frequency = 1
                self.paragraphs = []
                self.category = kObj.category
                self.size = 1

            def resize(self, min, max):
                self.size = int((1 + (4*len(self.paragraphs))/max)*30)
                self.size = self.size

            def __str__(self):
                res = f"""t_{str(self.id)}[label="{max(self.labels)}",size={self.size}, shape=dot, color={COLORSCHEMA[self.category] if self.category in COLORSCHEMA else '#888888'}] -- """ + "{" + " ".join([f"p_{str(_.id)}" for _ in self.paragraphs]) + " }"
                return res

            def add(self, paragraph):
                if paragraph not in self.paragraphs:
                    self.paragraphs.append(paragraph)
                self.frequency += 1

        P.id = 1
        paragraphs = []
        for chapter in doc.text.chapters:
            for paragraph in chapter.paragraphs:
                paragraphs.append(P(paragraph))

        tables = doc.tables

        res = []
        _max = 0
        _min = 999
        for kObj in doc.knowledgeObjects:
            triple = Triple(kObj)
            for paragraph in paragraphs:
                for sentence in paragraph.sentences:
                    for word in sentence.words:
                        if word.annotation_id in kObj.annotation_ids:
                            triple.add(paragraph)

            # ToDo: Add counting of tables
            res.append(triple)
            if len(triple.paragraphs) > _max:
                _max = len(triple.paragraphs)
            if len(triple.paragraphs) < _min:
                _min = len(triple.paragraphs)

        for triple in res:
            triple.resize(_min, _max)
        res = [str(_) for _ in res if len(_.paragraphs) > 0] + [str(_) for _ in paragraphs ]
        res = "digraph {" + " ".join(res) + " } "
        return res




class ContextGraphParser(ABCParser):

    def __init__(self):
        self.variables: Dict[str, BNode] = {}
        self.namespaces: Dict[str, Namespace] = {}
        self.triples: Dict[str, List] = defaultdict(list)
        self.triplePatterns: Dict[str, 'TriplePattern'] = {}

    def read_file(self, file: str):
        # Splits the file in the different categories
        with open(file, 'r') as file:
            state = ''
            buffered: List[str] = []
            for line in file.readlines():
                # If new Data reconfigure the
                line = line.replace("\n", "")
                if line.rstrip().lstrip() == '':
                    if state == "IF ONLY":
                        templates = self._get_template(buffered)
                        triples = self._get_triples(buffered)
                        variables = self._get_variables(buffered)

                        for template in templates:
                            self.triples[template].extend(triples)
                        self.variables.update(variables)

                    elif state == "IF OR":
                        templates = self._get_template(buffered)
                        triples = self._get_triples(buffered)
                        variables = self._get_variables(buffered)
                        for template in templates:
                            self.triples[template].extend(triples)
                        self.variables.update(variables)

                    elif state == "IF AND":
                        templates = self._get_template(buffered)
                        triples = self._get_triples(buffered)
                        variables = self._get_variables(buffered)
                        for template in templates:
                            self.triples[template].extend(triples)
                        self.variables.update(variables)

                    state = ''
                    buffered = []
                else:
                    state = self._get_state(line, state)
                    if state == 'NAMESPACES':
                        uri, namespace = self._get_namespace(line)
                        if namespace != "" and uri != "":
                            self.namespaces[namespace] = uri
                    elif state == "IF ONLY":
                        buffered.append(line)
                    elif state == "IF OR":
                        buffered.append(line)
                    elif state == "IF AND":
                        buffered.append(line)

        for key, triples in self.triples.items():
            triplePattern = self._create_triplepatterns(triples, self.namespaces, self.variables)
            self.triplePatterns[key] = triplePattern
        # Namespaces

        # Conditionals

        # Triple
        return self.triplePatterns
    # AND OR ANY

    def _create_triplepatterns(self, triples: List, namespaces: Dict, variables: Dict) -> 'TripplePattern':
        ''' Creates predefined patterns of tripples that only need to add an answer to.'''
        class TriplePattern:
            triples = []
            def add_answer(self, answer):
                ''' Adds the answer to the triple. '''
                print("ok")
                # get the triples that contain the answer
                zwerg = []
                new_triples = []
                for triple in self.triples:
                    if "#ANSWER" in triple:
                        zwerg.append(triple)
                # update these triples
                for answer in answer.final_answer:
                    has_knowledgeObjects: bool = len(answer.knowledgeObjects) > 0
                    if has_knowledgeObjects:

                        KObjURI = URIRef(f"http://example_data.org/{id(answer)}")#BNode()

                        new_triples.append([KObjURI, RDFS.label, Literal(answer.textual_representation)])
                        for triple in zwerg:
                            _triple = [KObjURI if x == "#ANSWER" else x for x in triple]
                            new_triples.append(_triple)

                    # ToDo: Add the option that no knowledgeobject has been found
                self.triples.extend(new_triples)

            def get_triples(self):
                ''' Returns a List of triples in rdf-format. '''
                res = []
                for triple in self.triples:
                    if "#ANSWER" not in triple:
                        res.append(triple)
                return res



        res = TriplePattern()
        for triple in triples:
            _triple = []
            for element in triple:
                is_variable: bool = element.startswith("<")
                has_namespace: bool = ":" in element
                if is_variable:
                    _triple.append(variables[element[1:-1]])
                elif has_namespace:
                    namespace, reference = element.split(":")
                    _triple.append(namespaces[namespace][reference])
                else:
                    _triple.append(element)
            res.triples.append(_triple)
        return res


    def _get_namespace(self, line: str):
        ''' Gets the namespace and uri from the line '''

        uri = line.split(": ")[1].rstrip().lstrip()
        namespace = line.split(": ")[0].rstrip().lstrip()

        if "" == namespace or "" == uri:
            return "", ""

        uri = re.sub(">.*\.?", "", uri)
        uri = re.sub("^<", "", uri)
        return Namespace(uri), namespace

    def _get_state(self, line: str, state) -> str:
        ''' Returns the state. '''
        if line.startswith("IF"):
            if "AND" in line:
                return "IF AND"
            elif "OR" in line:
                return "IF OR"
            else:
                return "IF ONLY"
        elif "NAMESPACE" in line:
            return "NAMESPACES"
        else:
            return state

    def _get_template(self, lines: List[str]) -> List[str]:
        first_line = lines[0]
        first_line = re.sub("IF {0,}", "", first_line)
        first_line = re.sub(":", "", first_line)
        if " AND " in first_line:
            return first_line.split(" AND ")
        if " OR " in first_line:
            return first_line.split(" OR ")
        return [first_line]

    def _get_triples(self, lines: List[str]) -> str:
        lines = lines[1:]
        res = []
        for line in lines:
            line = line.rstrip().replace(".", "")
            res.append(line.split(" "))
        return res

    def _get_variables(self, lines: List[str]) -> Dict[str, BNode]:
        lines = lines[1:]
        variables = set()
        res = {}
        for line in lines:
            for word in line.split(" "):
                if word.startswith("<"):
                    if word.endswith(">"):
                        variables.add(word[1:-1])
                    elif word.endswith("."):
                        variables.add(word[1:-2])

        for variable in variables:
            res[variable] = URIRef(f"http://example.org/{id(variable)}") #BNode()
        return res



