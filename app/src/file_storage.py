import json
from pathlib import Path


class EventFileManager:
    FILE_PATH = "events.json"

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else Path(__file__).resolve().parents[2] / self.FILE_PATH

    def read_events_from_file(self) -> list[dict]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                events = json.load(file)
            return events if isinstance(events, list) else []
        except (OSError, UnicodeError, json.JSONDecodeError):
            return []

    def write_events_to_file(self, events: list[dict]) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(events, file, indent=4, ensure_ascii=False)
            file.write("\n")
