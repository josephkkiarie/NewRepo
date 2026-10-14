import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from src.app import app  # noqa: E402
from src.event_analyzer import EventAnalyzer  # noqa: E402
from src.file_storage import EventFileManager  # noqa: E402


SAMPLE = {
    "id": 1,
    "name": "First event",
    "date": "2024-03-06",
    "organizer": {"name": "fdev", "email": "fdev@example.com"},
    "status": "active",
    "type": "event",
    "location": "Budapest, Hungary",
    "max_attendees": 100,
    "joiners": [{"name": "Test User", "email": "test@test.com", "country": "Hungary"}],
}


class EventApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "events.json"
        self.manager = EventFileManager(self.path)
        self.manager.write_events_to_file([SAMPLE])
        self.patcher = patch("src.routes.file_manager", self.manager)
        self.patcher.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.patcher.stop()
        self.client.close()
        self.temp_dir.cleanup()

    def test_root_and_read_routes(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(len(self.client.get("/events").json()), 1)
        self.assertEqual(self.client.get("/events/1").json()["name"], "First event")
        self.assertEqual(self.client.get("/events/999").status_code, 404)
        self.assertEqual(self.client.get("/events/filter").status_code, 400)

        for parameter, value in (
            ("date", "2024-03-06"),
            ("organizer", "fdev@example.com"),
            ("organizer", "fdev"),
            ("status", "active"),
            ("event_type", "event"),
        ):
            self.assertEqual(len(self.client.get("/events/filter", params={parameter: value}).json()), 1)
        self.assertEqual(self.client.get("/events/filter", params={"status": "cancelled"}).json(), [])

    def test_create_update_delete_and_duplicates(self):
        second = {**SAMPLE, "id": 2, "name": "Second event"}
        self.assertEqual(self.client.post("/events", json=second).status_code, 201)
        duplicate = self.client.post("/events", json=second)
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(duplicate.json()["detail"], "Event ID already exists")

        changed = {**second, "id": 99, "name": "Updated event"}
        response = self.client.put("/events/2", json=changed)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 2)
        self.assertEqual(self.client.get("/events/2").json()["name"], "Updated event")
        self.assertEqual(self.client.put("/events/999", json=changed).status_code, 404)

        self.assertEqual(self.client.delete("/events/2").json()["message"], "Event deleted successfully")
        self.assertEqual(self.client.delete("/events/2").status_code, 404)
        self.assertEqual([event["id"] for event in self.manager.read_events_from_file()], [1])

    def test_multiple_meetings_returns_all_matching_joiners(self):
        self.assertEqual(
            self.client.get("/events/joiners/multiple-meetings").json(),
            {"message": "No joiners attending at least 2 meetings"},
        )
        extra_joiner = {"name": "Second User", "email": "second@test.com", "country": "Hungary"}
        second = {**SAMPLE, "id": 2, "joiners": SAMPLE["joiners"] + [extra_joiner]}
        third = {**SAMPLE, "id": 3, "joiners": SAMPLE["joiners"] + [extra_joiner]}
        self.manager.write_events_to_file([SAMPLE, second, third])
        joiners = self.client.get("/events/joiners/multiple-meetings").json()
        self.assertEqual(joiners, [
            {"full_name": "Test User", "email": "test@test.com", "meetings_attended": 3},
            {"full_name": "Second User", "email": "second@test.com", "meetings_attended": 2},
        ])

    def test_storage_read_failure_and_distinct_events(self):
        self.path.unlink()
        self.assertEqual(self.manager.read_events_from_file(), [])
        self.path.write_text("{bad json", encoding="utf-8")
        self.assertEqual(self.manager.read_events_from_file(), [])

        event = {**SAMPLE, "joiners": SAMPLE["joiners"] * 2}
        self.assertEqual(EventAnalyzer().get_joiners_multiple_meetings_method([event]), [])


if __name__ == "__main__":
    unittest.main()
