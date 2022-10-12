from rocksdict import Rdict 
import re
import random
import string 
from pathlib import Path


class DocumentDB():
    def __init__(self, path: str = "../database/"):
        self.path = path
        self.db = Rdict(path)
    
    def _delete_old_logs(self):
        database_path = Path(self.path)    
        database_files = list(database_path.iterdir())
        
        for filename in database_files:
            if filename.name[:7] == "LOG.old":
                filename.unlink()
             

    def _generate_id(self):
        characters = string.ascii_letters + string.digits 
        doc_id = ''.join(random.choice(characters) for i in range(8))

        return doc_id


    def insert_object(self, document):
        document_dict = document.__dict__.copy()
        doc_id = self.insert(document_dict)

        return doc_id


    def insert(self, document):
        # encoding: 
        # doc_id/column_name -> value 

        if "_id" not in document:
            document["_id"] = self._generate_id()
        
        doc_id = document["_id"]

        for key, value in document.items():
            if key != "_id":
                key_string = f"{doc_id}/{key}"
                self.db[key_string] = value

        self._delete_old_logs()
        return doc_id


    def insert_batch(self, document_list):
        for document in document_list:
            self.insert(document)


    def insert_object_batch(self, object_list):
        for object in object_list:
            self.insert_object(object)


    def _get(self, key):
        return self.db[key]

    
    def _iterate_keys(self):
        for key in self.db.keys():
            yield key
        
        self._delete_old_logs()

    def get_id_exact(self, field, value, max_count: int = None):
        all_ids = []

        for key in self._iterate_keys():
            
            key_column = key.split("/")[1]
            
            if field == key_column:
                if value == self._get(key):
                    row_id = key.split("/")[0]
                    all_ids.append(row_id)
        
            if max_count:
                if len(all_ids) == max_count:
                    return all_ids
        
        return all_ids
                    

    def get_id_contains(self, field, value, max_count: int = None):
        all_ids = []

        for key in self._iterate_keys():
            
            key_column = key.split("/")[1]
            key_value = self._get(key)

            if (field == key_column) and key_value:
                if value in self._get(key):
                    row_id = key.split("/")[0]
                    all_ids.append(row_id)
        
            if max_count:
                if len(all_ids) == max_count:
                    return all_ids
        
        return all_ids

    def _contains(self, field, value, max_count: int = None):
        results = []
        doc_ids = self.get_id_contains(field, value, max_count)

        if doc_ids:
            for doc_id in doc_ids:
                doc_dict = {}
                doc_dict["_id"] = doc_id
                
                for key in self._iterate_keys():
                    search_doc_id = key.split("/")[0]

                    if (search_doc_id == doc_id):

                        column_name = key.split("/")[1]
                        doc_dict[column_name] = self._get(key)

                results.append(doc_dict)

        return results

    
    def _exact(self, field, value, max_count: int = None):
        results = []
        doc_ids = self.get_id_exact(field, value, max_count)

        if doc_ids:
            for doc_id in doc_ids:
                doc_dict = {}
                doc_dict["_id"] = doc_id
                
                for key in self._iterate_keys():
                    search_doc_id =  key.split("/")[0]

                    if (search_doc_id == doc_id):
                        column_name = key.split("/")[1]
                        doc_dict[column_name] = self._get(key)

                results.append(doc_dict)

        return results


    def search(self, field, value, type: str = "exact", max_count: int = None):
        if type == "exact":
            results = self._exact(field, value, max_count)
        
        elif type == "contains":
            results = self._contains(field, value, max_count)
        
        else:
            print(f"Wrong search type specified. Must specifiy 'exact' or 'contains' not {type}\n")
            return None

        self._delete_old_logs()
        return results
    

    def delete(self, id):
        did_delete = False

        for key in self._iterate_keys():
            doc_id = key.split("/")[0]

            if id == doc_id:
                self.db[key] = None
                did_delete = True

        self._delete_old_logs()
        return did_delete


    def delete_bath(self, id_list):
        for id in id_list:
            self.delete(id)
        
    
    def get(self, id):
        document = {}

        for key in self._iterate_keys():
            search_doc_id = key.split("/")[0]

            if (search_doc_id == id):
                column_name = key.split("/")[1]
                document[column_name] = self._get(key)

        if document:
            document["_id"] = id

        return document
    

    def get_batch(self, id_list):
        results = []

        for id in id_list:
            document = self.get(id)
            results.append(document)

        return results


            