from db.mongo import db
import json

class CategoryRepository:
    def __init__(self):
        self.categories_file_path = "categories/categories.json"
    
    def find_all_by_type(self, type: str):
        with open(self.categories_file_path) as json_data:
            d = json.load(json_data)
            return d.get(type, [])