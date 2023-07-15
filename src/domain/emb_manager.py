from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http import models
import tiktoken
from typing import List, Union
import openai
import time
import os
import uuid
from dotenv import load_dotenv, dotenv_values

# Env startup
load_dotenv()
_dotenv = dotenv_values(".env")

class EmbeddingsManager:
    def __init__(self,mode: str,
    path: str,
    collection_name: str,
    embedding_model: str=_dotenv['EMBEDDING_MODEL'],
    ) -> None:
        self.path = path
        self.mode = mode
        self.collection_name = collection_name
        self.EMBEDDING_MODEL = embedding_model

        self.openai = openai
        self.qdrant_client = None
        self.points = None

        self.openai.api_key = _dotenv['OPENAI_APIKEY']

    def instantiate_vector_db(self, autocreate: bool=False) -> None:
        if    self.mode == "localhost":
            qdrant_client = QdrantClient("localhost", port=6333)
        elif  self.mode == "memory":
            qdrant_client = QdrantClient(":memory:")
        elif  self.mode == "hdd":
            qdrant_client = QdrantClient(path=self.path) #"./qdrant"

        try:
            collection_info = qdrant_client.get_collection(collection_name=self.collection_name)
        except Exception as e:
            if not autocreate:
                raise e
            print(f'{e}\n Creating {self.collection_name} collection...')
            self.__create_collection(qdrant_client)
            collection_info = qdrant_client.get_collection(collection_name=self.collection_name)
        print(collection_info)

        self.qdrant_client = qdrant_client
        return None
        

    def __create_collection(self, client: QdrantClient) -> None:
        client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )
        return None

    def generate_embeddings(self, chunks: list[str], retry: int=20) -> list:
        #model RPM	TPM
        #text-embedding-ada-002	3000  1 000 000
        points = []
        for _id, chunk in enumerate(chunks, 1):
            print(f"Embeddings id: {_id}, chunk len: {len(chunk)}")
            for i in range(retry):
                retry_formula = (0.5*(2**i * 100))*0.001
                print(f"Retry {i} {retry_formula} milliseconds")
                time.sleep(retry_formula) if i > 0 else None # backoff strategy in milliseconds
                try:
                    response = self.openai.Embedding.create(
                        input=chunk,
                        model=self.EMBEDDING_MODEL
                    )
                    embeddings = response['data'][0]['embedding']
                    break
                except Exception as e:
                    if i >= retry:
                        raise e

            # new class for "dataframe" based on pointsctruct?
            points.append(PointStruct(id=_id, vector=embeddings, payload={"text": chunk}))
        self.points = points
        return points


    def vdb_insert(self) -> None:
        operation_info = self.qdrant_client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=self.points
        )

        print("Operation info:", operation_info)
        return None
        

    def create_answer_with_context(self, user_input: str, with_context: bool=True) -> str:
        prompt = user_input
        context_json = {}
        scores = []
        if with_context:
            response = self.openai.Embedding.create(
                input=user_input,
                model=self.EMBEDDING_MODEL
            )
            embeddings = response['data'][0]['embedding']

            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embeddings, 
                limit=5
            )

            prompt = "Contexto:\n"
            for result in search_results:
                prompt += result.payload['text'] + "\n---\n"
                scores.append(result.score)
            prompt += f"Pergunta: {user_input}\n---\nResposta:"

            #print("----PROMPT START----")
            #print(prompt)
            #print("----PROMPT END----")

            context_json = {
                "context": search_results,
                "prompt_embedding": embeddings
            }

        completion = openai.ChatCompletion.create(
            model=_dotenv['GENERATOR_MODEL'],
            messages=[
                {"role": "user", "content": prompt}
            ]
            )
        generated = completion.choices[0].message.content
        costs = self.check_price(user_input, prompt, generated)
        emb_distance = sum(scores)/len(scores) if scores else None

        return {
            "user_input": user_input,
            "with_context": with_context,
            "prompt": prompt,
            "generated": generated,
            **context_json,
            "emb_distance": emb_distance,
            "costs": costs
        }

    def num_tokens_from_string(self, string: str, encoding_name: str="cl100k_base") -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(string))

    def check_price(self, user_input:str, prompt: str, generated: str) -> dict:
        prompt_num_tokens = self.num_tokens_from_string(prompt)
        input_num_tokens = self.num_tokens_from_string(user_input)
        generated_num_tokens = self.num_tokens_from_string(generated)
        embedding_cost = input_num_tokens*.0001/1000
        #$0.0015 / 1K tokens	$0.002 / 1K tokens
        gpt_cost = (prompt_num_tokens*.00015/1000) + (generated_num_tokens*.002/1000)
        total_cost = gpt_cost+embedding_cost
        return {
            "input_num_tokens": input_num_tokens,
            "prompt_num_tokens": prompt_num_tokens,
            "embedding_cost": embedding_cost,
            "gpt_cost": gpt_cost,
            "total_cost": total_cost
        }
