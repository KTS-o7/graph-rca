# Log Analysis System API Documentation

## Overview

This documentation covers the main components and APIs of the Log Analysis System, which includes log parsing, embedding generation, vector database operations, and graph-based log analysis.

## Core Components

### 1. Embedding Creation (`core/embedding.py`)

#### EmbeddingCreator

Creates and manages text embeddings using Ollama's embedding models.

```python
creator = EmbeddingCreator()
```

Methods:

- `create_embedding(text: str) -> List[float]`: Generate embedding for single text
- `create_batch_embeddings(texts: List[str]) -> List[List[float]]`: Generate embeddings for multiple texts
- `get_similarity(embedding1: List[float], embedding2: List[float]) -> float`: Calculate cosine similarity between embeddings

### 2. Database Handlers (`core/database_handlers.py`)

#### VectorDatabaseHandler

Manages ChromaDB operations for vector similarity search.

```python
vector_db = VectorDatabaseHandler()
```

Methods:

- `get_collection(name: str = "docs")`: Get or create a ChromaDB collection
- `add_documents(documents: List[str], embeddings: List[List[float]])`: Add documents with embeddings
- `query_collection(query_texts: List[str], n_results: int = 3)`: Query similar documents
- `search(query: str, context: str, top_k: int = 5) -> list`: Semantic search with context

#### MongoDBHandler

Handles MongoDB operations for storing DAGs and context.

```python
mongo_db = MongoDBHandler()
```

Methods:

- `save_dag(dag_data: dict)`: Save DAG to MongoDB
- `get_context(dag_id: str = None)`: Retrieve context by DAG ID
- `save_context(context_data: dict)`: Save context data

### 3. Log Analysis (`utilz/`)

#### LogParser (`utilz/log_parser.py`)

Parses log entries using LLM-based extraction.

```python
parser = LogParser(model="llama3.2:3b")
```

Methods:

- `parse_log_from_file(log_file: str) -> LogChain`: Parse logs from file
- `parse_log(log_data: str) -> LogChain`: Parse logs from string
- `extract_log_info_by_llm(log_entry: str) -> LogEntry`: Extract structured info from log entry

#### GraphGenerator (`utilz/graph_generator.py`)

Generates DAG from parsed log entries.

```python
generator = GraphGenerator(log_chain)
```

Methods:

- `generate_dag() -> DAG`: Generate DAG from log chain
- `find_root_cause() -> str`: Identify root cause from DAG

#### ContextBuilder (`utilz/context_builder.py`)

Builds context from DAG for analysis.

```python
builder = ContextBuilder()
```

Methods:

- `build_context(dag: DAG) -> Context`: Generate context from DAG

### 4. Health Monitoring (`utilz/database_healthcheck.py`)

#### ServerHealthCheck

Monitors database connections.

```python
health = ServerHealthCheck()
```

Methods:

- `check_chroma() -> bool`: Check ChromaDB connection
- `check_mongo() -> bool`: Check MongoDB connection

## Data Models

### Parsing Models (`models/parsing_data_models.py`)

- `LogEntry`: Complete log entry information
- `LogChain`: Collection of log entries
- `BaseLogEntry`: Common log entry fields
- `SystemInfo`: System-level information
- `UserInfo`: User-related information
- `TraceInfo`: Tracing information

### Graph Models (`models/graph_data_models.py`)

- `DAGNode`: Node in the Directed Acyclic Graph
- `DAG`: Complete graph structure

### Context Models (`models/context_data_models.py`)

- `Context`: Context information from log analysis
- `Solution`: Solution response with sources

### RAG Response Models (`models/rag_response_data_models.py`)

- `SummaryResponse`: Summary of log analysis
- `SolutionQuery`: Query and response structure

## Usage Examples

### Parse Logs and Generate DAG

```python
# Initialize parser
parser = LogParser()

# Parse logs
log_chain = parser.parse_log_from_file("app.log")

# Generate DAG
generator = GraphGenerator(log_chain)
dag = generator.generate_dag()

# Build context
context_builder = ContextBuilder()
context = context_builder.build_context(dag)
```

### Vector Search

```python
# Initialize vector DB
vector_db = VectorDatabaseHandler()

# Add documents
vector_db.add_documents(documents, embeddings)

# Search
results = vector_db.search(
    query="error in authentication",
    context="user login flow",
    top_k=5
)
```

### Health Check

```python
health = ServerHealthCheck()
chroma_status = health.check_chroma()
mongo_status = health.check_mongo()
```

## Error Handling

All components include comprehensive error handling and logging. Common exceptions:

- `ValueError`: Invalid input parameters
- `RuntimeError`: Operation execution failures
- Database connection errors
- LLM processing errors

## Dependencies

- ChromaDB
- MongoDB
- Ollama
- Pydantic
- Streamlit (for health monitoring UI)
