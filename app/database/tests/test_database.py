from unittest import TestCase
from app.database.database import DataBase


class Document:
    def __init__(self):
        self.id = id(self)
        self.file_path: str
        self.data: dict

    def to_json(self):
        return self.data

class TestDataBase(TestCase):

    def test_update_file(self):

        db = DataBase()
        doc = Document()
        doc.file_path = "/home/rene/userinterface/app/database/files/analysed/test_2.txt"
        doc.data = {
                    "test": "asdasd",
                    "test_2": [2, 4, 6]
                    }

        db.update_file(doc)

    def test_add_file(self):
        db = DataBase()
        doc = Document()
        doc.id = str(123123123)
        doc.data = {
                    "test": "asdasd",
                    "test_2": [2, 4, 6]
                    }
        doc.file_path = "/home/rene/userinterface/app/database/files/analysed/test_2.txt"
        self.assertTrue(db.add_file(doc, 'analyse'))
        db.save_indexes()



    def test_del_file(self):
        db = DataBase()
        doc = Document()
        doc.id = str(123123123)
        doc.data = {
                    "test": "asdasd",
                    "test_2": [2, 4, 6]
                    }
        doc.file_path = "/home/rene/userinterface/app/database/files/analysed/test_2.txt"
        self.assertTrue(db.del_file(doc, 'analyse'))
        db.save_indexes()

    def test_del_file(self):
        db = DataBase()
        doc = Document()
        doc.id = str(123123123)
        doc.data = {
                    "test": "asdasd",
                    "test_2": [2, 4, 6]
                    }
        doc.file_path = "/home/rene/userinterface/app/database/files/analysed/test_2.txt"
        self.assertTrue(db.del_file(doc, 'all'))
        db.save_indexes()