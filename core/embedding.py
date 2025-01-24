import chromadb
from chromadb.utils.embedding_functions import OllamaEmbedding
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class EmbeddingProcessor:
    def __init__(
        self, 
        collection_name: str,
        embedding_model: str = "nomic-embed-text"
    ):
        # Initialize ChromaDB client
        self.client = chromadb.HttpClient(
            host='localhost',
            port=8000,
            settings=chromadb.Settings(
                persist_directory="/chroma/data",
                is_persistent=True
            )
        )
        
        # Initialize embedding function
        self.embedding_function = OllamaEmbedding(
            model_name=embedding_model,
            url="http://localhost:11434/api/embeddings"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def process_data(self, raw_data: List[str]) -> List[str]:
        """Process raw text data for embedding"""
        processed_data = []
        for text in raw_data:
            # Basic processing - remove extra whitespace and normalize
            processed = " ".join(text.split())
            processed_data.append(processed)
        return processed_data

    def create_metadata(
        self, 
        data: List[str], 
        additional_info: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Create metadata for each document"""
        metadata = []
        for idx, text in enumerate(data):
            meta = {
                "timestamp": datetime.now().isoformat(),
                "document_id": f"doc_{idx}",
                "char_length": len(text)
            }
            if additional_info and len(additional_info) > idx:
                meta.update(additional_info[idx])
            metadata.append(meta)
        return metadata

    def add_documents(
        self,
        texts: List[str],
        ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add documents to ChromaDB with embeddings"""
        try:
            # Process the input texts
            processed_texts = self.process_data(texts)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"id_{i}" for i in range(len(processed_texts))]
            
            # Generate metadata if not provided
            if metadata is None:
                metadata = self.create_metadata(processed_texts)
            
            # Add to collection
            self.collection.add(
                documents=processed_texts,
                metadatas=metadata,
                ids=ids
            )
            
        except Exception as e:
            raise Exception(f"Error adding documents to ChromaDB: {str(e)}")

    def query_similar(
        self,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Query similar documents"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            raise Exception(f"Error querying ChromaDB: {str(e)}")