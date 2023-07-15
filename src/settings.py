from .domain.emb_manager import EmbeddingsManager
from .infra.database import SessionLocal


manager_params = {
        "path": "./qdrant",
        "collection_name": "mycollection", # test collection aviation
        #"collection_name": "2023collection", # test collection with unseen data
        "mode": "hdd"
    }
manager = EmbeddingsManager(**manager_params)
manager.instantiate_vector_db(autocreate=True)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
