from db.mongo import db
import json

class CategoryRepository:
    def __init__(self):
        self.categories_file_path = "categories/categories.json"
    
    def find_all_by_type(self, type: str):
        with open(self.categories_file_path) as json_data:
            d = json.load(json_data)
            return d.get(type, [])

    def get_category_label(self, type: str, value: str):
        with open(self.categories_file_path) as json_data:
            d = json.load(json_data)
            categories = d.get(type, [])
            for category in categories:
                if category['value'] == value:
                    return category['label']
            return None