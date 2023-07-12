from .domain.emb_manager import EmbeddingsManager


manager_params = {
        "path": "./qdrant",
        "collection_name": "mycollection",
        "mode": "hdd"
    }
manager = EmbeddingsManager(**manager_params)
manager.instantiate_vector_db()
