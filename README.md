# Q&A with context provided using qdrant

We will use `qdrant` as our Vector DB on this example, an open-source vector similarity search engine, OpenAI `ada002` embeddings model to build our
document embeddings and a middleman to user input data, FastAPI to simulate this process as an API.

## What is a Vector DB?

A vector database is a type of database that stores data as high-dimensional vectors, which are mathematical representations of features or attributes. 
Each vector has a certain number of dimensions, which can range from tens to thousands, depending on the complexity and granularity of the data. 
It makes it useful for all sorts of neural network or semantic-based matching, faceted search, and other applications.

Qdrant [GitHub](https://github.com/qdrant/qdrant) and [Docs](https://qdrant.tech/documentation/quick-start/).  
OpenAI [Docs](https://platform.openai.com/docs/api-reference).  

The process:
1. Create a vector DB
2. extract text from documents (e.g. .pdf, .txt, .docx) and create embeddings
3. use vector DB to index the embeddings
4. use vector DB to search for the most similar embeddings based on a user input
5. Enhance a prompt concatenating the results of most similar embeddings as context to a user input
6. Generate a response based on the enhanded prompt

## How to setup
```sh
conda env create -f environment.yml
```
```sh
conda activate llm-base
```  
or
```sh
conda create -n llm-base python=3.9 
```  
```sh
pip install -r requirements.txt
```  

To create your own requirements:  
```sh
pip3 list --format=freeze > requirements.txt
```  
```sh
conda env export > environment.yml --no-builds
```  
  
Change OPENAI_APIKEY on `.env_example` to yours and rename that file to `.env`  

## How to run (locally)
```sh
uvicorn api:app --host localhost --port 8000 --reload
```

## How to use (locally)
Go to FastAPI swagger on [localhost](http://localhost:8000/docs)
