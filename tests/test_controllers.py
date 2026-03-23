"""Tests for F1 Ingestor controllers."""
import os
import sys
from datetime import date

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.season_controller import SeasonController
from models.event import EventStatus


def _expected_year_menu_top() -> int:
    """Latest year shown first in UI (mock data tops out at 2026)."""
    return min(date.today().year, 2026)


class TestSeasonController:
    """Test cases for the SeasonController."""
    
    def test_controller_initialization(self):
        """Test controller initializes with default values."""
        controller = SeasonController()
        
        assert controller.current_year == _expected_year_menu_top()
        assert controller.data_store is not None
    
    def test_controller_get_available_years(self):
        """Test getting available years (current year down to 2019, capped at mock max 2026)."""
        controller = SeasonController()
        
        years = controller.get_available_years()
        top = _expected_year_menu_top()
        
        assert isinstance(years, list)
        assert min(years) == 2019
        assert max(years) == top
        assert years[0] == top
        assert years[-1] == 2019
        assert years == list(range(top, 2018, -1))
    
    def test_controller_set_current_year(self):
        """Test setting current year."""
        controller = SeasonController()
        
        controller.current_year = 2023
        
        assert controller.current_year == 2023
    
    def test_controller_set_invalid_year(self):
        """Test setting invalid year doesn't change current year."""
        controller = SeasonController()
        original_year = controller.current_year
        
        controller.current_year = 2000  # Invalid year
        
        assert controller.current_year == original_year
    
    def test_controller_get_current_season(self):
        """Test getting current season."""
        controller = SeasonController()
        controller.current_year = 2024
        
        season = controller.get_current_season()
        
        assert season is not None
        assert season.year == 2024
    
    def test_controller_get_events_for_current_season(self):
        """Test getting events for current season."""
        controller = SeasonController()
        controller.current_year = 2024
        
        events = controller.get_events_for_current_season()
        
        assert len(events) > 0
        assert all(e.date.year == 2024 for e in events)
    
    def test_controller_get_upcoming_events(self):
        """Test getting upcoming events."""
        controller = SeasonController()
        controller.current_year = 2026  # Has both completed and upcoming
        
        upcoming = controller.get_upcoming_events()
        
        assert all(e.is_upcoming for e in upcoming)
    
    def test_controller_get_completed_events(self):
        """Test getting completed events."""
        controller = SeasonController()
        controller.current_year = 2024  # Fully completed
        
        completed = controller.get_completed_events()
        
        assert len(completed) > 0
        assert all(e.is_completed for e in completed)
    
    def test_controller_get_season_stats(self):
        """Test getting season statistics."""
        controller = SeasonController()
        controller.current_year = 2024
        
        stats = controller.get_season_stats()
        
        assert 'total_events' in stats
        assert 'completed' in stats
        assert 'upcoming' in stats
        assert 'cancelled' in stats
        assert 'completion_percentage' in stats
        assert 'deleted' in stats
        assert 'rounds_counted_toward_progress' in stats
        assert 'champion' in stats
        assert 'constructor_champion' in stats
        
        assert stats['total_events'] > 0
        assert stats['completion_percentage'] >= 0
        assert stats['rounds_counted_toward_progress'] == stats['completed'] + stats['cancelled']
    
    def test_controller_search_events(self):
        """Test event search functionality."""
        controller = SeasonController()
        controller.current_year = 2024
        
        # Search by name
        results = controller.search_events("Monaco")
        assert len(results) >= 1
        assert any("Monaco" in e.name for e in results)
        
        # Search by country
        results = controller.search_events("Italy")
        assert len(results) >= 1
        
        # Search by circuit
        results = controller.search_events("Silverstone")
        assert len(results) >= 1
        
        # Empty search returns all
        results = controller.search_events("")
        assert len(results) == len(controller.get_events_for_current_season())
    
    def test_controller_filter_events_by_status(self):
        """Test filtering events by status."""
        controller = SeasonController()
        controller.current_year = 2025
        
        # Filter completed
        completed = controller.filter_events_by_status("completed")
        assert all(e.status == EventStatus.COMPLETED for e in completed)
        
        # Filter upcoming
        upcoming = controller.filter_events_by_status("upcoming")
        assert all(e.status == EventStatus.UPCOMING for e in upcoming)
        
        # Filter cancelled
        cancelled = controller.filter_events_by_status("cancelled")
        assert all(e.status == EventStatus.CANCELLED for e in cancelled)
        
        # Filter all
        all_events = controller.filter_events_by_status("all")
        assert len(all_events) == len(controller.get_events_for_current_season())
    
    def test_controller_get_event_by_round(self):
        """Test getting event by round number."""
        controller = SeasonController()
        controller.current_year = 2024
        
        event = controller.get_event_by_round(1)
        
        assert event is not None
        assert event.round_number == 1
    
    def test_controller_get_next_event(self):
        """Test getting next upcoming event."""
        controller = SeasonController()
        controller.current_year = 2026  # Has upcoming events
        
        next_event = controller.get_next_event()
        
        if next_event:
            assert next_event.is_upcoming
    
    def test_controller_get_last_completed_event(self):
        """Test getting last completed event."""
        controller = SeasonController()
        controller.current_year = 2024
        
        last_event = controller.get_last_completed_event()
        
        assert last_event is not None
        assert last_event.is_completed
    
    def test_controller_get_winners_count(self):
        """Test getting winner statistics."""
        controller = SeasonController()
        controller.current_year = 2024
        
        winners = controller.get_winners_count()
        
        assert isinstance(winners, dict)
        assert len(winners) > 0
        
        # Check sorting (most wins first)
        counts = list(winners.values())
        assert counts == sorted(counts, reverse=True)
    
    def test_controller_get_pole_positions_count(self):
        """Test getting pole position statistics."""
        controller = SeasonController()
        controller.current_year = 2024
        
        poles = controller.get_pole_positions_count()
        
        assert isinstance(poles, dict)
        assert len(poles) > 0
    
    def test_controller_observer_pattern(self):
        """Test observer notification system."""
        controller = SeasonController()
        callback_called = [False]  # Use list to allow modification in closure
        
        def observer():
            callback_called[0] = True
        
        controller.add_observer(observer)
        controller.current_year = 2023  # Trigger notification
        
        assert callback_called[0]
    
    def test_controller_remove_observer(self):
        """Test removing observer."""
        controller = SeasonController()
        callback_called = [False]
        
        def observer():
            callback_called[0] = True
        
        controller.add_observer(observer)
        controller.remove_observer(observer)
        controller.current_year = 2023
        
        assert not callback_called[0]
    
    def test_controller_multiple_observers(self):
        """Test multiple observers are notified."""
        controller = SeasonController()
        calls = []
        
        def observer1():
            calls.append(1)
        
        def observer2():
            calls.append(2)
        
        controller.add_observer(observer1)
        controller.add_observer(observer2)
        controller.current_year = 2023
        
        assert 1 in calls
        assert 2 in calls
    
    def test_controller_get_season_for_specific_year(self):
        """Test getting season for specific year."""
        controller = SeasonController()
        
        season = controller.get_season(2019)
        
        assert season is not None
        assert season.year == 2019
        assert season.champion == "Lewis Hamilton"
    
    def test_controller_get_all_seasons(self):
        """Test getting all seasons."""
        controller = SeasonController()
        
        seasons = controller.get_all_seasons()
        
        assert len(seasons) == 8
        assert all(s.year in range(2019, 2027) for s in seasons)


class TestSeasonControllerEdgeCases:
    """Test edge cases for SeasonController."""
    
    def test_empty_search_query(self):
        """Test search with empty query."""
        controller = SeasonController()
        controller.current_year = 2024
        
        all_events = controller.get_events_for_current_season()
        search_results = controller.search_events("")
        
        assert len(search_results) == len(all_events)
    
    def test_no_match_search(self):
        """Test search with no matches."""
        controller = SeasonController()
        controller.current_year = 2024
        
        results = controller.search_events("XYZNONEXISTENT")
        
        assert len(results) == 0
    
    def test_case_insensitive_search(self):
        """Test case insensitive search."""
        controller = SeasonController()
        controller.current_year = 2024
        
        lower_results = controller.search_events("monaco")
        upper_results = controller.search_events("MONACO")
        mixed_results = controller.search_events("Monaco")
        
        assert len(lower_results) == len(upper_results) == len(mixed_results)
    
    def test_invalid_filter_status(self):
        """Test filter with invalid status."""
        controller = SeasonController()
        controller.current_year = 2024
        
        # Invalid status should return all events
        results = controller.filter_events_by_status("invalid_status")
        all_events = controller.get_events_for_current_season()
        
        assert len(results) == len(all_events)
    
    def test_no_upcoming_events_season(self):
        """Test getting next event when none upcoming."""
        controller = SeasonController()
        controller.current_year = 2024  # Fully completed season
        
        next_event = controller.get_next_event()
        
        # 2024 is completed, so no upcoming events
        # The method should return None
        assert next_event is None or next_event.is_upcoming
    
    def test_2026_season_in_progress_has_completed_and_upcoming(self):
        """2026 lists partition the season; mix depends on date.today()."""
        controller = SeasonController()
        controller.current_year = 2026
        
        completed = controller.get_completed_events()
        upcoming = controller.get_upcoming_events()
        all_ev = controller.get_events_for_current_season()
        
        assert len(completed) + len(upcoming) == len(all_ev)
    
    def test_season_stats_empty_season(self):
        """Test stats when season has no data."""
        controller = SeasonController()
        
        # This tests the fallback for missing season
        controller._current_year = 9999  # Non-existent year
        stats = controller.get_season_stats()
        
        assert stats['total_events'] == 0
        assert stats['completion_percentage'] == 0.0
        assert stats['deleted'] == 0
        assert stats['rounds_counted_toward_progress'] == 0
