from pathlib import Path

from whenever import Instant

STATE_DIR = Path("data")
STATE_FILE = STATE_DIR / "last_checked.txt"


def get_last_checked() -> Instant | None:
    if not STATE_FILE.exists():
        return None

    try:
        timestamp = STATE_FILE.read_text().strip()
        return Instant.parse_iso(timestamp)
    except Exception:
        return None


def set_last_checked(instant: Instant):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(instant.format_iso())
