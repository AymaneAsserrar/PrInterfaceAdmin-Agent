"""
Module for parsing and analyzing Apache web server log files.

This module provides functionality to read and parse Apache log files,
extracting relevant information such as remote host, user, status code,
and request details.
"""

import os
from typing import List, Union
import apache_log_parser


def parser_ligne(ligne: str) -> List[Union[str, str]]:
    """
    Parse a single line from an Apache log file.

    Args:
        ligne (str): A single line from the log file to parse

    Returns:
        List[Union[str, str]]: Contains extracted log information:
            - remote_host: IP address of the client
            - remote_user: Username of the client
            - status: HTTP status code
            - request_url: Requested URL
            - timestamp: Time of the request
    """
    line_parser = apache_log_parser.make_parser("%h %l %u %t \"%r\" %>s %b")
    log_parsed = line_parser(ligne)
    return [
        log_parsed['remote_host'],
        log_parsed['remote_user'],
        log_parsed['status'],
        log_parsed['request_url'],
        log_parsed['time_received_datetimeobj']
    ]


def parser(chemin: str) -> None:
    """
    Parse an entire log file and process each line.

    Args:
        chemin (str): Path to the log file to parse

    Raises:
        FileNotFoundError: If the specified log file is not found
        Exception: If there's an error parsing the log file
    """
    with open(chemin, 'r', encoding='utf-8') as fichier:
        for ligne in fichier:
            resultat = parser_ligne(ligne.strip())
            print(resultat)


# Get current directory and construct log file path
CURRENT_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(CURRENT_DIR, "../tests/tst_log.log")

# Example log entry for testing
EXAMPLE_LOG = ('127.0.0.1 - - [09/Jan/2020:10:35:48 +0000] '
               '"GET / HTTP/1.1" 200 11229 "-" "Wget/1.19.4 (linux-gnu)"')

if __name__ == "__main__":
    parser(LOG_PATH)