# collector.py — script de collecte des données RATP PRIM
# Ce script tourne en production sur le VPS Hetzner comme service systemd
# Il interroge l'API PRIM (Île-de-France Mobilités) toutes les 5 minutes
# et sauvegarde les snapshots en JSON dans data/raw/

import json
import os
import time
from datetime import datetime, timezone

import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

IDFM_API_KEY = os.getenv("IDFM_API_KEY")
DATA_DIR = os.getenv("DATA_DIR", "data/raw")

METRO_LINES = ["1", "2", "3", "3B", "4", "5", "6", "7", "7B", "8", "9", "10", "11", "12", "13", "14"]

PRIM_BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/estimated-timetable"


def fetch_line(line_id: str) -> list[dict]:
    """Interroge l'endpoint estimated-timetable pour une ligne."""
    headers = {"apikey": IDFM_API_KEY}
    params = {"LineRef": f"STIF:Line::C{line_id.zfill(5)}:"}
    try:
        resp = requests.get(PRIM_BASE_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        calls = []
        for journey in data.get("Siri", {}).get("ServiceDelivery", {}).get("EstimatedTimetableDelivery", []):
            for vehicle in journey.get("EstimatedJourneyVersionFrame", []):
                for call in vehicle.get("EstimatedVehicleJourney", []):
                    for stop_call in call.get("EstimatedCalls", {}).get("EstimatedCall", []):
                        calls.append({
                            "line": line_id,
                            "stop": stop_call.get("StopPointRef", {}).get("value", ""),
                            "departure_status": stop_call.get("DepartureStatus", ""),
                            "arrival_status": stop_call.get("ArrivalStatus", ""),
                            "is_delayed": stop_call.get("DepartureStatus", "") not in ("", "onTime"),
                            "expected_departure": stop_call.get("ExpectedDepartureTime", ""),
                            "aimed_departure": stop_call.get("AimedDepartureTime", ""),
                        })
        return calls
    except Exception as e:
        print(f"[ERROR] Ligne {line_id}: {e}")
        return []


def collect_snapshot() -> dict:
    """Collecte un snapshot complet de toutes les lignes."""
    fetched_at = datetime.now(timezone.utc).isoformat()
    metro_calls = []
    for line in METRO_LINES:
        calls = fetch_line(line)
        metro_calls.extend(calls)
        print(f"  Ligne {line}: {len(calls)} appels")

    return {
        "fetched_at": fetched_at,
        "metro_calls": metro_calls,
    }


def save_snapshot(snapshot: dict) -> str:
    """Sauvegarde le snapshot en JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    ts = snapshot["fetched_at"].replace(":", "-").replace("+", "Z")
    filename = f"snapshot_{ts}.json"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return path


def run():
    def job():
        print(f"\n[{datetime.now(timezone.utc).isoformat()}] Collecte en cours...")
        snapshot = collect_snapshot()
        path = save_snapshot(snapshot)
        print(f"[OK] Snapshot sauvegardé : {path} ({len(snapshot['metro_calls'])} appels)")

    schedule.every(5).minutes.do(job)
    job()  # première collecte immédiate
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    run()
