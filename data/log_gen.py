from pydantic import BaseModel, Field
import ollama
from datetime import datetime
import json
import logging
from typing import Optional
import random
import uuid
import time

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

SCENARIO_MODEL = "qwen2.5:3b"
LOG_MODEL = "qwen2.5-coder:1.5b"

class ApplicationLog(BaseModel):
    timestamp: datetime = Field(description="Timestamp of the log entry")
    pid: int = Field(description="Process ID of the application")
    level: str = Field(description="Log level")
    component: str = Field(description="Component/module generating the log")
    message: str = Field(description="Log message content")
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    error_code: Optional[int] = Field(None, description="Error code if applicable")

class Logs(BaseModel):
    log_chain: list[ApplicationLog] = Field(description="list of log entries")

class Scenario(BaseModel):
    root_cause: str = Field(description='root cause of the issue')
    effects: list[str] = Field(description='subsequent effects so that logs can be mimicked')

class ScenarioGenerator:
    def __init__(self) -> None:
        self.incident_seeds = [{
            "scenario": "Database Degradation",
            "initial_context": "Database system experiencing performance issues",
            "components": ["DatabaseMonitor", "QueryExecutor", "DatabaseManager"]
        },
        {
            "scenario": "Security Breach Attempt",
            "initial_context": "Multiple failed login attempts detected",
            "components": ["AuthService", "SecurityMonitor", "AccountManager"]
        },
        {
            "scenario": "Memory Leak",
            "initial_context": "Gradual memory consumption increase",
            "components": ["MemoryManager", "ResourceMonitor", "ApplicationServer"]
        }]
        
        self.client = ollama.Client()
        self.options = ollama.Options(temperature=0.83,seed=random.randint(0,10000))

    def generate_cause(self) -> Scenario:
        seed = random.choice(self.incident_seeds)
        
        prompt = f"""Create a JSON object with exactly two fields:
        1. "root_cause": A detailed technical description of the root cause based on this scenario: {seed['scenario']}
        2. "effects": An array of 3 specific technical effects that would result from this root cause

        Example format:
        {{
            "root_cause": "Database connection pool exhaustion due to connection leaks",
            "effects": [
                "Increasing response times in database queries",
                "Connection timeout errors in application layer",
                "Service degradation and request failures"
            ]
        }}"""

        try:
            response = self.client.generate(
                model=SCENARIO_MODEL,
                prompt=prompt,
                options=self.options
            )
            
            # Extract JSON from the response
            response_text = response.response
            # Find the first { and last } to extract valid JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                scenario_dict = json.loads(json_str)
                return Scenario(**scenario_dict)
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            logging.error(f"Error parsing scenario: {str(e)}")
            raise

class LogGenerator:
    def __init__(self):
        self.client = ollama.Client()
        self.options = ollama.Options(temperature=0.5,seed=random.randint(0,10000))

    def _generate_single_log_entry(self, context: str, level: str = None) -> ApplicationLog:
        time.sleep(0.3)
        current_time = datetime.now().isoformat()
        pid = random.randint(10000, 99999)
        trace_id = str(uuid.uuid4())
        log_level = level or random.choice(['INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        
        prompt = f"""Generate a single log entry as a valid JSON object. Use this exact format with double quotes around all keys and string values:

        {{
            "timestamp": "{current_time}",
            "pid": {pid},
            "level": "{log_level}",
            "component": "COMPONENT_NAME",
            "message": "LOG_MESSAGE",
            "trace_id": "{trace_id}",
            "error_code": null
        }}

        Replace COMPONENT_NAME with a relevant system component name and LOG_MESSAGE with a short log message based on this context: {context}"""

        try:
            response = self.client.generate(
                model=LOG_MODEL,
                prompt=prompt,
                options=self.options,
            )
            
            # Extract JSON from the response
            response_text = response.response
            # Find the first { and last } to extract valid JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                # Clean up any potential formatting issues
                json_str = json_str.replace("'", '"')  # Replace single quotes with double quotes
                json_str = json_str.strip()  # Remove any extra whitespace
                
                log_dict = json.loads(json_str)
                
                # Ensure proper types
                log_dict['timestamp'] = datetime.fromisoformat(log_dict['timestamp'].replace('Z', '+00:00'))
                log_dict['pid'] = int(log_dict['pid'])
                if 'error_code' in log_dict and log_dict['error_code']:
                    log_dict['error_code'] = int(log_dict['error_code'])
                
                return ApplicationLog(**log_dict)
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            logging.error(f"Error generating log entry: {str(e)}\nResponse was: {response.response}")
            raise
        
        
    def _generate_complete_log(self, scenario: Scenario) -> Logs:
        log_entries = []
        
        # Initial warning about the root cause
        log_entries.append(self._generate_single_log_entry(
            context=f"{scenario.root_cause}",
            level="WARNING"
        ))
        
        time.sleep(0.3)
        # Logs for each effect
        for effect in scenario.effects:
            # Info log about the effect
            log_entries.append(self._generate_single_log_entry(
                context=effect,
                level="INFO"
            ))
            
            # Error or Critical log about the impact
            log_entries.append(self._generate_single_log_entry(
                context=f"{effect}",
                level=random.choice(["ERROR", "CRITICAL"])
            ))

        return Logs(log_chain=sorted(log_entries, key=lambda x: x.timestamp))

    def validate_generated_log(self, log: Logs) -> bool:
        if not log.log_chain or len(log.log_chain) < 3:
            return False
        
        # Check timestamp sequence
        timestamps = [entry.timestamp for entry in log.log_chain]
        if not all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1)):
            return False
            
        # Check for variety in log levels
        levels = set(entry.level for entry in log.log_chain)
        if len(levels) < 2:
            return False
            
        return True

    @staticmethod
    def generate_dataset_of_logs(total_logs: int, output_file: str):
        scenario_builder = ScenarioGenerator()
        generator = LogGenerator()
        all_logs = []
        
        for i in range(total_logs):
            try:
                logging.info(f"Generating log set {i+1}/{total_logs}")
                
                time.sleep(0.3)
                
                scenario = scenario_builder.generate_cause()
                
                time.sleep(0.3)
                
                logs = generator._generate_complete_log(scenario)
                
                if generator.validate_generated_log(logs):
                    all_logs.append(logs)
                    logging.info(f"Generated valid log set {i+1}/{total_logs}")
                else:
                    logging.warning(f"Invalid log set generated, retrying {i+1}")
                    continue
                    
            except Exception as e:
                logging.error(f"Error generating log set {i+1}: {str(e)}")
                time.sleep(0.3)
                continue
        
        try:
            with open(output_file, 'w') as f:
                json_data = [log.model_dump() for log in all_logs]
                json.dump(json_data, f, indent=2, default=str)
            logging.info(f"Successfully saved {len(all_logs)} log sets to {output_file}")
        except Exception as e:
            logging.error(f"Error saving dataset: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        LogGenerator.generate_dataset_of_logs(
            total_logs=50,
            output_file="generated_logs.json"
        )
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")