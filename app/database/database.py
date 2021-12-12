from __future__ import annotations
import os
from typing import Dict, Union
import json
from json.decoder import JSONDecodeError
from app.config import database_folders, indexs, PATH_TO_APP
from app.internal.internal_datamodels import Document, QuestionTemplate, QuestionTemplateList
from typing import List
from functools import lru_cache

class Index:

    def __init__(self, file_path):
        self.file_path: str = file_path
        self.data: Dict = self._create_index(file_path)


    def _create_index(self, path_to_index: str):
        ''' Creates a search index for the files already in the database. '''
        file_exists: bool = os.path.isfile(path_to_index)
        if not file_exists:
            os.makedirs(os.path.dirname(path_to_index), exist_ok=True)
            return {}
        with open(path_to_index, 'r', encoding='utf-8') as index_file:
            try:
                index = json.load(index_file)
            except JSONDecodeError:
                index = {}
        return index

    def save_index(self):
        ''' Savs the index. '''
        with open(self.file_path, 'w', encoding='utf-8') as index_file:
            json.dump(self.data, index_file)

    def update_index(self, id: str, path_to_file: str) -> bool:
        ''' Updates the index if possible and returns true '''
        try:
            self.data[id] = path_to_file
            return True
        except KeyError:
            return False

    def add_id(self, id: str, path_to_file: str) -> bool:
        return self.update_index(id, path_to_file)

    def del_id(self, id: str) -> bool:
        ''' Deletes an id from the index if avaiable. '''
        if id in self.data:
            file_path = self.data[id]
            try:
                os.remove(file_path)
            except:
                return False
            del self.data[id]
            return True
        return True
        
class DataBase:


    _indexs: Dict[str, Index] = {idx: Index(os.path.join(PATH_TO_APP, path)) for idx, path in indexs.items()}


    def get_file(self, index: str, file_id: str, cached: bool = True) -> Dict:
        """ Method to get a file. """
        if cached:
            return self._get_cached_file(index, file_id)
        else:
            return self._get_file(index, file_id)



    @lru_cache()
    def _get_cached_file(self, index: str, file_id: str) -> Dict:
        """ If cached data is available use the cached fil.e"""
        return self._get_file(index, file_id)

    def _get_file(self, index: str, file_id: str) -> Dict:
        ''' Loads and returns the document if found else it returns false. '''
        _index = self._indexs[index]
        if file_id in _index.data:
            path_to_file: str = _index.data[file_id]
            with open(path_to_file, "r") as file:
                data = json.load(file)
            return data
        return None



    def get_all_files(self, index: str, cached: bool = True) -> List[Document]:
        """ Returns all files from a given index. """
        if cached:
            return self._get_cached_all_files(index)
        else:
            return self._get_all_files(index)

    @lru_cache()
    def _get_cached_all_files(self, index: str) -> List[Document]:
        return self._get_all_files(index)

    def _get_all_files(self, index: str) -> List[Document]:
        """ Returns all files from a given index. """
        res = []
        _index = self._indexs[index]
        for path_to_file in _index.data.values():
            with open(path_to_file, "r") as file:
                res.append(json.load(file))
        return res

    def add_file(self, file: Union[Document, QuestionTemplate, 'TripleTemplate'], file_type, overwrite=False):
        ''' Adds a new file to the db. '''
        if file_type in self._indexs:
            index = self._indexs[file_type]
            if file.id in index.data and not overwrite:
                return False
            else:
                index.add_id(file.id, file.file_path)
                with open(file.file_path, 'w') as f:
                    f.write(file.to_json()) #.dump(file.to_json(), f)
                return True
        else:
            return False

    def update_file(self, file: Union[Document, QuestionTemplate, 'TripleTemplate']):
        ''' Updates the files. '''
        file_path = file.file_path
        with open(file_path, "w") as f:
            json.dump(file.dict(), f)
        
    def del_file(self, file, file_type: str):
        ''' Deletes the file and reload the indexs. '''

        if file_type == 'all':
            res = []
            for idx in self._indexs.keys():
                result = self._indexs[idx].del_id(file.id)
                res.append(result)
            return any(res)
        else:
            if file_type in self._indexs:
                index = self._indexs[file_type]
                return index.del_id(file.id)

    def save_indexes(self):
        ''' Save all indexes. '''
        for idx in self._indexs.values():
            idx.save_index()



db = DataBase()