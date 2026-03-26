import json
from pathlib import Path
from typing import List


DB_DIR = Path(__file__).resolve().parent
GAMES_FILE = DB_DIR / "games.json"


def ensure_db_dir() -> None:
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def load_games() -> List[dict]:
    ensure_db_dir()
    if not GAMES_FILE.exists():
        return []
    try:
        with GAMES_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_games(games: List[dict]) -> bool:
    ensure_db_dir()
    try:
        with GAMES_FILE.open("w", encoding="utf-8") as f:
            json.dump(games, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False
