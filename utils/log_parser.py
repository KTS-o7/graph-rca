import ollama
from datetime import datetime
from ..models.parsing_data_models import LogEntry, LogChain

LLAMA = "llama3.2:3b"
QWEN = "qwen2.5-coder:3b"

class LogParser:
    def __init__(self,model:str="llama3.2:3b"):
        try:
            self.model = model
            self.ollama_client = ollama.Client()
            self.ollama_options = ollama.Options(temperature=0.2)
            self.system_prompt = f"You are an expert in log parsing. You are given a log entry and a pydantic model. Extract and fill the fields of the model with the information from the log entry."
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LogParser: {str(e)}")
        
    def extract_log_info_by_llm(self,log_entry:str) -> LogEntry:
        """Extract log information using the specified language model"""
        try:
            user_prompt = f"""Extract the information from the following log entry : \n{log_entry}\n
             Important instruction : DONOT include a field if the information is not present in the log entry.
            
            Mandatory fields: timestamp, message, level
            Optional fields: pid, component, error_code, username, ip_address, group, trace_id, request_id
            """
            
            response = self.ollama_client.generate(model=self.model,system=self.system_prompt,user=user_prompt,options=self.ollama_options,format=LogEntry)
            
            if not response or not response.response:
                raise ValueError("Empty response from language model")
                
            return response.response
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract log info: {str(e)}")
        
    def parse_log_from_file(self,log_file:str)->LogChain:
        """Parse log entries from a log file. Must accept only .txt, .log, .out, .err files"""
        try:
            if not log_file.endswith((".txt",".log",".out",".err")):
                raise ValueError("Only .txt, .log, .out, .err files are supported")
            
            with open(log_file,"r") as f:
                log_data = f.read()
            return self.parse_log(log_data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {log_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse log file: {str(e)}")
    
    def parse_log(self,log_data:str)->LogChain:
        """Parse log entries from a string"""
        try:
            if not log_data:
                raise ValueError("Empty log data provided")
                
            log_data_split = log_data.split("\n")
            log_entries = []
            
            for log in log_data_split:
                if log:
                    try:
                        log_entries.append(self.extract_log_info_by_llm(log))
                    except Exception as e:
                        print(f"Warning: Failed to parse log entry '{log}': {str(e)}")
                        continue
            
            if not log_entries:
                raise ValueError("No valid log entries found")
                
            return LogChain(log_chain=log_entries)
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse log data: {str(e)}")