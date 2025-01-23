"""import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import pymongo

class VectorDatabaseHandler:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(host='localhost', port=8000)
        self.ollama_ef = embedding_functions.OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="llama2",
        )   
        
        """
        
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

client = chromadb.HttpClient(
    host='localhost', 
    port=8000,
    settings=chromadb.Settings(
        persist_directory="/chroma/data",  # Maps to Docker volume
        is_persistent=True
    )
)
# create EF with custom endpoint
ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434/api/embeddings",
)

print(ef(["Here is an article about llamas..."]))

# Create or get collection
collection = client.get_or_create_collection(
    name="my_collection",
    embedding_function=ef
)

# Add documents
collection.add(
    documents=["Here is an article about llamas..."],
    ids=["doc1"]
)

# Query the collection
results = collection.query(
    query_texts=["article about llamas"],
    n_results=1
)

print("Retrieved results:", results)