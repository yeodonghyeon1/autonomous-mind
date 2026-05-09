import json
from pathlib import Path
from datetime import datetime

_STATE_PATH = Path(__file__).parent.parent / "vault" / ".state.json"


def load_state() -> dict:
    if not _STATE_PATH.exists():
        return {
            "cycle": 0,
            "last_hypothesis": None,
            "next_hypothesis_seed": None,
            "key_insights": [],
            "created_at": datetime.now().isoformat(),
        }
    with open(_STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def extract_section(text: str, header: str) -> str:
    """Extract content under a markdown ## header."""
    if header not in text:
        return ""
    start = text.index(header) + len(header)
    next_header = text.find("\n##", start)
    return text[start:next_header].strip() if next_header != -1 else text[start:].strip()
