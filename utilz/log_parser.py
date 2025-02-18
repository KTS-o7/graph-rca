import ollama
from datetime import datetime
from models.parsing_data_models import LogEntry, LogChain

LLAMA = "llama3.2:3b"
QWEN = "qwen2.5-coder:3b"

class LogParser:
    def __init__(self,model:str="llama3.2:3b"):
        try:
            self.model = model
            self.ollama_client = ollama.Client(host='http://localhost:11435')
            self.ollama_options = ollama.Options(temperature=0.2)
            self.system_prompt = f"You are an expert in log parsing. You are given a log entry and a pydantic model. Extract and fill the fields of the model with the information from the log entry."
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LogParser: {str(e)}")
        
    def extract_log_info_by_llm(self, log_entry: str) -> LogEntry:
        """Extract log information using the specified language model"""
        try:
            user_prompt = f"""Parse this log entry into JSON format:
            {log_entry}
            
            Required fields:
            - timestamp (ISO 8601 format)
            - message (original log message)
            - level (log severity level)
            
            Optional fields (include ONLY if present):
            - pid (process ID as string)
            - component (source component/module)
            - error_code (error code as string)
            - username
            - ip_address
            - group
            - trace_id
            - request_id
            
            Return empty strings for missing fields. Maintain original case for field values.
            """
            
            response = self.ollama_client.generate(
                model=self.model,
                prompt=user_prompt,
                system=self.system_prompt,
                options=self.ollama_options,
                format="json"
            )

            print(f"Raw LLM response: {response.response}")  # Debug JSON output
            
            # Handle empty responses
            if not response or not response.response.strip():
                raise ValueError("Empty response from language model")
                
            try:
                # Parse and validate the JSON response
                parsed = LogEntry.model_validate_json(response.response)
                
                # Validate mandatory fields
                if not all([parsed.timestamp, parsed.message, parsed.level]):
                    raise ValueError("Missing required fields in parsed entry")
                    
                return parsed
                
            except Exception as e:
                print(f"JSON validation error: {e}")
                print(f"Problematic JSON: {response.response}")
                raise

        except Exception as e:
            raise RuntimeError(f"Failed to extract log info: {str(e)}")
        
    def parse_log_from_file(self, log_file: str) -> LogChain:
        """Parse log entries from a log file. Must accept only .txt, .log, .out, .err files"""
        try:
            # Remove file extension check since Streamlit already filters uploads
            # if not log_file.endswith((".txt",".log",".out",".err")):
            #     raise ValueError("Only .txt, .log, .out, .err files are supported")
            
            with open(log_file,"r") as f:
                log_data = f.read()
            return self.parse_log(log_data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {log_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse log file: {str(e)}")
    
    def parse_log(self, log_data: str) -> LogChain:
        """Parse log entries from a string using LLM"""
        try:
            if not log_data:
                raise ValueError("Empty log data provided")
                
            log_data_split = log_data.split("\n")
            log_entries = []
            
            print(f"Processing {len(log_data_split)} log lines")

            for idx, log in enumerate(log_data_split):
                if not log.strip():
                    print(f"Skipping empty line {idx+1}")
                    continue
                    
                try:
                    print(f"\n--- Processing line {idx+1} ---")
                    print(f"Original log: {log}")
                    entry = self.extract_log_info_by_llm(log)
                    print(f"Parsed entry: {entry.model_dump_json(indent=2)}")
                    # Store even partial entries for analysis
                    log_entries.append(entry)
                    
                except Exception as e:
                    print(f"Error processing line {idx+1}: {str(e)}")
                    continue
            
            if not log_entries:
                raise ValueError("No valid log entries found after LLM processing")
                
            return LogChain(log_chain=log_entries)
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse log data: {str(e)}")

"""# Remove the test code at the bottom of the file and create a proper test
def test_parser():
    parser = LogParser()
    test_logs = [
        "2023-10-12T14:23:00Z INFO [pid=1234] [component=auth] User login successful",
        "2023-10-12T14:25:30Z ERROR [error_code=500] Database connection failed",
        "2023-10-12T14:26:45Z WARN [trace_id=abc123] High latency detected"
    ]
    
    for log in test_logs:
        try:
            entry = parser.extract_log_info_by_llm(log)
            print(f"Successfully parsed:\n{entry.model_dump_json(indent=2)}")
        except Exception as e:
            print(f"Failed to parse '{log}': {str(e)}")

if __name__ == "__main__":
    test_parser()"""