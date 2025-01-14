"""
This module provides services for analyzing log data.
"""
import os
from typing import List, Dict
from collections import Counter
from datetime import datetime
import apache_log_parser
from domain.schemas import LogEntrySchema, LogMetricsSchema

class LogService:
    """Service for analyzing log data."""
    
    def __init__(self):
        """Initialize the log service with parser."""
        self.line_parser = apache_log_parser.make_parser(
            "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
        )

    async def get_log_metrics(self, access_log_path: str, error_log_path: str) -> LogMetricsSchema:
        """
        Analyze log file and return metrics.
        
        Args:
            access_log_path: Path to the access log file
            error_log_path: Path to the error log file
            
        Returns:
            LogMetricsSchema: Aggregated log metrics
        """
        entries: List[LogEntrySchema] = []
        status_counter = Counter()
        url_counter = Counter()

        try:
            # Check if log file exists
            if not os.path.exists(access_log_path):
                print(f"Access log file not found at {access_log_path}")
                return LogMetricsSchema(
                    total_requests=0,
                    success_count=0,
                    error_count=0,
                    status_codes={},
                    top_urls=[],
                    recent_errors=[]
                )

            with open(access_log_path, "r", encoding="utf-8") as file:
                for line in file:
                    try:
                        entry = self.parse_log_entry(line.strip())
                        entries.append(entry)
                        status_counter[str(entry.status_code)] += 1
                        url_counter[entry.url] += 1
                    except Exception as e:
                        print(f"Error parsing log line: {e}")
                        continue

            # Calculate metrics
            error_entries = [e for e in entries if e.status_code >= 400]
            recent_errors = sorted(
                error_entries, key=lambda x: x.timestamp, reverse=True
            )[:10]

            return LogMetricsSchema(
                total_requests=len(entries),
                success_count=sum(1 for e in entries if e.status_code < 400),
                error_count=len(error_entries),
                status_codes=dict(status_counter),
                top_urls=[
                    {"url": url, "count": count}
                    for url, count in url_counter.most_common(5)
                ],
                recent_errors=recent_errors,
            )
        except Exception as e:
            print(f"Error analyzing logs: {str(e)}")
            raise