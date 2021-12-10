from rdflib import Graph
from typing import List, Dict, Union, Tuple
from app.internal.internal_datamodels import KnowledgeObject
import json

class Triple:

    subject: Union[str, KnowledgeObject]
    predicate: str
    object: Union[str, KnowledgeObject]

    def get_triple(self) -> Tuple[str, str, str]:
        ''' Returns the triple as a list'''
        return [str(self.subject), str(self.predicate), str(self.object)]


class Knowledgegraph:

    def __init__(self):
        self.triples: List[Triple] = []
        self.graph: Graph = Graph()


    def add_triples(self, triples):
        self.triples.extend(triples)

    def create_graph(self, linked_data_format: bool=True, format: str="json-ld"):
        '''
            Creates and returns a new graph.
            If linked_data_format is activated it will be returned as a linked graph.
            Otherwise it will be returned as a json-file.
        '''

        if linked_data_format:
            return self._get_linked_graph(format)
        else:
            return self._get_graph()

    def _get_linked_graph(self, format: str):
        ''' Returns the triples as rdf-graph in the given format. '''
        g = Graph()
        for triple in self.triples:
            g.add(triple)


        return g.serialize(format=format)

    def _get_graph(self):
        ''' Returns the triples as a json file. '''

        def is_inside(triple: List, lis: List) -> bool:
            ''' Checks if the triple is already in the list. '''
            for o_triple in lis:
                if triple[0] == o_triple[0] and triple[1] == o_triple[1] and triple[2] == o_triple[2]:
                    return True
            return False

        res = []
        for triple in self.triples:
            if not is_inside(triple, res):
                res.append(triple)
        return json.dumps(res)

