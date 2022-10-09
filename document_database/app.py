from fastapi import FastAPI
from document_db import DocumentDB

app = FastAPI()


@app.get("/search/")
async def search(type: str, field: str, value: str):
    db = DocumentDB("../database")
    results = db.search(field=field, value=value, type=type)

    return {"results": results}


@app.get("/document/{doc_id}")
async def get_document(doc_id):
    db = DocumentDB("../database")
    result = db.get_document(str(doc_id))

    return result

@app.delete("/delete/{doc_id}")
async def delete_document(doc_id):
    db = DocumentDB("../database")
    db.delete([doc_id])

    return {"successful": True}


# TO-DO:  
# connect to db 
# insert doc