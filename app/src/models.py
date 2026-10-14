from pydantic import BaseModel, Field


class Organizer(BaseModel):
    name: str
    email: str


class Joiner(BaseModel):
    name: str
    email: str
    country: str


class Event(BaseModel):
    id: int
    name: str
    date: str
    organizer: Organizer
    status: str
    type: str
    location: str
    max_attendees: int
    joiners: list[Joiner] = Field(default_factory=list)
