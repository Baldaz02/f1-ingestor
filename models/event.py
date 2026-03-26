"""Event model representing a Formula 1 Grand Prix event."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EventStatus(Enum):
    """Status of an F1 event."""
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    DELETED = "deleted"  # Removed from the calendar; excluded from season totals / progress bar


@dataclass
class Event:
    """
    Represents a Formula 1 Grand Prix event.
    
    Attributes:
        id: Unique identifier for the event
        name: Display title (short name when imported from FastF1 ``EventName``)
        country: Country where the event takes place
        circuit: Name of the racing circuit
        city: City where the circuit is located
        date: Date of the main race
        round_number: Round number in the season
        status: Current status of the event
        winner: Name of the race winner (if completed)
        pole_position: Driver who secured pole position
        fastest_lap: Driver with the fastest lap
        flag_emoji: Country flag emoji
        official_name: Long / official title when available (e.g. FastF1 ``OfficialEventName``); UI uses ``name`` for display (short title).
    """
    id: str
    name: str
    country: str
    circuit: str
    city: str
    date: datetime
    round_number: int
    status: EventStatus = EventStatus.UPCOMING
    winner: Optional[str] = None
    pole_position: Optional[str] = None
    fastest_lap: Optional[str] = None
    flag_emoji: str = "🏁"
    official_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate event data after initialization."""
        if self.round_number < 1:
            raise ValueError("Round number must be positive")
        if not self.name:
            raise ValueError("Event name cannot be empty")
    
    @property
    def formatted_date(self) -> str:
        """Return formatted date string."""
        return self.date.strftime("%d %B %Y")
    
    @property
    def month_day(self) -> str:
        """Return short month-day format."""
        return self.date.strftime("%d %b")
    
    @property
    def is_completed(self) -> bool:
        """Check if event is completed."""
        return self.status == EventStatus.COMPLETED
    
    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming."""
        return self.status == EventStatus.UPCOMING
    
    @property
    def is_deleted(self) -> bool:
        """Round removed from the schedule (excluded from season round counts and bar)."""
        return self.status == EventStatus.DELETED
    
    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'circuit': self.circuit,
            'city': self.city,
            'date': self.date.isoformat(),
            'round_number': self.round_number,
            'status': self.status.value,
            'winner': self.winner,
            'pole_position': self.pole_position,
            'fastest_lap': self.fastest_lap,
            'flag_emoji': self.flag_emoji,
            'official_name': self.official_name,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create Event instance from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            country=data['country'],
            circuit=data['circuit'],
            city=data['city'],
            date=datetime.fromisoformat(data['date']),
            round_number=data['round_number'],
            status=EventStatus(data.get('status', 'upcoming')),
            winner=data.get('winner'),
            pole_position=data.get('pole_position'),
            fastest_lap=data.get('fastest_lap'),
            flag_emoji=data.get('flag_emoji', '🏁'),
            official_name=data.get('official_name'),
        )
