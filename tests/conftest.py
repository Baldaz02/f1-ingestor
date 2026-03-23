"""Pytest configuration and fixtures for F1 Ingestor tests."""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.event import Event, EventStatus
from models.season import Season
from models.data_store import DataStore
from controllers.season_controller import SeasonController


@pytest.fixture
def sample_event():
    """Create a sample completed event."""
    return Event(
        id="2024-R01",
        name="Australian Grand Prix",
        country="Australia",
        circuit="Albert Park Circuit",
        city="Melbourne",
        date=datetime(2024, 3, 24),
        round_number=1,
        status=EventStatus.COMPLETED,
        winner="Max Verstappen",
        pole_position="Charles Leclerc",
        fastest_lap="Lando Norris",
        flag_emoji="🇦🇺"
    )


@pytest.fixture
def sample_upcoming_event():
    """Create a sample upcoming event."""
    return Event(
        id="2026-R01",
        name="Australian Grand Prix",
        country="Australia",
        circuit="Albert Park Circuit",
        city="Melbourne",
        date=datetime(2026, 3, 15),
        round_number=1,
        status=EventStatus.UPCOMING,
        flag_emoji="🇦🇺"
    )


@pytest.fixture
def sample_season():
    """Create a sample season with events."""
    season = Season(year=2024, champion="Max Verstappen", constructor_champion="Red Bull Racing")
    
    for i in range(1, 6):
        status = EventStatus.COMPLETED if i <= 3 else EventStatus.UPCOMING
        event = Event(
            id=f"2024-R{i:02d}",
            name=f"Grand Prix {i}",
            country="Test Country",
            circuit=f"Circuit {i}",
            city=f"City {i}",
            date=datetime(2024, 3, i * 7),
            round_number=i,
            status=status,
            winner="Max Verstappen" if status == EventStatus.COMPLETED else None
        )
        season.add_event(event)
    
    return season


@pytest.fixture
def data_store():
    """Create a data store instance."""
    return DataStore()


@pytest.fixture
def controller():
    """Create a controller instance."""
    return SeasonController()


@pytest.fixture
def full_season():
    """Create a full season with all events completed."""
    season = Season(year=2024, champion="Max Verstappen", constructor_champion="Red Bull Racing")
    
    events_data = [
        ("Bahrain", "Bahrain", "Sakhir", 3, 2),
        ("Saudi Arabian", "Saudi Arabia", "Jeddah", 3, 9),
        ("Australian", "Australia", "Melbourne", 3, 24),
        ("Japanese", "Japan", "Suzuka", 4, 7),
        ("Chinese", "China", "Shanghai", 4, 21),
    ]
    
    for i, (name, country, city, month, day) in enumerate(events_data, 1):
        event = Event(
            id=f"2024-R{i:02d}",
            name=f"{name} Grand Prix",
            country=country,
            circuit=f"{city} Circuit",
            city=city,
            date=datetime(2024, month, day),
            round_number=i,
            status=EventStatus.COMPLETED,
            winner="Max Verstappen",
            pole_position="Max Verstappen",
            fastest_lap="Max Verstappen"
        )
        season.add_event(event)
    
    return season
