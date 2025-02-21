from typing import List, Dict
from mirascope.core import openai
from mirascope.core.openai import OpenAICallParams
from openai import OpenAI
from models.rag_response_data_models import SummaryResponse, SolutionQuery
from .embedding import EmbeddingCreator
from core.database_handlers import VectorDatabaseHandler, MongoDBHandler
import ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class RAG_Engine:
    def __init__(self):
        self.embedder = EmbeddingCreator()
        self.vector_db = VectorDatabaseHandler()
        self.mongo_db = MongoDBHandler()
        self.ollama_client = ollama.Client(host="http://localhost:11435")
    
    def generate_summary(self, context: List[str]) -> SummaryResponse:
        """Generate summary using LLM"""
        response = self.ollama_client.generate(
            model="llama3.2:3b",
            prompt=f"Summarize this log context and identify root cause:\n{'\n'.join(context)}",
            options={"temperature": 0.2}
        )
        return SummaryResponse(
            summary=response['response'].split("\n"),
            root_cause_expln="Identified via log analysis",
            severity="High"
        )
    
    def generate_solution(self, context: str, root_cause: str) -> SolutionQuery:
        """Generate solution using RAG with automatic query"""
        print("\n=== Starting Solution Generation ===")
        automated_query = f"Provide resolution steps for: {root_cause}"
        print(f"Debug - Query: {automated_query}")
        print(f"Debug - Root cause: {root_cause}")
        
        try:
            # Ensure context is a string
            if not isinstance(context, str):
                if isinstance(context, (list, tuple)):
                    context_str = "\n".join(map(str, context))
                else:
                    context_str = str(context)
            else:
                context_str = context
            
            print(f"Debug - Context type after conversion: {type(context_str)}")
            print(f"Debug - Context preview: {context_str[:100]}...")
            
            # Search documentation using context embeddings
            try:
                print("\n=== Starting Vector Search ===")
                results = self.vector_db.search(
                    query=automated_query,
                    context=context_str,
                    top_k=5
                )
                print(f"Debug - Search results: {results}")
                
            except Exception as e:
                print(f"Vector search error: {str(e)}")
                results = [Document(
                    page_content="Error searching documentation",
                    metadata={"source": "error"}
                )]
            
            # Format context for prompt
            doc_context = "\n".join([doc.page_content for doc in results])
            print(f"\nDebug - Formatted doc context: {doc_context[:200]}...")
            
            try:
                print("\n=== Starting LLM Generation ===")
                # Format response with sources
                llm_response = self.ollama_client.generate(
                    model="llama3.2:3b",
                    prompt=f"""Based on the following information, provide a structured solution:

Root Cause:
{root_cause}

Context:
{context_str}

Available Documentation:
{doc_context}

Please provide a detailed solution in the following format:

Problem Analysis:
- Briefly describe the identified issue
- Key observations from the context

Recommended Steps:
1. First step with explanation
2. Second step with explanation
3. Additional steps as needed

Additional Recommendations:
- Important considerations
- Preventive measures
- Monitoring suggestions

Please be specific and actionable in your recommendations.""",
                    options={"temperature": 0.1}
                )
                print(f"Debug - LLM response: {llm_response}")
                
            except Exception as e:
                print(f"LLM generation error: {str(e)}")
                return SolutionQuery(
                    context=context_str,
                    query=automated_query,
                    response="Error: Unable to generate solution from LLM",
                    sources=[doc.metadata.get("source", "Unknown") for doc in results]
                )
            
            if not llm_response or 'response' not in llm_response:
                return SolutionQuery(
                    context=context_str,
                    query=automated_query,
                    response="Error: No response received from LLM",
                    sources=[doc.metadata.get("source", "Unknown") for doc in results]
                )
            
            return SolutionQuery(
                context=context_str,
                query=automated_query,
                response=llm_response['response'],
                sources=[doc.metadata.get("source", "Unknown") for doc in results]
            )
            
        except Exception as e:
            print(f"Error in generate_solution: {str(e)}")
            error_context = str(context) if isinstance(context, str) else "\n".join(map(str, context)) if isinstance(context, (list, tuple)) else str(context)
            return SolutionQuery(
                context=error_context,
                query=automated_query,
                response=f"Error generating solution: {str(e)}",
                sources=[]
            )
    
    def store_documentation(self, documents: List[str]) -> None:
        """Store documentation in ChromaDB"""
        print("\n=== Storing Documentation ===")
        
        # Add validation for empty documents
        if not documents:
            raise ValueError("Received empty documents list")
        
        # Add chunk size validation
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            add_start_index=True,
        )
        
        print(f"Original documents: {len(documents)} chunks")
        chunks = text_splitter.split_text("\n\n".join(documents))
        print(f"Split into {len(chunks)} chunks")
        
        # Validate chunks before embedding
        if not chunks:
            raise ValueError("No text chunks created after splitting")
        
        print("Creating embeddings...")
        embeddings = self.embedder.create_batch_embeddings(chunks)
        print(f"Created {len(embeddings)} embeddings")
        
        print("Storing in vector database...")
        self.vector_db.add_documents(
            documents=chunks,
            embeddings=embeddings
        )
        
        # Verify storage
        collection = self.vector_db.get_collection()
        print(f"Collection now contains {collection.count()} documents")