from src.domain.doc_reader import DocReader
from src.domain.emb_manager import EmbeddingsManager
import argparse

# Initialize the parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("--db", help = "Vector db", default="qdrant")
parser.add_argument("--collection", help = "Vector DB collection", default="mycollection")
parser.add_argument("--create_embeddings", help = "Creation of embeddings", default=False)
parser.add_argument("--document", help = "Document name", default="tec_navegacao.pdf")
parser.add_argument("--prompt", help = "User input", default="")
 
# Read arguments from command line
ARGS = parser.parse_args()

def create_vectors() -> float:
    reader = DocReader('tec_navegacao.pdf')
    reader.parse_doc(autogen=True)
    ##reader.gen_chunks(reader.text)
    price = reader.check_price()
    chunks = reader.chunks

    manager = EmbeddingsManager(path="./qdrant",
            collection_name="mycollection", mode='hdd')
    print(manager.EMBEDDING_MODEL)
    manager.instantiate_vector_db()
    #manager.generate_embeddings(chunks)
    #manager.vdb_insert()
    print(f"Price paid in USD for {price[0]} tokens: {price[1]}")
    del manager
    return price[1]


def generate(user_input: str) -> str:
    handler = EmbeddingsManager(path="./qdrant",
            collection_name="mycollection", mode='hdd')
    handler.instantiate_vector_db()
    return handler.create_answer_with_context(user_input)


result = create_vectors() if ARGS.create_embeddings else generate(ARGS.prompt)
print(result)
