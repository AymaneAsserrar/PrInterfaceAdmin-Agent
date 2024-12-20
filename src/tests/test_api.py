import threading
import os
from fastapi.testclient import TestClient
from server import app
from monitor import MonitorTask
from typing import List
import datetime
from monitor.monitor_log import parser_ligne, parser
import pytest


class MonitorTaskFake(MonitorTask):
    """
    Monitor class to mock the real monitor
    Instead of using the real monitor that fetch data on the host
    we use a monitor that provide "fake" values to control the output
    and make deterministic test (deterministic = repeatable and known values)
    """
    interval: int = 0
    cpu_percent: List[float] = ["10", "12"]
    total_ram = 4000.
    available_ram = 3000.
    used_ram = 1000.
    free_ram = 3000.      
    num_cores: int = 3

    def __init__(self): 
        None

    def monitor(self):
        pass

# Launching the real monitor for test involving the real monitor
client = TestClient(app)
thread = threading.Thread(target=app.state.monitortask.monitor, daemon=True)
thread.start()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_cpu_usage():
    # backup of the existing monitortask to restore it after the test
    save_app = app.state.monitortask
    # use fake monitor to have deterministic values
    app.state.monitortask = MonitorTaskFake()
    response = client.get("/metrics/v1/cpu/usage")
    print(app.state.monitortask.cpu_percent)
    assert response.status_code == 200
    assert response.json() == [{"id": 0, "usage": "10"}, {"id": 1, "usage": "12"}]
    # restore monitortask for next test
    app.state.monitortask = save_app



def test_get_ram_info():
    # backup of the existing monitortask to restore it after the test
    save_app = app.state.monitortask
    try:
        print("Starting RAM info test...")
        # use fake monitor to have deterministic values
        app.state.monitortask = MonitorTaskFake()
        
        response = client.get("/metrics/v1/ram/info")
        print("Response from RAM endpoint:", response.json())
        
        assert response.status_code == 200
        assert response.json() == {
            "total": 4000.0,
            "available": 3000.0,
            "used": 1000.0,
            "free": 3000.0
        }
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        raise
    finally:
        # restore monitortask for next test
        app.state.monitortask = save_app
def test_parser_ligne_simple():
    # Log simulé
    log = '192.168.1.10 - - [01/Jan/2020:08:12:14 +0000] "GET / HTTP/1.1" 200 1245 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'

    # Résultat attendu
    resultat_attendu = [
        '192.168.1.10',  # remote_host
        '-',             # remote_user
        '200',           # status
        '/',             # request_url
        datetime.datetime(2020, 1, 1, 8, 12, 14)  # time_received_datetimeobj
    ]

    # Appel de la fonction parser_ligne
    resultat = parser_ligne(log)
    assert resultat == resultat_attendu, f"Erreur : {resultat} != {resultat_attendu}"

def test_parser_simple(tmp_path):
    # Logs simulés
    logs = [
        '192.168.1.10 - - [01/Jan/2020:08:12:14 +0000] "GET / HTTP/1.1" 200 1245 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
        '192.168.1.11 - - [01/Jan/2020:08:15:00 +0000] "POST /login HTTP/1.1" 302 512 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
        '192.168.1.12 - - [01/Jan/2020:08:18:00 +0000] "GET /notfound HTTP/1.1" 404 178 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'
    ]

    # Créer un fichier temporaire avec les logs
    log_file = tmp_path / "test_logs.log"
    log_file.write_text("\n".join(logs))

    # Résultat attendu
    resultat_attendu = [
        ['192.168.1.10', '-', '200', '/', datetime.datetime(2020, 1, 1, 8, 12, 14)],
        ['192.168.1.11', '-', '302', '/login', datetime.datetime(2020, 1, 1, 8, 15, 0)],
        ['192.168.1.12', '-', '404', '/notfound', datetime.datetime(2020, 1, 1, 8, 18, 0)],
    ]

    # Appeler la fonction parser et stocker les résultats
    resultats = []
    with open(log_file, 'r') as fichier:
        for ligne in fichier:
            resultats.append(parser_ligne(ligne.strip()))

    # Comparer les résultats
    assert resultats == resultat_attendu, f"Erreur : {resultats} != {resultat_attendu}"

def test_parser_simple_invalid(capsys, tmp_path):
    # Logs invalides (manquent des champs importants)
    logs_invalides = [
        "192.168.1.10 - - [01/Jan/2020:08:12:14 +0000] GET / HTTP/1.1",
        "192.168.1.11 - - [01/Jan/2020:08:15:00 +0000] 302",
        "INVALID LOG LINE"
    ]

    # Créer un fichier temporaire avec les logs invalides
    log_file = tmp_path / "test_logs_invalid.log"
    log_file.write_text("\n".join(logs_invalides))

    # Appeler la fonction parser et vérifier qu'une exception est levée
    with pytest.raises(Exception):
        parser(str(log_file))

