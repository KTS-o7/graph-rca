import mirascope

# import needed embedding logic
# use bert or any other embedding models via ollama or mirascope

class EmbeddingCreator:
    def show_model(self, model_name: str):
        # this will show the model
        pass
    
    def create_embedding(self, text: str, model_name: str) -> list:
        # this will create the embedding of the text
        pass
    def create_embedding_from_file(self, file_path: str, model_name: str) -> list:
        # this will create the embedding of the text from the file
        pass
    
    def create_similarity(self, text1: str, text2: str, model_name: str) -> float:
        # this will create the similarity between two texts
        pass
    
    def create_similarity_from_file(self, file_path1: str, file_path2: str, model_name: str) -> float:
        
        # this will create the similarity between two texts from the file
        pass

# feel free to rename and add more methods as required