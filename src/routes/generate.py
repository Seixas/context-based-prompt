from fastapi import Depends, Request, APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from starlette.responses import JSONResponse
from tempfile import NamedTemporaryFile

from ..schemas import req, res
from ..settings import manager

router = APIRouter(
    prefix="/generate",
    tags=["Generate response"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
    )


#@app.post("/generate", response_class=JSONResponse) #use this on app root file
@router.post("/", response_class=JSONResponse)
async def generate(prompt: req.Prompt) -> JSONResponse:
    print(prompt)
    return manager.create_answer_with_context(prompt.text, prompt.with_context)