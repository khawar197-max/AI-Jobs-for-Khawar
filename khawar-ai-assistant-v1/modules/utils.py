import json
from pathlib import Path
from typing import Any

def load_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def save_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

def load_profile(path: Path):
    return load_json(path, {
        "name": "Khawar Khalid",
        "target_fields": [],
        "education": [],
        "experience": [],
        "skills": [],
        "preferences": {},
        "base_cv": ""
    })

def clean_text(value: str) -> str:
    return " ".join((value or "").split())
