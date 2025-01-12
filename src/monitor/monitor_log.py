# src/monitor/monitor_log.py

import re
from datetime import datetime
from typing import List, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parser_ligne(ligne: str) -> List[Union[str, datetime]]:
    """
    Parse a single line from an Apache log file.
    
    Args:
        ligne (str): A single line from the log file to parse
        
    Returns:
        List[Union[str, datetime]]: Contains extracted log information:
        - remote_host: IP address of the client
        - remote_user: Username of the client
        - status: HTTP status code
        - request_url: Requested URL
        - timestamp: Time of the request
    """
    try:
        pattern = re.compile(
            r'(?P<ip>[\d.]+)\s+'
            r'(?P<remote_user>[-\w]+)\s+'
            r'(?P<user>[-\w]+)\s+'
            r'\[(?P<timestamp>[\w:/\s\+]+)\]\s+'
            r'"(?:GET|POST|PUT|DELETE)\s+'
            r'(?P<request_url>[^\s]+)\s+'
            r'HTTP/[\d.]+"\s+'
            r'(?P<status>\d+)\s+'
            r'\d+\s+'
            r'"[^"]*"\s+'
            r'"[^"]*"'
        )
        
        match = pattern.match(ligne)
        if not match:
            raise ValueError(f"Could not parse line: {ligne}")
            
        data = match.groupdict()
        
        # Parse timestamp
        timestamp = datetime.strptime(
            data['timestamp'],
            '%d/%b/%Y:%H:%M:%S %z'
        )
        
        return [
            data['ip'],
            data['remote_user'],
            data['status'],
            data['request_url'],
            timestamp
        ]
        
    except Exception as e:
        logger.error(f"Error parsing line: {ligne}, Error: {str(e)}")
        raise

def parser(chemin: str) -> List[List[Union[str, datetime]]]:
    """
    Parse an entire log file and process each line.
    
    Args:
        chemin (str): Path to the log file to parse
        
    Returns:
        List[List[Union[str, datetime]]]: List of parsed log entries
        
    Raises:
        FileNotFoundError: If the specified log file is not found
        Exception: If there's an error parsing the log file
    """
    results = []
    try:
        with open(chemin, 'r', encoding='utf-8') as fichier:
            for ligne in fichier:
                if ligne.strip():  # Skip empty lines
                    results.append(parser_ligne(ligne.strip()))
        return results
    except FileNotFoundError:
        logger.error(f"Log file not found: {chemin}")
        raise
    except Exception as e:
        logger.error(f"Error parsing file {chemin}: {str(e)}")
        raise

def parse_apache_log(path: str) -> dict:
    """
    Parse Apache log file and generate statistics.
    
    Args:
        path (str): Path to the log file
        
    Returns:
        dict: Statistics about the log file including:
        - visitor counts
        - page access counts
        - error logs
    """
    visitor_stats = {}
    page_stats = {}
    errors = []
    
    try:
        parsed_logs = parser(path)
        for log in parsed_logs:
            ip, _, status, url, timestamp = log
            
            # Update visitor stats
            visitor_stats[ip] = visitor_stats.get(ip, 0) + 1
            
            # Update page stats
            page_stats[url] = page_stats.get(url, 0) + 1
            
            # Track errors
            if int(status) >= 400:
                errors.append({
                    'ip': ip,
                    'status': status,
                    'url': url,
                    'timestamp': timestamp.isoformat()
                })
                
        return {
            'visitors': visitor_stats,
            'pages': page_stats,
            'errors': errors,
            'summary': {
                'total_visitors': len(visitor_stats),
                'total_pages': len(page_stats),
                'total_errors': len(errors)
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing log file: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
        try:
            stats = parse_apache_log(log_path)
            print(stats)
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("Please provide a log file path")