from fastapi import Depends, Request, APIRouter, HTTPException
from starlette.responses import JSONResponse

from ..infra import models
from sqlalchemy.orm import Session

from ..settings import get_db


router = APIRouter(
    prefix="/prompts",
    tags=["Query past prompts"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
    )


@router.get("/{prompt_id}", response_class=JSONResponse)
def read_prompt(prompt_id: int, db: Session = Depends(get_db)):
    return db.query(models.Prompts).filter(models.Prompts.id == prompt_id).one_or_none()
