from .domain.emb_manager import EmbeddingsManager
from .infra.database import SessionLocal


manager_params = {
        "path": "./qdrant",
        "collection_name": "mycollection",
        "mode": "hdd"
    }
manager = EmbeddingsManager(**manager_params)
manager.instantiate_vector_db()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
