from fastapi import APIRouter, HTTPException

from .event_analyzer import EventAnalyzer
from .file_storage import EventFileManager
from .models import Event


router = APIRouter()
file_manager = EventFileManager()
event_analyzer = EventAnalyzer()


@router.get("/events", response_model=list[Event])
async def get_all_events():
    return file_manager.read_events_from_file()


@router.get("/events/filter", response_model=list[Event])
async def get_events_by_filter(
    date: str | None = None,
    organizer: str | None = None,
    status: str | None = None,
    event_type: str | None = None,
):
    if not any(value is not None for value in (date, organizer, status, event_type)):
        raise HTTPException(status_code=400, detail="At least one filtering parameter required")

    events = file_manager.read_events_from_file()
    if date is not None:
        events = [event for event in events if event["date"] == date]
    if organizer is not None:
        events = [
            event for event in events
            if organizer in (event["organizer"]["email"], event["organizer"]["name"])
        ]
    if status is not None:
        events = [event for event in events if event["status"] == status]
    if event_type is not None:
        events = [event for event in events if event["type"] == event_type]
    return events


@router.get("/events/joiners/multiple-meetings")
async def get_joiners_multiple_meetings():
    events = file_manager.read_events_from_file()
    joiners = event_analyzer.get_joiners_multiple_meetings_method(events)
    return joiners if joiners else {"message": "No joiners attending at least 2 meetings"}


@router.get("/events/{event_id}", response_model=Event)
async def get_event_by_id(event_id: int):
    for event in file_manager.read_events_from_file():
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")


@router.post("/events", response_model=Event, status_code=201)
async def create_event(event: Event):
    events = file_manager.read_events_from_file()
    if any(existing["id"] == event.id for existing in events):
        raise HTTPException(status_code=400, detail="Event ID already exists")
    events.append(event.model_dump())
    file_manager.write_events_to_file(events)
    return event


@router.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: int, event: Event):
    events = file_manager.read_events_from_file()
    for index, existing in enumerate(events):
        if existing["id"] == event_id:
            updated = event.model_copy(update={"id": event_id})
            events[index] = updated.model_dump()
            file_manager.write_events_to_file(events)
            return updated
    raise HTTPException(status_code=404, detail="Event not found")


@router.delete("/events/{event_id}")
async def delete_event(event_id: int):
    events = file_manager.read_events_from_file()
    remaining = [event for event in events if event["id"] != event_id]
    if len(remaining) == len(events):
        raise HTTPException(status_code=404, detail="Event not found")
    file_manager.write_events_to_file(remaining)
    return {"message": "Event deleted successfully"}
