"""Module providing log analysis and metrics collection functionality."""
import os
from collections import Counter
from datetime import datetime
from typing import Dict, List

import apache_log_parser
from domain.schemas import LogEntrySchema, LogMetricsSchema


class LogService:
    """Service class for analyzing log data and generating metrics."""

    def __init__(self) -> None:
        """Initialize the log service with configured parser."""
        self.line_parser = apache_log_parser.make_parser(
            "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
        )

    def parse_log_entry(self, line: str) -> LogEntrySchema:
        """
        Parse a single log line into a structured schema.

        Args:
            line: Raw log line to parse

        Returns:
            LogEntrySchema: Structured log entry data

        Raises:
            Exception: If parsing fails
        """
        try:
            parsed = self.line_parser(line)
            return LogEntrySchema(
                timestamp=parsed["time_received_datetimeobj"],
                ip=parsed["remote_host"],
                url=parsed["request_url"],
                status_code=int(parsed["status"]),
                user_agent=parsed["request_header_user_agent"],
            )
        except Exception as exc:
            raise ValueError(f"Error parsing log line: {exc}") from exc

    async def get_log_metrics(
        self, access_log_path: str, error_log_path: str
    ) -> LogMetricsSchema:
        """
        Analyze log files and generate comprehensive metrics.

        Args:
            access_log_path: Path to the access log file
            error_log_path: Path to the error log file

        Returns:
            LogMetricsSchema: Aggregated metrics including request counts,
                            status codes, and recent errors

        Raises:
            FileNotFoundError: If log file is not accessible
            IOError: If reading log file fails
        """
        entries: List[LogEntrySchema] = []
        status_counter = Counter()
        url_counter: Counter = Counter()

        if not os.path.exists(access_log_path):
            return self._create_empty_metrics()

        try:
            entries = self._process_log_file(access_log_path, status_counter, url_counter)
            return self._calculate_metrics(entries, status_counter, url_counter)
        except Exception as exc:
            raise IOError(f"Error analyzing logs: {exc}") from exc

    def _create_empty_metrics(self) -> LogMetricsSchema:
        """
        Create empty metrics when no log file is available.

        Returns:
            LogMetricsSchema: Empty metrics structure
        """
        return LogMetricsSchema(
            total_requests=0,
            success_count=0,
            error_count=0,
            status_codes={},
            top_urls=[],
            recent_errors=[],
        )

    def _process_log_file(
        self, log_path: str, status_counter: Counter, url_counter: Counter
    ) -> List[LogEntrySchema]:
        """
        Process log file and update counters.

        Args:
            log_path: Path to the log file
            status_counter: Counter for HTTP status codes
            url_counter: Counter for URLs

        Returns:
            List[LogEntrySchema]: List of processed log entries
        """
        entries = []
        with open(log_path, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    entry = self.parse_log_entry(line.strip())
                    entries.append(entry)
                    status_counter[str(entry.status_code)] += 1
                    url_counter[entry.url] += 1
                except ValueError:
                    continue
        return entries

    def _calculate_metrics(
        self,
        entries: List[LogEntrySchema],
        status_counter: Counter,
        url_counter: Counter,
    ) -> LogMetricsSchema:
        """
        Calculate final metrics from processed log data.

        Args:
            entries: List of processed log entries
            status_counter: Counter with status code frequencies
            url_counter: Counter with URL frequencies

        Returns:
            LogMetricsSchema: Calculated metrics
        """
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