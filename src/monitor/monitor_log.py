import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LogEntry:
    ip: str
    timestamp: datetime
    request_method: str
    path: str
    protocol: str
    status_code: int
    bytes_sent: int
    user_agent: str
    
    def to_dict(self) -> Dict:
        return {
            'ip': self.ip,
            'timestamp': self.timestamp.isoformat(),
            'request_method': self.request_method,
            'path': self.path,
            'protocol': self.protocol,
            'status_code': self.status_code,
            'bytes_sent': self.bytes_sent,
            'user_agent': self.user_agent
        }

class ApacheLogParser:
    def __init__(self, log_dir: str = "/var/log/apache2"):
        self.log_dir = Path(log_dir)
        self.log_pattern = re.compile(
            r'(?P<ip>[\d.]+)\s+[-]\s+[-]\s+'
            r'\[(?P<timestamp>.*?)\]\s+'
            r'"(?P<request_method>\w+)\s+'
            r'(?P<path>[^\s]*)\s+'
            r'(?P<protocol>[^"]*)"\s+'
            r'(?P<status_code>\d+)\s+'
            r'(?P<bytes_sent>\d+)\s+'
            r'"[^"]*"\s+'
            r'"(?P<user_agent>[^"]*)"'
        )
        
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse a single line from the log file."""
        try:
            match = self.log_pattern.match(line)
            if not match:
                logger.warning(f"Could not parse line: {line}")
                return None
                
            data = match.groupdict()
            return LogEntry(
                ip=data['ip'],
                timestamp=datetime.strptime(data['timestamp'], '%d/%b/%Y:%H:%M:%S %z'),
                request_method=data['request_method'],
                path=data['path'],
                protocol=data['protocol'],
                status_code=int(data['status_code']),
                bytes_sent=int(data['bytes_sent']),
                user_agent=data['user_agent']
            )
        except Exception as e:
            logger.error(f"Error parsing line: {line}, Error: {str(e)}")
            return None

    def analyze_logs(self) -> Tuple[Dict, Dict, List]:
        """Analyze logs and return visitor stats, page stats, and errors."""
        visitor_stats: Dict[str, int] = {}
        page_stats: Dict[str, int] = {}
        errors: List[Dict] = []
        
        for log_file in self.log_dir.glob("*.log"):
            logger.info(f"Processing log file: {log_file}")
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        entry = self.parse_line(line.strip())
                        if entry:
                            # Update visitor stats
                            visitor_stats[entry.ip] = visitor_stats.get(entry.ip, 0) + 1
                            
                            # Update page stats
                            page_stats[entry.path] = page_stats.get(entry.path, 0) + 1
                            
                            # Track errors (4xx and 5xx status codes)
                            if entry.status_code >= 400:
                                errors.append(entry.to_dict())
            except Exception as e:
                logger.error(f"Error processing file {log_file}: {str(e)}")
                
        return visitor_stats, page_stats, errors

    def generate_report(self) -> str:
        """Generate a JSON report of the log analysis."""
        visitor_stats, page_stats, errors = self.analyze_logs()
        
        report = {
            'top_visitors': dict(sorted(visitor_stats.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:10]),
            'top_pages': dict(sorted(page_stats.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True)[:10]),
            'errors': errors[:100],  # Limit to last 100 errors
            'summary': {
                'total_visitors': len(visitor_stats),
                'total_pages_accessed': len(page_stats),
                'total_errors': len(errors)
            }
        }
        
        return json.dumps(report, indent=2)

def main():
    parser = ApacheLogParser()
    report = parser.generate_report()
    print(report)
    
    # Optionally save the report
    with open('apache_analysis_report.json', 'w') as f:
        f.write(report)

if __name__ == "__main__":
    main()