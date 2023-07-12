from multiprocessing import cpu_count
from typing import Union
import time

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import req
from src.routes import emb_create, generate
from src.settings import manager

from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

import logging
from utils import CustomFormatter

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

#logger.debug("debug message")
#logger.info("info message")
#logger.warning("warning message")
#logger.error("error message")
#logger.critical("critical message")


# Worker Options
#number_of_workers = number_of_cores x num_of_threads_per_core + 1
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

description = """
addContextAPP API helps you do awesome stuff. 🚀

## Text

You will be able to:

* **Add document embeedings to a Vector DB**.
* **Add Context to user prompts using Vector DB similarities**.
"""

app = FastAPI(
    title="addContextAPP",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Seixas",
        "url": "https://www.linkedin.com/in/seixasdev/",
        "email": "__@gmail.com",
    },
    license_info={
        "name": "Copyright (C) Seixas",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

origins = [
    "http://localhost",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@cache()
async def get_cache():
    return 1


@app.get("/")
@cache(expire=60)
async def index() -> dict:
    return dict(hello="world")


@app.on_event("startup")
async def startup():
    FastAPICache.init(manager, prefix="fastapi-cache")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/healthcheck", status_code=200)
async def healthcheck() -> str:
    return "Good to go!"


app.include_router(generate.router)
app.include_router(emb_create.router)
