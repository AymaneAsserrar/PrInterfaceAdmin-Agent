"""Module for parsing Apache log files and outputting structured data."""
from pathlib import Path
from typing import List, Dict, Union
from datetime import datetime
import apache_log_parser
import json
import sys
import argparse

def parse_log_line(line: str) -> Dict[str, Union[str, datetime]]:
    """Parse a single Apache log line."""
    try:
        line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %b")
        parsed = line_parser(line)
        return {
            'remote_host': parsed['remote_host'],
            'remote_user': parsed['remote_user'],
            'status': parsed['status'],
            'request_url': parsed['request_url'],
            'timestamp': parsed['time_received_datetimeobj'].isoformat()
        }
    except Exception as e:
        raise ValueError(f"Invalid log line format: {str(e)}")

def parse_log_file(input_path: Path, output_path: Path) -> None:
    """
    Parse Apache log file and write results to output file.
    
    Args:
        input_path: Path to input log file
        output_path: Path to output parsed logs
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Log file not found: {input_path}")
        
    with output_path.open('w', encoding='utf-8') as out_file:
        with input_path.open('r', encoding='utf-8') as in_file:
            for line in in_file:
                if line.strip():
                    try:
                        parsed_line = parse_log_line(line.strip())
                        out_file.write(json.dumps(parsed_line) + '\n')
                    except ValueError as e:
                        print(f"Skipping invalid line: {e}")

def main():
    parser = argparse.ArgumentParser(description='Parse Apache log files')
    parser.add_argument('command', choices=['parse'], help='Command to execute')
    parser.add_argument('input_file', help='Path to the input log file')
    args = parser.parse_args()

    if args.command == 'parse':
        input_file = Path(args.input_file)
        output_file = Path("/logs/parsed_logs.log")
        try:
            parse_log_file(input_file, output_file)
            print(f"Successfully parsed logs to {output_file}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()