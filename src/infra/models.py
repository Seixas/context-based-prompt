from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class Prompts(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String)
    withcontext = Column(Boolean)
    prompt = Column(String)
    ntokens = Column(Integer)
    cost = Column(Float)
