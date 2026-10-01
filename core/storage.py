"""Lettura/scrittura dei dati su file JSON (data/gym_data.json)."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "gym_data.json"


def load():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8")) if DATA_FILE.exists() else {}
    data.setdefault("exercises", {})  # lista esercizi vuota
    data.setdefault("logs", [])
    data.setdefault("plan", {})  # giorno (0=Lun ... 6=Dom) -> lista esercizi
    return data


def save(data):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
