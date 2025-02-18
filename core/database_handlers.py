import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import pymongo
from pymongo import MongoClient
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    text: str
    metadata: dict

class VectorDatabaseHandler:
    def __init__(self):
        try:
            print("Initializing VectorDatabaseHandler...")
            self.client = chromadb.HttpClient(
                host='localhost', 
                port=8000,
                settings=chromadb.Settings(
                    persist_directory="/chroma/data",
                    is_persistent=True
                )
            )
            print("ChromaDB client initialized")
            
            # Test connection
            try:
                self.client.heartbeat()
                print("ChromaDB connection successful")
            except Exception as e:
                print(f"ChromaDB connection failed: {str(e)}")
                raise
                
            self.ef = OllamaEmbeddingFunction(
                model_name="nomic-embed-text",
                url="http://localhost:11435/api/embeddings",
            )
            print("Embedding function initialized")
            
        except Exception as e:
            print(f"Error initializing VectorDB: {str(e)}")
            import traceback
            print(f"Full initialization error: {traceback.format_exc()}")
            raise
    
    def get_collection(self, name: str = "docs"):
        try:
            print(f"Getting collection: {name}")
            collection = self.client.get_or_create_collection(
                name=name,
                embedding_function=self.ef
            )
            print(f"Collection info: {collection.count()} documents")
            return collection
        except Exception as e:
            print(f"Error getting collection: {str(e)}")
            import traceback
            print(f"Collection error traceback: {traceback.format_exc()}")
            return None
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]]):
        collection = self.get_collection()
        # Generate unique ID for each document chunk
        ids = [str(hash(doc)) for doc in documents]  # Now using the actual chunks
        
        collection.add(
            documents=documents,  # Should be the chunks not original docs
            ids=ids,
            embeddings=embeddings
        )
    
    def query_collection(self, query_texts: List[str], n_results: int = 3):
        collection = self.get_collection()
        return collection.query(
            query_texts=query_texts,
            n_results=n_results
        )

    def search(self, query: str, context: str, top_k: int = 5) -> list:
        """Search implementation using text query"""
        try:
            print("\n=== Starting Vector Search ===")
            collection = self.get_collection()
            print(f"Debug - Collection: {collection}")
            
            if not collection:
                print("Debug - No collection found")
                return [Document(text="No documentation available", metadata={"source": "system"})]

            query_text = f"{query}\nContext: {context}"
            print(f"Debug - Query text: {query_text}")
            
            try:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                    include=["documents", "metadatas"]
                )
                print(f"Debug - Raw results type: {type(results)}")
                print(f"Debug - Raw results keys: {results.keys() if hasattr(results, 'keys') else 'No keys'}")
                print(f"Debug - Raw results: {results}")
            except Exception as e:
                print(f"Query execution error: {str(e)}")
                import traceback
                print(f"Query error traceback: {traceback.format_exc()}")
                return [Document(text=f"Error executing query: {str(e)}", metadata={"source": "error"})]
            
            if not results:
                print("Debug - No results returned")
                return [Document(text="No relevant documentation found", metadata={"source": "system"})]
            
            if not isinstance(results, dict):
                print(f"Debug - Unexpected results type: {type(results)}")
                return [Document(text="Unexpected query result format", metadata={"source": "error"})]
            
            if "documents" not in results:
                print("Debug - No documents in results")
                return [Document(text="No documents found in results", metadata={"source": "system"})]
            
            if not results["documents"] or not results["documents"][0]:
                print("Debug - Empty documents list")
                return [Document(text="Empty documents list", metadata={"source": "system"})]

            print(f"Debug - Documents: {results['documents']}")
            print(f"Debug - Metadatas: {results.get('metadatas', [])}")

            return [
                Document(
                    text=doc,
                    metadata=meta if meta else {"source": "unknown"}
                ) for doc, meta in zip(
                    results["documents"][0],
                    results.get("metadatas", [[{"source": "unknown"}]])[0]
                )
            ]
        except Exception as e:
            print(f"Search error: {str(e)}")
            import traceback
            print(f"Debug - Full traceback: {traceback.format_exc()}")
            return [Document(text=f"Error searching documentation: {str(e)}", metadata={"source": "error"})]

class MongoDBHandler:
    def __init__(self):
        self.client = MongoClient('mongodb://admin:password@localhost:27017/')
        self.db = self.client["log_analysis"]
    
    def save_dag(self, dag_data: dict):
        return self.db["dags"].insert_one(dag_data)
    
    def get_context(self, dag_id: str = None):
        """Retrieve context by DAG ID or latest if not specified"""
        if dag_id:
            return self.db["contexts"].find_one({"dag_id": dag_id})
        return self.db["contexts"].find_one(sort=[('timestamp', -1)])
    
    def save_context(self, context_data: dict):
        return self.db["contexts"].insert_one(context_data)