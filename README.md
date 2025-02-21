# Log Analysis & Incident Resolution System

This application provides automated log analysis and incident resolution using AI. It processes log files, generates insights, and provides solutions based on your documentation.

## Features

- 📊 Automated log file analysis
- 🔍 Root cause identification
- 📝 Documentation integration for context-aware solutions
- 🤖 AI-powered incident resolution
- 📈 Causal chain visualization
- 🗄️ Persistent storage of analysis results

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (optional, for better performance)
- Python 3.8+

## Installation

1. Clone the repository:

```bash
git clone https://github.com/KTS-o7/graph-rca.git
cd graph-rca
```

2. Create a Python virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the required services using Docker Compose:

```bash
docker-compose up -d
```

This will start:

- ChromaDB (Vector Database) on port 8000
- MongoDB on port 27017
- Ollama (Local LLM) on port 11435

2. Check available Ollama models:

```bash
docker exec -it $(docker ps -qf "name=ollama") ollama list
```

3. Install the ollama model:

```bash
docker exec -it $(docker ps -qf "name=ollama") ollama pull llama3.2:3b
```

4. Run the Streamlit application:

```bash
streamlit run frontend/app.py
```

The application will be available at `http://localhost:8501`

## Usage

1. **Upload Log File**

   - Click on "Upload Log File" expander
   - Select your log file (.log or .txt)
   - The system will automatically analyze the log and display a summary

2. **Add Documentation**

   - Click on "Add Documentation" expander
   - Upload relevant documentation files (.txt or .md)
   - These documents will be used as context for generating solutions

3. **Get Automated Solutions**
   - Once both log and documentation are processed
   - The system will automatically generate solutions based on the analysis
   - View root cause analysis and recommended solutions

## Environment Variables

The following environment variables can be configured in the `docker-compose.yaml`:

```yaml
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password
```

## Troubleshooting

- If the GPU is not detected, ensure NVIDIA drivers and CUDA are properly installed
- For database connection issues, verify that all Docker containers are running:
  ```bash
  docker-compose ps
  ```
- Check container logs for specific issues:
  ```bash
  docker-compose logs <service-name>
  ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
