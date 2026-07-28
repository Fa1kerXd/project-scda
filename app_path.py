import os
import sys
from pathlib import Path

APP_NAME = "CorrecaoApontamentos"


def get_app_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".local" / "share"

    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


DATABASE_FILE = get_app_data_dir() / "database.db"
EMAIL_ATTACHMENT_FILE = get_app_data_dir() / "corrigir.txt"