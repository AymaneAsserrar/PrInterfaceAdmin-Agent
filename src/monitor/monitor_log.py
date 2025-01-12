from pathlib import Path
from typing import List, Dict
from datetime import datetime

def parse_log_line(line: str) -> Dict[str, Union[str, datetime]]:
    """
    Parse a single Apache log line.
    
    Args:
        line: Raw log line string
        
    Returns:
        Dict containing parsed log fields
        
    Raises:
        ValueError: If line format is invalid
    """
    try:
        line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %b")
        parsed = line_parser(line)
        return {
            'remote_host': parsed['remote_host'],
            'remote_user': parsed['remote_user'],
            'status': parsed['status'],
            'request_url': parsed['request_url'],
            'timestamp': parsed['time_received_datetimeobj']
        }
    except Exception as e:
        raise ValueError(f"Invalid log line format: {str(e)}")

def parse_log_file(path: Path) -> List[Dict[str, Union[str, datetime]]]:
    """
    Parse entire Apache log file.
    
    Args:
        path: Path to log file
        
    Returns:
        List of parsed log entries
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file can't be read
    """
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")
        
    results = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(parse_log_line(line.strip()))
    return results