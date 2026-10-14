# Lab 5 - Event API

This FastAPI application stores events in `events.json` at the project root. The file is seeded from the starter repository's `event.json` example.

## Run locally

Run these commands from the project directory containing `requirements.txt`.

### Ubuntu or WSL

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app/main.py
```

If `.venv` already exists, start with the second command. You can optionally activate it with `source .venv/bin/activate`.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app/main.py
```

Open <http://127.0.0.1:8000/docs> to use the interactive API documentation. To run the checks, use `.venv/bin/python -m unittest discover -s tests -v` on Ubuntu or WSL, or `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` in Windows PowerShell.

The API provides event listing, filtering, lookup, creation, update, deletion, and a list of joiners who attended at least two distinct events. `EventFileManager.FILE_PATH` is `events.json`; it resolves that file relative to the project root so the server works regardless of the launch directory.
