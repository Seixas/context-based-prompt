from fastapi import Depends, Request, APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from starlette.responses import JSONResponse
from tempfile import NamedTemporaryFile
import os

from ..schemas import req, res
from ..domain.doc_reader import DocReader
from ..settings import manager

router = APIRouter(
    prefix="/create_embeddings_from_doc",
    tags=["Generate document embeddings from text"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
    )


def create_vectors(uploaded_file: dict) -> float:
    #reader = DocReader('tec_navegacao.pdf')
    reader = DocReader(uploaded=uploaded_file)
    reader.parse_doc(autogen=True)
    reader.gen_chunks(reader.text)
    price = reader.check_price()
    chunks = reader.chunks

    manager.generate_embeddings(chunks)
    manager.vdb_insert()
    print(f"Price paid for {price[0]} tokens: USD {price[1]}")
    #del manager
    return price[1]

#@app.post('/create_embeddings_from_doc', response_class=JSONResponse) #use this on app root file
@router.post("/", response_class=JSONResponse)
async def upload(file: UploadFile = File(...)) -> JSONResponse:
    filesuffix = '.'+file.headers['content-type'].split('/')[-1]
    temp = NamedTemporaryFile(
        dir= './tmp',
        suffix=filesuffix,
        delete=False
        ) 
    try:
        try:
            contents = file.file.read()
            with temp as f:
                f.write(contents)
        except Exception as e:
            raise HTTPException(status_code=500, detail='Error on uploading the file') from e
        finally:
            file.file.close()

        # Upload the file to your S3 service using `temp.name`
        #s3_client.upload_file(temp.name, 'local', 'myfile.txt')
    except Exception as e:
        raise HTTPException(status_code=500, detail='Something went wrong') from e
    finally:
        file.file.close()

    #print(file.__dict__) # debug form data
    #print(temp.name) #tmpdipn6yce gibberish
    #print(file.headers['content-type']) #'application/pdf'

    uploaded_file = {
        "file": file,
        "temp": temp.name,
        "size": file.size,
        "type": file.headers['content-type']
    }

    create_vectors(uploaded_file)

    try:
        os.remove(str(temp.name))
        print(f"removed file {temp.name}")
    except Exception as e:
        print(e)

    return {
        "file": file.filename,
        "size": file.size,
        "msg": "Inserted into vector DB"
    }