from fastapi import Depends, Request, APIRouter, HTTPException
from starlette.responses import JSONResponse

from ..schemas import req
from ..settings import manager

from ..infra import models
from sqlalchemy.orm import Session

from ..settings import get_db


router = APIRouter(
    prefix="/generate",
    tags=["Generate response"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
    )


@router.post("/", response_class=JSONResponse)
async def generate(prompt: req.Prompt, db: Session = Depends(get_db)) -> JSONResponse:
    print(prompt)

    result = manager.create_answer_with_context(prompt.text, prompt.with_context)

    prompt_model = models.Prompts()
    prompt_model.author = 'root'
    prompt_model.withcontext = result['with_context']
    prompt_model.prompt = result['user_input']
    prompt_model.ntokens = result['costs']['prompt_num_tokens']
    prompt_model.cost = result['costs']['total_cost']
    prompt_model.emb_distance = result['emb_distance']

    db.add(prompt_model)
    db.commit()

    return result
