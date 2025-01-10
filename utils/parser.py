import re
from datetime import datetime
import json
from typing import Optional, Dict, Any

class LogParser:
    def __init__(self):
        self.timestamp_patterns = [
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)', '%Y-%m-%dT%H:%M:%S'),
            (r'\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}\s[+-]\d{4})\]', '%d/%b/%Y:%H:%M:%S %z'),
            (r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
            (r'(\d{2}/[A-Za-z]{3}/\d{4}\s+\d{2}:\d{2}\s+[AP]M)', '%d/%b/%Y %I:%M %p')
        ]

    def parse_log_type(self, log_line: str) -> str:
        # System and Service Logs
        if 'kernel[' in log_line or 'kernel:' in log_line:
            return 'kernel'
        elif 'sshd[' in log_line:
            return 'sshd'
        elif 'CRON[' in log_line:
            return 'cron'
        elif 'systemd[' in log_line:
            return 'systemd'
        elif 'NetworkManager[' in log_line:
            return 'networkmanager'
        elif 'wpa_supplicant[' in log_line:
            return 'wpa_supplicant'
        # Web Server Logs
        elif 'W3SVC' in log_line:
            return 'iis'
        elif '[MY-SQL]' in log_line:
            return 'mysql'
        elif 'nginx' in log_line.lower():
            return 'nginx'
        elif any(x in log_line for x in ['HTTP/1.1', 'HTTP/2']):
            return 'http'
        # Application Logs
        elif '[Note]' in log_line or '[Warning]' in log_line or '[Error]' in log_line:
            return 'database'
        elif re.search(r'\b(error|warn|info|debug)\b', log_line, re.IGNORECASE):
            return 'application'
        # Security Logs
        elif 'firewall' in log_line.lower():
            return 'firewall'
        return 'unknown'

    def parse_timestamp(self, log_line: str) -> Optional[str]:
        # First check if timestamp is already in ISO format
        iso_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', log_line)
        if iso_match:
            return iso_match.group(0)

        current_year = datetime.now().year
        
        for pattern, time_format in self.timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    if 'AM' in timestamp_str or 'PM' in timestamp_str:
                        dt = datetime.strptime(timestamp_str, time_format)
                    elif time_format == '%b %d %H:%M:%S':
                        dt = datetime.strptime(f"{current_year} {timestamp_str}", '%Y %b %d %H:%M:%S')
                    else:
                        dt = datetime.strptime(timestamp_str, time_format)
                    return dt.isoformat()
                except ValueError:
                    continue
        return None

    def parse_system_log(self, log_line: str) -> Dict[str, Any]:
        result = {}
        
        # Extract hostname and program info
        system_match = re.search(r'^([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^[\s]+)(?:\[(\d+)\])?:', log_line)
        if system_match:
            result.update({
                'hostname': system_match.group(2),
                'program': system_match.group(3)
            })
            if system_match.group(4):
                result['pid'] = int(system_match.group(4))

        # Extract network interface
        interface_match = re.search(r'(\w+\d+):', log_line)
        if interface_match:
            result['interface'] = interface_match.group(1)

        # Extract MAC addresses
        mac_match = re.search(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', log_line)
        if mac_match:
            result['mac_address'] = mac_match.group(0)

        # Extract status and state information
        status_match = re.search(r'status[=:](\d+)', log_line)
        if status_match:
            result['status'] = int(status_match.group(1))

        # Extract user information
        user_match = re.search(r"(?:user|for user)\s+'([^']+)'", log_line)
        if user_match:
            result['user'] = user_match.group(1)

        # Extract IP addresses
        ip_match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', log_line)
        if ip_match:
            result['ip_address'] = ip_match.group(1)

        # Extract kernel-specific information
        if 'kernel' in log_line:
            kernel_time_match = re.search(r'\[\s*(\d+\.\d+)\]', log_line)
            if kernel_time_match:
                result['kernel_time'] = float(kernel_time_match.group(1))

        # Extract message content
        message_start = log_line.find(']:') + 2 if ']:' in log_line else 0
        if message_start:
            result['message'] = log_line[message_start:].strip()

        return result

    def parse_web_log(self, log_line: str) -> Dict[str, Any]:
        result = {}
        
        # Parse HTTP method, path, status, and size
        http_match = re.search(r'"(GET|POST|PUT|DELETE)\s+([^\s]+)\s+HTTP/[^"]+"\s+(\d+)\s+(\d+)', log_line)
        if http_match:
            result.update({
                'method': http_match.group(1),
                'path': http_match.group(2),
                'status_code': int(http_match.group(3)),
                'response_size': int(http_match.group(4))
            })
        else:
            # Try parsing W3SVC format
            w3svc_match = re.search(r'(\S+)\s+(\d{2}/\w+/\d{4}\s+\d{2}:\d{2}:\d{2})\s+(GET|POST|PUT|DELETE)\s+([^\s]+)\s+(\d+)\s+(\d+)', log_line)
            if w3svc_match:
                result.update({
                    'server': w3svc_match.group(1),
                    'method': w3svc_match.group(3),
                    'path': w3svc_match.group(4),
                    'status_code': int(w3svc_match.group(5)),
                    'response_size': int(w3svc_match.group(6))
                })

        # Extract response time if present
        time_match = re.search(r'response_time[=:](\d+)ms', log_line)
        if time_match:
            result['response_time'] = int(time_match.group(1))

        return result

    def parse_application_log(self, log_line: str) -> Dict[str, Any]:
        result = {}
        
        # Extract log level
        level_match = re.search(r'\b(ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE|CRITICAL|FATAL)\b', log_line, re.IGNORECASE)
        if level_match:
            result['level'] = level_match.group(1).upper()

        # Extract class/module information
        class_match = re.search(r'(\w+(?:\.\w+)+)', log_line)
        if class_match:
            result['class'] = class_match.group(1)

        # Extract user information
        user_match = re.search(r"User\s+'([^']+)'", log_line)
        if user_match:
            result['user'] = user_match.group(1)

        # Extract endpoint information
        endpoint_match = re.search(r"endpoint\s+'([^']+)'", log_line)
        if endpoint_match:
            result['endpoint'] = endpoint_match.group(1)

        # Extract message content
        message = log_line
        # Remove timestamp if present
        message = re.sub(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\s*', '', message)
        # Remove log level if present
        message = re.sub(r'\b(ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE|CRITICAL|FATAL)\b\s*', '', message, flags=re.IGNORECASE)
        result['message'] = message.strip()

        return result

    def extract_log(self, log_line: str) -> Dict[str, Any]:
        log_type = self.parse_log_type(log_line)
        result = {
            'raw_log': log_line.strip(),
            'timestamp': self.parse_timestamp(log_line),
            'type': log_type
        }

        if log_type in ['kernel', 'sshd', 'cron', 'systemd', 'networkmanager', 'wpa_supplicant']:
            result.update(self.parse_system_log(log_line))
        elif log_type in ['http', 'iis', 'nginx']:
            result.update(self.parse_web_log(log_line))
        elif log_type in ['application', 'database']:
            result.update(self.parse_application_log(log_line))

        return result

    def parse_file(self, input_file: str, output_file: str) -> None:
        try:
            results = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        results.append(self.extract_log(line))
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"Error: {str(e)}")

# Example usage
# if __name__ == "__main__":
#     parser = LogParser()
    
#     # Test with sample logs
#     test_logs = [
#         "Jan 10 11:37 AM myhostname kernel[456]: [123456789] eth0 link up",
#         "Jan 5 09:12:39 dell-Inspiron-5584 wpa_supplicant[938]: wlp4s0: CTRL-EVENT-SUBNET-STATUS-UPDATE status=0",
#         "[10/Jan/2025 11:31 AM] \"POST /api/create HTTP/1.1\" status_code=201 response_time=75ms",
#         "2025-01-10T11:25:15Z error Database connection failed for user 'admin'"
#     ]
    
#     for log in test_logs:
#         result = parser.extract_log(log)
#         print(json.dumps(result, indent=2))