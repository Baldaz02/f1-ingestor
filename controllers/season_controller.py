"""Controller for managing F1 season data and interactions."""
from datetime import date
from typing import Callable, Dict, List, Optional
from models.data_store import DataStore
from models.season import Season
from models.event import Event, EventStatus


class SeasonController:
    """
    Controller responsible for managing season data and coordinating
    between the model and view layers.
    """
    
    def __init__(self):
        """Initialize the controller with a data store."""
        self._data_store = DataStore()
        years = self._data_store.get_available_years()
        # Default season = newest available year, or calendar year when the store is empty.
        self._current_year: int = years[0] if years else date.today().year
        self._observers: List[Callable] = []
    
    @property
    def data_store(self) -> DataStore:
        """Get the data store."""
        return self._data_store
    
    @property
    def current_year(self) -> int:
        """Get the currently selected year."""
        return self._current_year
    
    @current_year.setter
    def current_year(self, year: int) -> None:
        """Set the current year and notify observers."""
        if year in self.get_available_years():
            self._current_year = year
            self._notify_observers()
    
    def add_observer(self, callback: Callable) -> None:
        """Add an observer callback."""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable) -> None:
        """Remove an observer callback."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify_observers(self) -> None:
        """Notify all observers of data changes."""
        for callback in self._observers:
            callback()
    
    def notify_data_changed(self) -> None:
        """Notify observers after model updates (e.g. from UI after a background import)."""
        self._notify_observers()
    
    def import_current_season_from_fastf1(self) -> None:
        """Replace the current season with events from the FastF1 schedule (no observer call)."""
        self._data_store.replace_season_from_fastf1(self._current_year)
    
    def get_available_years(self) -> List[int]:
        """Get list of available season years."""
        return self._data_store.get_available_years()
    
    def get_current_season(self) -> Optional[Season]:
        """Get the currently selected season."""
        return self._data_store.get_season(self._current_year)
    
    def get_season(self, year: int) -> Optional[Season]:
        """Get a specific season by year."""
        return self._data_store.get_season(year)
    
    def get_all_seasons(self) -> List[Season]:
        """Get all available seasons."""
        return self._data_store.get_all_seasons()
    
    def get_events_for_current_season(self) -> List[Event]:
        """Get all events for the current season."""
        season = self.get_current_season()
        if season:
            return season.events
        return []
    
    def get_upcoming_events(self) -> List[Event]:
        """Get upcoming events for the current season."""
        season = self.get_current_season()
        if season:
            return season.get_events_by_status(EventStatus.UPCOMING)
        return []
    
    def get_completed_events(self) -> List[Event]:
        """Get completed events for the current season."""
        season = self.get_current_season()
        if season:
            return season.get_events_by_status(EventStatus.COMPLETED)
        return []
    
    def get_season_stats(self) -> Dict:
        """Get statistics for the current season."""
        season = self.get_current_season()
        if not season:
            return {
                'total_events': 0,
                'completed': 0,
                'upcoming': 0,
                'cancelled': 0,
                'deleted': 0,
                'rounds_counted_toward_progress': 0,
                'completion_percentage': 0.0,
                'champion': None,
                'constructor_champion': None
            }
        
        return {
            'total_events': season.scheduled_rounds,
            'completed': season.completed_events,
            'upcoming': season.upcoming_events,
            'cancelled': season.cancelled_events,
            'deleted': season.deleted_events,
            'rounds_counted_toward_progress': season.rounds_counted_toward_progress,
            'completion_percentage': season.completion_percentage,
            'champion': season.champion,
            'constructor_champion': season.constructor_champion
        }
    
    def search_events(self, query: str) -> List[Event]:
        """Search events by name, country, or circuit."""
        events = self.get_events_for_current_season()
        query = query.lower().strip()
        
        if not query:
            return events
        
        return [
            event for event in events
            if query in event.name.lower()
            or query in event.country.lower()
            or query in event.circuit.lower()
            or query in event.city.lower()
        ]
    
    def filter_events_by_status(self, status: str) -> List[Event]:
        """Filter events by status string."""
        events = self.get_events_for_current_season()
        
        if status.lower() == 'all':
            return events
        
        try:
            event_status = EventStatus(status.lower())
            return [e for e in events if e.status == event_status]
        except ValueError:
            return events
    
    def get_event_by_round(self, round_number: int) -> Optional[Event]:
        """Get an event by its round number."""
        season = self.get_current_season()
        if season:
            return season.get_event_by_round(round_number)
        return None
    
    def get_next_event(self) -> Optional[Event]:
        """Get the next upcoming event."""
        upcoming = self.get_upcoming_events()
        if upcoming:
            return upcoming[0]
        return None
    
    def get_last_completed_event(self) -> Optional[Event]:
        """Get the last completed event."""
        completed = self.get_completed_events()
        if completed:
            return completed[-1]
        return None
    
    def get_winners_count(self) -> Dict[str, int]:
        """Get count of wins per driver for current season."""
        events = self.get_completed_events()
        winners: Dict[str, int] = {}
        
        for event in events:
            if event.winner:
                winners[event.winner] = winners.get(event.winner, 0) + 1
        
        return dict(sorted(winners.items(), key=lambda x: x[1], reverse=True))
    
    def get_pole_positions_count(self) -> Dict[str, int]:
        """Get count of pole positions per driver for current season."""
        events = self.get_completed_events()
        poles: Dict[str, int] = {}
        
        for event in events:
            if event.pole_position:
                poles[event.pole_position] = poles.get(event.pole_position, 0) + 1
        
        return dict(sorted(poles.items(), key=lambda x: x[1], reverse=True))
