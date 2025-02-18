import mirascope
import ollama
from typing import List
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# import needed embedding logic
# use bert or any other embedding models via ollama or mirascope

class EmbeddingCreator:
    def __init__(self):
        self.ef = OllamaEmbeddingFunction(
            url="http://localhost:11435/api/embeddings",
            model_name="nomic-embed-text"
        )
    
    def show_model(self, model_name: str):
        # this will show the model
        pass
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        return self.ef([text])[0]
    
    def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        # Add input validation
        if not texts:
            raise ValueError("Cannot embed empty texts list")
        
        if any(not isinstance(t, str) or len(t.strip()) == 0 for t in texts):
            raise ValueError("Text list contains empty or non-string values")
        
        try:
            return self.ef(texts)
        except Exception as e:
            # Add error logging
            print(f"Embedding generation failed: {str(e)}")
            raise
    
    def get_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        dot_product = sum(a*b for a, b in zip(embedding1, embedding2))
        norm_a = sum(a**2 for a in embedding1) ** 0.5
        norm_b = sum(b**2 for b in embedding2) ** 0.5
        return dot_product / (norm_a * norm_b)
    
    def create_embedding_from_file(self, file_path: str, model_name: str) -> list:
        # this will create the embedding of the text from the file
        pass
    
    def create_similarity(self, text1: str, text2: str, model_name: str) -> float:
        # this will create the similarity between two texts
        pass
    
    def create_similarity_from_file(self, file_path1: str, file_path2: str, model_name: str) -> float:
        # this will create the similarity between two texts from the file
        pass