from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from ..models.rag_response_data_models import SummaryResponse, SolutionQuery
from ..models.graph_data_models import DAG

class MongoDBHandler:
    """Handler for MongoDB operations"""
    
    def __init__(
        self,
        connection_string: str = "mongodb://localhost:27017/",
        database_name: str = "graph_rca"
    ):
        try:
            self.client = MongoClient(connection_string)
            self.db: Database = self.client[database_name]
            # Verify connection
            self.client.server_info()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    def create_session(self, description: Optional[str] = None) -> str:
        """
        Create a new analysis session
        Returns: session_id
        """
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "session_id": session_id,
                "created_at": datetime.now(datetime.timezone.utc),
                "description": description,
                "status": "initialized"
            }
            
            # Create collection for this session
            self.db[f"session_{session_id}"].insert_one(session_data)
            return session_id
            
        except Exception as e:
            raise Exception(f"Failed to create session: {str(e)}")

    def get_session_collection(self, session_id: str) -> Collection:
        """Get collection for a specific session"""
        collection_name = f"session_{session_id}"
        if collection_name not in self.db.list_collection_names():
            raise ValueError(f"Session {session_id} not found")
        return self.db[collection_name]

    def store_input_logs(self, session_id: str, logs: list[Dict[str, Any]]) -> None:
        """Store input logs for a session"""
        try:
            collection = self.get_session_collection(session_id)
            collection.insert_one({
                "type": "input_logs",
                "data": logs,
                "timestamp": datetime.now(datetime.timezone.utc)
            })
        except Exception as e:
            raise Exception(f"Failed to store input logs: {str(e)}")

    def store_graph(self, session_id: str, graph: DAG) -> None:
        """Store graph representation"""
        try:
            collection = self.get_session_collection(session_id)
            collection.insert_one({
                "type": "graph",
                "data": graph.model_dump(),
                "timestamp": datetime.now(datetime.timezone.utc)
            })
        except Exception as e:
            raise Exception(f"Failed to store graph: {str(e)}")

    def store_summary(self, session_id: str, summary: SummaryResponse) -> None:
        """Store analysis summary"""
        try:
            collection = self.get_session_collection(session_id)
            collection.insert_one({
                "type": "summary",
                "data": summary.model_dump(),
                "timestamp": datetime.now(datetime.timezone.utc)
            })
        except Exception as e:
            raise Exception(f"Failed to store summary: {str(e)}")

    def store_solution(self, session_id: str, solution: str, query: SolutionQuery) -> None:
        """Store generated solution"""
        try:
            collection = self.get_session_collection(session_id)
            collection.insert_one({
                "type": "solution",
                "data": {
                    "solution_text": solution,
                    "query": query.model_dump()
                },
                "timestamp": datetime.now(datetime.timezone.utc)
            })
        except Exception as e:
            raise Exception(f"Failed to store solution: {str(e)}")

    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Retrieve all data for a session"""
        try:
            collection = self.get_session_collection(session_id)
            data = {}
            
            # Get each type of data
            for doc_type in ["input_logs", "graph", "summary", "solution"]:
                result = collection.find_one({"type": doc_type})
                if result:
                    data[doc_type] = result["data"]
            
            return data
            
        except Exception as e:
            raise Exception(f"Failed to retrieve session data: {str(e)}")

    def update_session_status(self, session_id: str, status: str) -> None:
        """Update session status"""
        try:
            collection = self.get_session_collection(session_id)
            collection.update_one(
                {"session_id": session_id},
                {"$set": {"status": status}}
            )
        except Exception as e:
            raise Exception(f"Failed to update session status: {str(e)}")

    def delete_session(self, session_id: str) -> None:
        """Delete a session and its data"""
        try:
            collection_name = f"session_{session_id}"
            if collection_name in self.db.list_collection_names():
                self.db.drop_collection(collection_name)
        except Exception as e:
            raise Exception(f"Failed to delete session: {str(e)}")

    def close(self) -> None:
        """Close MongoDB connection"""
        try:
            self.client.close()
        except Exception as e:
            raise Exception(f"Failed to close MongoDB connection: {str(e)}")