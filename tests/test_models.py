"""Tests for F1 Ingestor models."""
import os
import sys
from datetime import date, datetime

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.event import Event, EventStatus
from models.season import Season
from models.data_store import MIN_SEASON_YEAR, DataStore


class TestEvent:
    """Test cases for the Event model."""
    
    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(
            id="2024-R01",
            name="Australian Grand Prix",
            country="Australia",
            circuit="Albert Park Circuit",
            city="Melbourne",
            date=datetime(2024, 3, 24),
            round_number=1
        )
        
        assert event.id == "2024-R01"
        assert event.name == "Australian Grand Prix"
        assert event.country == "Australia"
        assert event.circuit == "Albert Park Circuit"
        assert event.city == "Melbourne"
        assert event.round_number == 1
        assert event.status == EventStatus.UPCOMING
    
    def test_event_with_results(self):
        """Test event creation with results."""
        event = Event(
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
            fastest_lap="Lando Norris"
        )
        
        assert event.is_completed
        assert not event.is_upcoming
        assert event.winner == "Max Verstappen"
        assert event.pole_position == "Charles Leclerc"
        assert event.fastest_lap == "Lando Norris"
    
    def test_event_formatted_date(self):
        """Test date formatting."""
        event = Event(
            id="2024-R01",
            name="Test GP",
            country="Test",
            circuit="Test Circuit",
            city="Test City",
            date=datetime(2024, 3, 24),
            round_number=1
        )
        
        assert event.formatted_date == "24 March 2024"
        assert event.month_day == "24 Mar"
    
    def test_event_invalid_round_number(self):
        """Test that invalid round number raises error."""
        with pytest.raises(ValueError, match="Round number must be positive"):
            Event(
                id="2024-R00",
                name="Test GP",
                country="Test",
                circuit="Test Circuit",
                city="Test City",
                date=datetime(2024, 3, 24),
                round_number=0
            )
    
    def test_event_empty_name(self):
        """Test that empty name raises error."""
        with pytest.raises(ValueError, match="Event name cannot be empty"):
            Event(
                id="2024-R01",
                name="",
                country="Test",
                circuit="Test Circuit",
                city="Test City",
                date=datetime(2024, 3, 24),
                round_number=1
            )
    
    def test_event_to_dict(self):
        """Test event serialization to dictionary."""
        event = Event(
            id="2024-R01",
            name="Australian Grand Prix",
            country="Australia",
            circuit="Albert Park Circuit",
            city="Melbourne",
            date=datetime(2024, 3, 24),
            round_number=1,
            flag_emoji="🇦🇺"
        )
        
        data = event.to_dict()
        
        assert data['id'] == "2024-R01"
        assert data['name'] == "Australian Grand Prix"
        assert data['country'] == "Australia"
        assert data['flag_emoji'] == "🇦🇺"
        assert data['status'] == "upcoming"
        assert data.get("official_name") is None
    
    def test_event_from_dict(self):
        """Test event creation from dictionary."""
        data = {
            'id': "2024-R01",
            'name': "Australian Grand Prix",
            'country': "Australia",
            'circuit': "Albert Park Circuit",
            'city': "Melbourne",
            'date': "2024-03-24T00:00:00",
            'round_number': 1,
            'status': "completed",
            'winner': "Max Verstappen",
            'flag_emoji': "🇦🇺"
        }
        
        event = Event.from_dict(data)
        
        assert event.id == "2024-R01"
        assert event.name == "Australian Grand Prix"
        assert event.status == EventStatus.COMPLETED
        assert event.winner == "Max Verstappen"


class TestSeason:
    """Test cases for the Season model."""
    
    def test_season_creation(self):
        """Test basic season creation."""
        season = Season(year=2024)
        
        assert season.year == 2024
        assert season.total_events == 0
        assert season.events == []
        assert season.champion is None
    
    def test_season_invalid_year(self):
        """Test that invalid year raises error."""
        with pytest.raises(ValueError, match="F1 started in 1950"):
            Season(year=1949)
    
    def test_season_with_events(self):
        """Test season with events."""
        season = Season(year=2024)
        
        event1 = Event(
            id="2024-R01", name="GP 1", country="Test",
            circuit="Circuit 1", city="City 1",
            date=datetime(2024, 3, 1), round_number=1,
            status=EventStatus.COMPLETED
        )
        event2 = Event(
            id="2024-R02", name="GP 2", country="Test",
            circuit="Circuit 2", city="City 2",
            date=datetime(2024, 3, 15), round_number=2,
            status=EventStatus.UPCOMING
        )
        
        season.add_event(event1)
        season.add_event(event2)
        
        assert season.total_events == 2
        assert season.completed_events == 1
        assert season.upcoming_events == 1
    
    def test_season_completion_percentage(self):
        """Test season completion calculation."""
        season = Season(year=2024)
        
        for i in range(1, 11):
            status = EventStatus.COMPLETED if i <= 6 else EventStatus.UPCOMING
            event = Event(
                id=f"2024-R{i:02d}", name=f"GP {i}", country="Test",
                circuit=f"Circuit {i}", city=f"City {i}",
                date=datetime(2024, 3, i), round_number=i,
                status=status
            )
            season.add_event(event)
        
        assert season.completion_percentage == 60.0
        assert not season.is_complete
    
    def test_season_deleted_excluded_from_scheduled_and_progress(self):
        """Removed rounds are not in scheduled totals; bar uses completed + cancelled only."""
        season = Season(year=2024)
        for i in range(1, 11):
            if i <= 5:
                status = EventStatus.COMPLETED
            elif i == 6:
                status = EventStatus.DELETED
            else:
                status = EventStatus.UPCOMING
            event = Event(
                id=f"2024-R{i:02d}", name=f"GP {i}", country="Test",
                circuit=f"Circuit {i}", city=f"City {i}",
                date=datetime(2024, 3, i), round_number=i,
                status=status,
            )
            season.add_event(event)
        assert season.deleted_events == 1
        assert season.completed_events == 5
        assert season.scheduled_rounds == 9
        assert season.rounds_counted_toward_progress == 5
        assert season.completion_percentage == (5 / 9) * 100
    
    def test_season_duplicate_round(self):
        """Test that duplicate round numbers raise error."""
        season = Season(year=2024)
        
        event1 = Event(
            id="2024-R01", name="GP 1", country="Test",
            circuit="Circuit 1", city="City 1",
            date=datetime(2024, 3, 1), round_number=1
        )
        event2 = Event(
            id="2024-R01-dup", name="GP 1 Dup", country="Test",
            circuit="Circuit 1", city="City 1",
            date=datetime(2024, 3, 8), round_number=1
        )
        
        season.add_event(event1)
        
        with pytest.raises(ValueError, match="Round 1 already exists"):
            season.add_event(event2)
    
    def test_season_get_event_by_round(self):
        """Test getting event by round number."""
        season = Season(year=2024)
        
        event = Event(
            id="2024-R05", name="Monaco GP", country="Monaco",
            circuit="Circuit de Monaco", city="Monte Carlo",
            date=datetime(2024, 5, 26), round_number=5
        )
        season.add_event(event)
        
        found = season.get_event_by_round(5)
        assert found is not None
        assert found.name == "Monaco GP"
        
        not_found = season.get_event_by_round(99)
        assert not_found is None
    
    def test_season_get_events_by_status(self):
        """Test filtering events by status."""
        season = Season(year=2024)
        
        for i in range(1, 6):
            status = EventStatus.COMPLETED if i <= 3 else EventStatus.UPCOMING
            event = Event(
                id=f"2024-R{i:02d}", name=f"GP {i}", country="Test",
                circuit=f"Circuit {i}", city=f"City {i}",
                date=datetime(2024, 3, i), round_number=i,
                status=status
            )
            season.add_event(event)
        
        completed = season.get_events_by_status(EventStatus.COMPLETED)
        upcoming = season.get_events_by_status(EventStatus.UPCOMING)
        
        assert len(completed) == 3
        assert len(upcoming) == 2
    
    def test_season_get_events_by_country(self):
        """Test filtering events by country."""
        season = Season(year=2024)
        
        event1 = Event(
            id="2024-R01", name="Australian GP", country="Australia",
            circuit="Albert Park", city="Melbourne",
            date=datetime(2024, 3, 24), round_number=1
        )
        event2 = Event(
            id="2024-R02", name="Italian GP", country="Italy",
            circuit="Monza", city="Monza",
            date=datetime(2024, 9, 1), round_number=2
        )
        event3 = Event(
            id="2024-R03", name="Emilia Romagna GP", country="Italy",
            circuit="Imola", city="Imola",
            date=datetime(2024, 5, 19), round_number=3
        )
        
        season.add_event(event1)
        season.add_event(event2)
        season.add_event(event3)
        
        italy_events = season.get_events_by_country("Italy")
        australia_events = season.get_events_by_country("AUSTRALIA")
        
        assert len(italy_events) == 2
        assert len(australia_events) == 1
    
    def test_season_to_dict(self):
        """Test season serialization."""
        season = Season(
            year=2024,
            champion="Max Verstappen",
            constructor_champion="Red Bull Racing"
        )
        
        data = season.to_dict()
        
        assert data['year'] == 2024
        assert data['champion'] == "Max Verstappen"
        assert data['constructor_champion'] == "Red Bull Racing"
        assert data['events'] == []


class TestDataStore:
    """Test cases for the DataStore."""
    
    def test_data_store_initialization(self):
        """Selectable years are current calendar year … 2019; independent of stored seasons."""
        store = DataStore()
        top = max(date.today().year, MIN_SEASON_YEAR)
        years = store.get_available_years()
        assert years[0] == top
        assert years[-1] == MIN_SEASON_YEAR
        assert set(years) == set(range(MIN_SEASON_YEAR, top + 1))
        
        store.populate_mock_f1_data()
        assert store.get_available_years() == years
    
    def test_data_store_get_season(self):
        """Test getting a specific season."""
        store = DataStore()
        store.populate_mock_f1_data()
        
        season = store.get_season(2024)
        
        assert season is not None
        assert season.year == 2024
        assert season.total_events > 0
    
    def test_data_store_invalid_season(self):
        """Test getting non-existent season."""
        store = DataStore()
        
        season = store.get_season(2000)
        
        assert season is None
    
    def test_data_store_2019_season(self):
        """Test 2019 season has correct data."""
        store = DataStore()
        store.populate_mock_f1_data()
        
        season = store.get_season(2019)
        
        assert season is not None
        assert season.total_events == 21
        assert season.champion == "Lewis Hamilton"
        assert season.constructor_champion == "Mercedes"
    
    def test_data_store_2023_season(self):
        """Test 2023 season has correct data."""
        store = DataStore()
        store.populate_mock_f1_data()
        
        season = store.get_season(2023)
        
        assert season is not None
        assert season.total_events == 22
        assert season.champion == "Max Verstappen"
        assert season.constructor_champion == "Red Bull Racing"
    
    def test_data_store_2026_season(self):
        """2026 completion split follows current date (mock calendar)."""
        store = DataStore()
        store.populate_mock_f1_data()
        
        season = store.get_season(2026)
        
        assert season is not None
        assert season.total_events == 24
        assert season.champion is None  # Season still open in mock
        completed = [e for e in season.events if e.is_completed]
        upcoming = [e for e in season.events if e.is_upcoming]
        assert len(completed) + len(upcoming) == 24
        for e in completed:
            assert e.winner
    
    def test_data_store_events_have_required_fields(self):
        """Test all events have required fields."""
        store = DataStore()
        store.populate_mock_f1_data()
        
        for season in store.get_all_seasons():
            for event in season.events:
                assert event.id
                assert event.name
                assert event.country
                assert event.circuit
                assert event.city
                assert event.date
                assert event.round_number > 0
                assert event.flag_emoji
    
    def test_data_store_completed_events_have_winners(self):
        """Test completed events have winner information."""
        store = DataStore()
        store.populate_mock_f1_data()
        
        for year in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
            season = store.get_season(year)
            completed = season.get_events_by_status(EventStatus.COMPLETED)
            
            for event in completed:
                assert event.winner, f"Event {event.name} missing winner"


class TestEventStatus:
    """Test cases for EventStatus enum."""
    
    def test_status_values(self):
        """Test all status values exist."""
        assert EventStatus.UPCOMING.value == "upcoming"
        assert EventStatus.COMPLETED.value == "completed"
        assert EventStatus.CANCELLED.value == "cancelled"
        assert EventStatus.IN_PROGRESS.value == "in_progress"
    
    def test_status_from_string(self):
        """Test creating status from string."""
        status = EventStatus("completed")
        assert status == EventStatus.COMPLETED
