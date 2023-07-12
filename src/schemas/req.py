from pydantic import BaseModel, Field


class Prompt(BaseModel):
    """
    User prompt schema
    """
    text: str = Field(default=None, examples=["como o RNAV revolucionou os sistemas de gps?"])
    with_context: bool = Field(examples=[False])


