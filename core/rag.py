import mirascope

# this is basically our rag model

class Rag:
    def generate_response(self, question: str, context: str) -> str:
        # this will generate the response
        pass
    
    def get_context(self, question: str) -> str:
        # this will get the context
        pass
    
    def append_context(self, context: str) -> None:
        # this will append the context
        pass
    
    def update_context(self, context: str) -> None:
        # this will update the context
        pass
    
    def delete_context(self, context: str) -> None:
        # this will delete the context
        pass
    
    def get_root_causes(self, question: str) -> list:
        # this will get the root causes
        pass
    
    def find_similar_solution(self, question: str) -> str:
        # this will find the similar solution
        pass
    
    # feel free to rename and add more methods as required