# Lab 5 - Event API

This FastAPI application stores events in `events.json` at the project root. The file is seeded from the starter repository's `event.json` example.

## Run locally

From this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app/main.py
```

Open <http://127.0.0.1:8000/docs> to use the interactive API documentation. Run the checks with:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

The API provides event listing, filtering, lookup, creation, update, deletion, and a list of joiners who attended at least two distinct events. `EventFileManager.FILE_PATH` is `events.json`; it resolves that file relative to the project root so the server works regardless of the launch directory.
