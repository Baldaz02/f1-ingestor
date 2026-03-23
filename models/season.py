"""Season model representing a Formula 1 season."""
from dataclasses import dataclass, field
from typing import List, Optional
from .event import Event, EventStatus


@dataclass
class Season:
    """
    Represents a Formula 1 season.
    
    Attributes:
        year: The season year
        events: List of events in the season
        champion: World champion driver name (if season is complete)
        constructor_champion: Constructor champion team name
    """
    year: int
    events: List[Event] = field(default_factory=list)
    champion: Optional[str] = None
    constructor_champion: Optional[str] = None
    
    def __post_init__(self):
        """Validate season data."""
        if self.year < 1950:
            raise ValueError("F1 started in 1950, year must be >= 1950")
    
    @property
    def total_events(self) -> int:
        """Get total number of event records (including removed slots)."""
        return len(self.events)
    
    @property
    def scheduled_rounds(self) -> int:
        """Rounds on the calendar (excludes removed/deleted slots)."""
        return sum(1 for e in self.events if e.status != EventStatus.DELETED)
    
    @property
    def completed_events(self) -> int:
        """Get number of completed events."""
        return sum(1 for e in self.events if e.is_completed)
    
    @property
    def upcoming_events(self) -> int:
        """Get number of upcoming events."""
        return sum(1 for e in self.events if e.is_upcoming)
    
    @property
    def cancelled_events(self) -> int:
        """Get number of cancelled events."""
        return sum(1 for e in self.events if e.status == EventStatus.CANCELLED)
    
    @property
    def deleted_events(self) -> int:
        """Rounds removed from the calendar (count as done for progress)."""
        return sum(1 for e in self.events if e.status == EventStatus.DELETED)
    
    @property
    def rounds_counted_toward_progress(self) -> int:
        """GPs counted as 'made' for the bar: completed plus cancelled (not removed slots)."""
        return self.completed_events + self.cancelled_events
    
    @property
    def completion_percentage(self) -> float:
        """Season progress: (completed + cancelled) / scheduled rounds × 100. Removed rounds excluded."""
        if self.scheduled_rounds == 0:
            return 0.0
        return (self.rounds_counted_toward_progress / self.scheduled_rounds) * 100
    
    @property
    def is_complete(self) -> bool:
        """True when every scheduled round is completed or cancelled (no upcoming)."""
        if self.scheduled_rounds == 0:
            return False
        return self.rounds_counted_toward_progress == self.scheduled_rounds
    
    def get_event_by_round(self, round_number: int) -> Optional[Event]:
        """Get event by round number."""
        for event in self.events:
            if event.round_number == round_number:
                return event
        return None
    
    def get_events_by_status(self, status: EventStatus) -> List[Event]:
        """Get all events with a specific status."""
        return [e for e in self.events if e.status == status]
    
    def get_events_by_country(self, country: str) -> List[Event]:
        """Get all events in a specific country."""
        return [e for e in self.events if e.country.lower() == country.lower()]
    
    def add_event(self, event: Event) -> None:
        """Add an event to the season."""
        # Check for duplicate round numbers
        if any(e.round_number == event.round_number for e in self.events):
            raise ValueError(f"Round {event.round_number} already exists")
        self.events.append(event)
        # Keep events sorted by round number
        self.events.sort(key=lambda e: e.round_number)
    
    def to_dict(self) -> dict:
        """Convert season to dictionary."""
        return {
            'year': self.year,
            'events': [e.to_dict() for e in self.events],
            'champion': self.champion,
            'constructor_champion': self.constructor_champion
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Season':
        """Create Season instance from dictionary."""
        season = cls(
            year=data['year'],
            champion=data.get('champion'),
            constructor_champion=data.get('constructor_champion')
        )
        for event_data in data.get('events', []):
            season.events.append(Event.from_dict(event_data))
        season.events.sort(key=lambda e: e.round_number)
        return season
