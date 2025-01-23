import chromadb
import pymongo


class ServerHealthCheck:
    def __init__(self) -> None:
        self.chroma_client = chromadb.HttpClient(host='localhost', port=8000)
        self.mongo_client = pymongo.MongoClient('mongodb://admin:password@localhost:27017/')
        
    def check_chroma(self)  -> bool:
        try:
            server_info = self.chroma_client.heartbeat()
            return server_info != 0
        except Exception as e:
            return str(e)
    
    def check_mongo(self) -> bool:
        try:
            server_info = self.mongo_client.server_info()
            return server_info.get('ok', 0) == 1.0
        except Exception as e:
            return str(e)