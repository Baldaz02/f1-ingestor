"""Data store with mock F1 season data from 2019 to 2026."""
from datetime import date, datetime
from typing import Dict, List, Optional
from .event import Event, EventStatus
from .season import Season

# Oldest year shown in the season selector (range is built from today down to this).
MIN_SEASON_YEAR = 2019


class DataStore:
    """
    Central data store for F1 seasons and events.
    Contains mock data for seasons 2019-2026.
    Seasons 2019-2025 are fixed completed calendars. The 2026 season marks races on or
    before ``date.today()`` as completed (with mock results); later races stay upcoming.
    """
    
    # F1 Drivers for mock data
    DRIVERS = {
        2019: ["Lewis Hamilton", "Valtteri Bottas", "Max Verstappen", "Sebastian Vettel", 
               "Charles Leclerc", "Carlos Sainz", "Pierre Gasly", "Lando Norris"],
        2020: ["Lewis Hamilton", "Valtteri Bottas", "Max Verstappen", "Charles Leclerc",
               "Sebastian Vettel", "Carlos Sainz", "Pierre Gasly", "Daniel Ricciardo"],
        2021: ["Max Verstappen", "Lewis Hamilton", "Valtteri Bottas", "Sergio Perez",
               "Carlos Sainz", "Lando Norris", "Charles Leclerc", "Daniel Ricciardo"],
        2022: ["Max Verstappen", "Charles Leclerc", "Sergio Perez", "Carlos Sainz",
               "George Russell", "Lewis Hamilton", "Lando Norris", "Esteban Ocon"],
        2023: ["Max Verstappen", "Sergio Perez", "Lewis Hamilton", "Fernando Alonso",
               "Charles Leclerc", "Lando Norris", "Carlos Sainz", "George Russell"],
        2024: ["Max Verstappen", "Lando Norris", "Charles Leclerc", "Carlos Sainz",
               "Lewis Hamilton", "George Russell", "Oscar Piastri", "Fernando Alonso"],
        2025: ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc", "Lando Norris",
               "George Russell", "Carlos Sainz", "Oscar Piastri", "Fernando Alonso"],
        2026: ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc", "Lando Norris",
               "George Russell", "Carlos Sainz", "Oscar Piastri", "Kimi Antonelli"]
    }
    
    # World Champions
    CHAMPIONS = {
        2019: ("Lewis Hamilton", "Mercedes"),
        2020: ("Lewis Hamilton", "Mercedes"),
        2021: ("Max Verstappen", "Red Bull Racing"),
        2022: ("Max Verstappen", "Red Bull Racing"),
        2023: ("Max Verstappen", "Red Bull Racing"),
        2024: ("Max Verstappen", "Red Bull Racing"),
        2025: ("Max Verstappen", "Red Bull Racing"),
        2026: None,  # Season in progress
    }
    
    # Country flag emojis
    FLAGS = {
        "Australia": "🇦🇺", "Bahrain": "🇧🇭", "China": "🇨🇳", "Azerbaijan": "🇦🇿",
        "Spain": "🇪🇸", "Monaco": "🇲🇨", "Canada": "🇨🇦", "France": "🇫🇷",
        "Austria": "🇦🇹", "United Kingdom": "🇬🇧", "Germany": "🇩🇪", "Hungary": "🇭🇺",
        "Belgium": "🇧🇪", "Italy": "🇮🇹", "Singapore": "🇸🇬", "Russia": "🇷🇺",
        "Japan": "🇯🇵", "Mexico": "🇲🇽", "United States": "🇺🇸", "Brazil": "🇧🇷",
        "Abu Dhabi": "🇦🇪", "Netherlands": "🇳🇱", "Portugal": "🇵🇹", "Turkey": "🇹🇷",
        "Saudi Arabia": "🇸🇦", "Qatar": "🇶🇦", "Las Vegas": "🇺🇸", "Miami": "🇺🇸"
    }
    
    def __init__(self):
        """Initialize the data store with mock data."""
        self._seasons: Dict[int, Season] = {}
        self._load_mock_data()
    
    def _load_mock_data(self):
        """Load mock F1 data for seasons 2019-2026."""
        self._seasons[2019] = self._create_2019_season()
        self._seasons[2020] = self._create_2020_season()
        self._seasons[2021] = self._create_2021_season()
        self._seasons[2022] = self._create_2022_season()
        self._seasons[2023] = self._create_2023_season()
        self._seasons[2024] = self._create_2024_season()
        self._seasons[2025] = self._create_2025_season()
        self._seasons[2026] = self._create_2026_season()
    
    def get_season(self, year: int) -> Optional[Season]:
        """Get a season by year."""
        return self._seasons.get(year)
    
    def get_all_seasons(self) -> List[Season]:
        """Get all available seasons."""
        return sorted(self._seasons.values(), key=lambda s: s.year)
    
    def get_available_years(self) -> List[int]:
        """Newest first: ``date.today().year`` down to ``MIN_SEASON_YEAR``; only years we have data for."""
        if not self._seasons:
            return []
        top = max(date.today().year, MIN_SEASON_YEAR)
        return [y for y in range(top, MIN_SEASON_YEAR - 1, -1) if y in self._seasons]
    
    def _create_event(self, round_num: int, name: str, country: str, circuit: str, 
                      city: str, date: datetime, status: EventStatus = EventStatus.COMPLETED,
                      winner: str = None, pole: str = None, fastest: str = None) -> Event:
        """Helper to create an event."""
        return Event(
            id=f"{date.year}-R{round_num:02d}",
            name=name,
            country=country,
            circuit=circuit,
            city=city,
            date=date,
            round_number=round_num,
            status=status,
            winner=winner,
            pole_position=pole,
            fastest_lap=fastest,
            flag_emoji=self.FLAGS.get(country, "🏁")
        )
    
    def _create_2019_season(self) -> Season:
        """Create 2019 F1 season data."""
        drivers = self.DRIVERS[2019]
        champion_info = self.CHAMPIONS[2019]
        
        events = [
            self._create_event(1, "Australian Grand Prix", "Australia", "Albert Park Circuit", 
                             "Melbourne", datetime(2019, 3, 17), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Lewis Hamilton", "Valtteri Bottas"),
            self._create_event(2, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2019, 3, 31), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Charles Leclerc", "Charles Leclerc"),
            self._create_event(3, "Chinese Grand Prix", "China", "Shanghai International Circuit",
                             "Shanghai", datetime(2019, 4, 14), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Valtteri Bottas", "Pierre Gasly"),
            self._create_event(4, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit",
                             "Baku", datetime(2019, 4, 28), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Valtteri Bottas", "Charles Leclerc"),
            self._create_event(5, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2019, 5, 12), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Valtteri Bottas", "Lewis Hamilton"),
            self._create_event(6, "Monaco Grand Prix", "Monaco", "Circuit de Monaco",
                             "Monte Carlo", datetime(2019, 5, 26), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Pierre Gasly"),
            self._create_event(7, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve",
                             "Montreal", datetime(2019, 6, 9), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Sebastian Vettel", "Valtteri Bottas"),
            self._create_event(8, "French Grand Prix", "France", "Circuit Paul Ricard",
                             "Le Castellet", datetime(2019, 6, 23), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Sebastian Vettel"),
            self._create_event(9, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2019, 6, 30), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Max Verstappen"),
            self._create_event(10, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2019, 7, 14), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Valtteri Bottas", "Lewis Hamilton"),
            self._create_event(11, "German Grand Prix", "Germany", "Hockenheimring",
                             "Hockenheim", datetime(2019, 7, 28), EventStatus.COMPLETED,
                             "Max Verstappen", "Lewis Hamilton", "Max Verstappen"),
            self._create_event(12, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2019, 8, 4), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Max Verstappen", "Max Verstappen"),
            self._create_event(13, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2019, 9, 1), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Sebastian Vettel"),
            self._create_event(14, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2019, 9, 8), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Lewis Hamilton"),
            self._create_event(15, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit",
                             "Singapore", datetime(2019, 9, 22), EventStatus.COMPLETED,
                             "Sebastian Vettel", "Charles Leclerc", "Kevin Magnussen"),
            self._create_event(16, "Russian Grand Prix", "Russia", "Sochi Autodrom",
                             "Sochi", datetime(2019, 9, 29), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Charles Leclerc", "Lewis Hamilton"),
            self._create_event(17, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course",
                             "Suzuka", datetime(2019, 10, 13), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Sebastian Vettel", "Lewis Hamilton"),
            self._create_event(18, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez",
                             "Mexico City", datetime(2019, 10, 27), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Charles Leclerc", "Charles Leclerc"),
            self._create_event(19, "United States Grand Prix", "United States", "Circuit of the Americas",
                             "Austin", datetime(2019, 11, 3), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Valtteri Bottas", "Charles Leclerc"),
            self._create_event(20, "Brazilian Grand Prix", "Brazil", "Autódromo José Carlos Pace",
                             "São Paulo", datetime(2019, 11, 17), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(21, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2019, 12, 1), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Lewis Hamilton"),
        ]
        
        season = Season(year=2019, champion=champion_info[0], constructor_champion=champion_info[1])
        season.events = events
        return season
    
    def _create_2020_season(self) -> Season:
        """Create 2020 F1 season data (COVID-affected season)."""
        drivers = self.DRIVERS[2020]
        champion_info = self.CHAMPIONS[2020]
        
        events = [
            self._create_event(1, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2020, 7, 5), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Valtteri Bottas", "Lando Norris"),
            self._create_event(2, "Styrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2020, 7, 12), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Carlos Sainz"),
            self._create_event(3, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2020, 7, 19), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Lewis Hamilton"),
            self._create_event(4, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2020, 8, 2), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Max Verstappen"),
            self._create_event(5, "70th Anniversary Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2020, 8, 9), EventStatus.COMPLETED,
                             "Max Verstappen", "Valtteri Bottas", "Lewis Hamilton"),
            self._create_event(6, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2020, 8, 16), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Valtteri Bottas"),
            self._create_event(7, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2020, 8, 30), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Daniel Ricciardo"),
            self._create_event(8, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2020, 9, 6), EventStatus.COMPLETED,
                             "Pierre Gasly", "Lewis Hamilton", "Lewis Hamilton"),
            self._create_event(9, "Tuscan Grand Prix", "Italy", "Mugello Circuit",
                             "Mugello", datetime(2020, 9, 13), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Lewis Hamilton"),
            self._create_event(10, "Russian Grand Prix", "Russia", "Sochi Autodrom",
                             "Sochi", datetime(2020, 9, 27), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Lewis Hamilton", "Valtteri Bottas"),
            self._create_event(11, "Eifel Grand Prix", "Germany", "Nürburgring",
                             "Nürburg", datetime(2020, 10, 11), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Valtteri Bottas", "Max Verstappen"),
            self._create_event(12, "Portuguese Grand Prix", "Portugal", "Autódromo Internacional do Algarve",
                             "Portimão", datetime(2020, 10, 25), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Lewis Hamilton"),
            self._create_event(13, "Emilia Romagna Grand Prix", "Italy", "Autodromo Enzo e Dino Ferrari",
                             "Imola", datetime(2020, 11, 1), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Valtteri Bottas", "Lewis Hamilton"),
            self._create_event(14, "Turkish Grand Prix", "Turkey", "Istanbul Park",
                             "Istanbul", datetime(2020, 11, 15), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lance Stroll", "Lando Norris"),
            self._create_event(15, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2020, 11, 29), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "George Russell"),
            self._create_event(16, "Sakhir Grand Prix", "Bahrain", "Bahrain International Circuit (Outer)",
                             "Sakhir", datetime(2020, 12, 6), EventStatus.COMPLETED,
                             "Sergio Perez", "Valtteri Bottas", "George Russell"),
            self._create_event(17, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2020, 12, 13), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
        ]
        
        season = Season(year=2020, champion=champion_info[0], constructor_champion=champion_info[1])
        season.events = events
        return season
    
    def _create_2021_season(self) -> Season:
        """Create 2021 F1 season data."""
        drivers = self.DRIVERS[2021]
        champion_info = self.CHAMPIONS[2021]
        
        events = [
            self._create_event(1, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2021, 3, 28), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Max Verstappen", "Max Verstappen"),
            self._create_event(2, "Emilia Romagna Grand Prix", "Italy", "Autodromo Enzo e Dino Ferrari",
                             "Imola", datetime(2021, 4, 18), EventStatus.COMPLETED,
                             "Max Verstappen", "Lewis Hamilton", "Lewis Hamilton"),
            self._create_event(3, "Portuguese Grand Prix", "Portugal", "Autódromo Internacional do Algarve",
                             "Portimão", datetime(2021, 5, 2), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Valtteri Bottas", "Valtteri Bottas"),
            self._create_event(4, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2021, 5, 9), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Max Verstappen"),
            self._create_event(5, "Monaco Grand Prix", "Monaco", "Circuit de Monaco",
                             "Monte Carlo", datetime(2021, 5, 23), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Lewis Hamilton"),
            self._create_event(6, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit",
                             "Baku", datetime(2021, 6, 6), EventStatus.COMPLETED,
                             "Sergio Perez", "Charles Leclerc", "Max Verstappen"),
            self._create_event(7, "French Grand Prix", "France", "Circuit Paul Ricard",
                             "Le Castellet", datetime(2021, 6, 20), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(8, "Styrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2021, 6, 27), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(9, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2021, 7, 4), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(10, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2021, 7, 18), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Max Verstappen"),
            self._create_event(11, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2021, 8, 1), EventStatus.COMPLETED,
                             "Esteban Ocon", "Lewis Hamilton", "Pierre Gasly"),
            self._create_event(12, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2021, 8, 29), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "No lap completed"),
            self._create_event(13, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort",
                             "Zandvoort", datetime(2021, 9, 5), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lewis Hamilton"),
            self._create_event(14, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2021, 9, 12), EventStatus.COMPLETED,
                             "Daniel Ricciardo", "Valtteri Bottas", "Daniel Ricciardo"),
            self._create_event(15, "Russian Grand Prix", "Russia", "Sochi Autodrom",
                             "Sochi", datetime(2021, 9, 26), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lando Norris", "Lando Norris"),
            self._create_event(16, "Turkish Grand Prix", "Turkey", "Istanbul Park",
                             "Istanbul", datetime(2021, 10, 10), EventStatus.COMPLETED,
                             "Valtteri Bottas", "Lewis Hamilton", "Valtteri Bottas"),
            self._create_event(17, "United States Grand Prix", "United States", "Circuit of the Americas",
                             "Austin", datetime(2021, 10, 24), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lewis Hamilton"),
            self._create_event(18, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez",
                             "Mexico City", datetime(2021, 11, 7), EventStatus.COMPLETED,
                             "Max Verstappen", "Valtteri Bottas", "Valtteri Bottas"),
            self._create_event(19, "São Paulo Grand Prix", "Brazil", "Autódromo José Carlos Pace",
                             "São Paulo", datetime(2021, 11, 14), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Max Verstappen", "Sergio Perez"),
            self._create_event(20, "Qatar Grand Prix", "Qatar", "Losail International Circuit",
                             "Lusail", datetime(2021, 11, 21), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Max Verstappen"),
            self._create_event(21, "Saudi Arabian Grand Prix", "Saudi Arabia", "Jeddah Corniche Circuit",
                             "Jeddah", datetime(2021, 12, 5), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Lewis Hamilton"),
            self._create_event(22, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2021, 12, 12), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
        ]
        
        season = Season(year=2021, champion=champion_info[0], constructor_champion=champion_info[1])
        season.events = events
        return season
    
    def _create_2022_season(self) -> Season:
        """Create 2022 F1 season data."""
        drivers = self.DRIVERS[2022]
        champion_info = self.CHAMPIONS[2022]
        
        events = [
            self._create_event(1, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2022, 3, 20), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Charles Leclerc"),
            self._create_event(2, "Saudi Arabian Grand Prix", "Saudi Arabia", "Jeddah Corniche Circuit",
                             "Jeddah", datetime(2022, 3, 27), EventStatus.COMPLETED,
                             "Max Verstappen", "Sergio Perez", "Charles Leclerc"),
            self._create_event(3, "Australian Grand Prix", "Australia", "Albert Park Circuit",
                             "Melbourne", datetime(2022, 4, 10), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Charles Leclerc"),
            self._create_event(4, "Emilia Romagna Grand Prix", "Italy", "Autodromo Enzo e Dino Ferrari",
                             "Imola", datetime(2022, 4, 24), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(5, "Miami Grand Prix", "Miami", "Miami International Autodrome",
                             "Miami", datetime(2022, 5, 8), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Max Verstappen"),
            self._create_event(6, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2022, 5, 22), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Sergio Perez"),
            self._create_event(7, "Monaco Grand Prix", "Monaco", "Circuit de Monaco",
                             "Monte Carlo", datetime(2022, 5, 29), EventStatus.COMPLETED,
                             "Sergio Perez", "Charles Leclerc", "Lando Norris"),
            self._create_event(8, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit",
                             "Baku", datetime(2022, 6, 12), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Sergio Perez"),
            self._create_event(9, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve",
                             "Montreal", datetime(2022, 6, 19), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Carlos Sainz"),
            self._create_event(10, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2022, 7, 3), EventStatus.COMPLETED,
                             "Carlos Sainz", "Carlos Sainz", "Lewis Hamilton"),
            self._create_event(11, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2022, 7, 10), EventStatus.COMPLETED,
                             "Charles Leclerc", "Max Verstappen", "Max Verstappen"),
            self._create_event(12, "French Grand Prix", "France", "Circuit Paul Ricard",
                             "Le Castellet", datetime(2022, 7, 24), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Carlos Sainz"),
            self._create_event(13, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2022, 7, 31), EventStatus.COMPLETED,
                             "Max Verstappen", "George Russell", "Lewis Hamilton"),
            self._create_event(14, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2022, 8, 28), EventStatus.COMPLETED,
                             "Max Verstappen", "Carlos Sainz", "Max Verstappen"),
            self._create_event(15, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort",
                             "Zandvoort", datetime(2022, 9, 4), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(16, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2022, 9, 11), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Sergio Perez"),
            self._create_event(17, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit",
                             "Singapore", datetime(2022, 10, 2), EventStatus.COMPLETED,
                             "Sergio Perez", "Charles Leclerc", "Sergio Perez"),
            self._create_event(18, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course",
                             "Suzuka", datetime(2022, 10, 9), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Zhou Guanyu"),
            self._create_event(19, "United States Grand Prix", "United States", "Circuit of the Americas",
                             "Austin", datetime(2022, 10, 23), EventStatus.COMPLETED,
                             "Max Verstappen", "Carlos Sainz", "George Russell"),
            self._create_event(20, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez",
                             "Mexico City", datetime(2022, 10, 30), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "George Russell"),
            self._create_event(21, "São Paulo Grand Prix", "Brazil", "Autódromo José Carlos Pace",
                             "São Paulo", datetime(2022, 11, 13), EventStatus.COMPLETED,
                             "George Russell", "Kevin Magnussen", "George Russell"),
            self._create_event(22, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2022, 11, 20), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lando Norris"),
        ]
        
        season = Season(year=2022, champion=champion_info[0], constructor_champion=champion_info[1])
        season.events = events
        return season
    
    def _create_2023_season(self) -> Season:
        """Create 2023 F1 season data."""
        drivers = self.DRIVERS[2023]
        champion_info = self.CHAMPIONS[2023]
        
        events = [
            self._create_event(1, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2023, 3, 5), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Zhou Guanyu"),
            self._create_event(2, "Saudi Arabian Grand Prix", "Saudi Arabia", "Jeddah Corniche Circuit",
                             "Jeddah", datetime(2023, 3, 19), EventStatus.COMPLETED,
                             "Sergio Perez", "Sergio Perez", "Max Verstappen"),
            self._create_event(3, "Australian Grand Prix", "Australia", "Albert Park Circuit",
                             "Melbourne", datetime(2023, 4, 2), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Sergio Perez"),
            self._create_event(4, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit",
                             "Baku", datetime(2023, 4, 30), EventStatus.COMPLETED,
                             "Sergio Perez", "Charles Leclerc", "George Russell"),
            self._create_event(5, "Miami Grand Prix", "Miami", "Miami International Autodrome",
                             "Miami", datetime(2023, 5, 7), EventStatus.COMPLETED,
                             "Sergio Perez", "Sergio Perez", "Max Verstappen"),
            self._create_event(6, "Monaco Grand Prix", "Monaco", "Circuit de Monaco",
                             "Monte Carlo", datetime(2023, 5, 28), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lewis Hamilton"),
            self._create_event(7, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2023, 6, 4), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(8, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve",
                             "Montreal", datetime(2023, 6, 18), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(9, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2023, 7, 2), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(10, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2023, 7, 9), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(11, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2023, 7, 23), EventStatus.COMPLETED,
                             "Max Verstappen", "Lewis Hamilton", "Max Verstappen"),
            self._create_event(12, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2023, 7, 30), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Lewis Hamilton"),
            self._create_event(13, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort",
                             "Zandvoort", datetime(2023, 8, 27), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Fernando Alonso"),
            self._create_event(14, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2023, 9, 3), EventStatus.COMPLETED,
                             "Max Verstappen", "Carlos Sainz", "Max Verstappen"),
            self._create_event(15, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit",
                             "Singapore", datetime(2023, 9, 17), EventStatus.COMPLETED,
                             "Carlos Sainz", "Carlos Sainz", "Lewis Hamilton"),
            self._create_event(16, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course",
                             "Suzuka", datetime(2023, 9, 24), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(17, "Qatar Grand Prix", "Qatar", "Lusail International Circuit",
                             "Lusail", datetime(2023, 10, 8), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(18, "United States Grand Prix", "United States", "Circuit of the Americas",
                             "Austin", datetime(2023, 10, 22), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Esteban Ocon"),
            self._create_event(19, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez",
                             "Mexico City", datetime(2023, 10, 29), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Lewis Hamilton"),
            self._create_event(20, "São Paulo Grand Prix", "Brazil", "Autódromo José Carlos Pace",
                             "São Paulo", datetime(2023, 11, 5), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lando Norris"),
            self._create_event(21, "Las Vegas Grand Prix", "Las Vegas", "Las Vegas Strip Circuit",
                             "Las Vegas", datetime(2023, 11, 19), EventStatus.COMPLETED,
                             "Max Verstappen", "Charles Leclerc", "Oscar Piastri"),
            self._create_event(22, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2023, 11, 26), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
        ]
        
        season = Season(year=2023, champion=champion_info[0], constructor_champion=champion_info[1])
        season.events = events
        return season
    
    def _create_2024_season(self) -> Season:
        """Create 2024 F1 season data."""
        drivers = self.DRIVERS[2024]
        champion_info = self.CHAMPIONS[2024]
        
        events = [
            self._create_event(1, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2024, 3, 2), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(2, "Saudi Arabian Grand Prix", "Saudi Arabia", "Jeddah Corniche Circuit",
                             "Jeddah", datetime(2024, 3, 9), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Charles Leclerc"),
            self._create_event(3, "Australian Grand Prix", "Australia", "Albert Park Circuit",
                             "Melbourne", datetime(2024, 3, 24), EventStatus.COMPLETED,
                             "Carlos Sainz", "Max Verstappen", "Charles Leclerc"),
            self._create_event(4, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course",
                             "Suzuka", datetime(2024, 4, 7), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(5, "Chinese Grand Prix", "China", "Shanghai International Circuit",
                             "Shanghai", datetime(2024, 4, 21), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lando Norris"),
            self._create_event(6, "Miami Grand Prix", "Miami", "Miami International Autodrome",
                             "Miami", datetime(2024, 5, 5), EventStatus.COMPLETED,
                             "Lando Norris", "Max Verstappen", "Max Verstappen"),
            self._create_event(7, "Emilia Romagna Grand Prix", "Italy", "Autodromo Enzo e Dino Ferrari",
                             "Imola", datetime(2024, 5, 19), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(8, "Monaco Grand Prix", "Monaco", "Circuit de Monaco",
                             "Monte Carlo", datetime(2024, 5, 26), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Oscar Piastri"),
            self._create_event(9, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve",
                             "Montreal", datetime(2024, 6, 9), EventStatus.COMPLETED,
                             "Max Verstappen", "George Russell", "Lewis Hamilton"),
            self._create_event(10, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2024, 6, 23), EventStatus.COMPLETED,
                             "Max Verstappen", "Lando Norris", "Lando Norris"),
            self._create_event(11, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2024, 6, 30), EventStatus.COMPLETED,
                             "George Russell", "Max Verstappen", "Oscar Piastri"),
            self._create_event(12, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2024, 7, 7), EventStatus.COMPLETED,
                             "Lewis Hamilton", "George Russell", "Max Verstappen"),
            self._create_event(13, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2024, 7, 21), EventStatus.COMPLETED,
                             "Oscar Piastri", "Lando Norris", "Max Verstappen"),
            self._create_event(14, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2024, 7, 28), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Charles Leclerc", "Lando Norris"),
            self._create_event(15, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort",
                             "Zandvoort", datetime(2024, 8, 25), EventStatus.COMPLETED,
                             "Lando Norris", "Lando Norris", "Lando Norris"),
            self._create_event(16, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2024, 9, 1), EventStatus.COMPLETED,
                             "Charles Leclerc", "Lando Norris", "Oscar Piastri"),
            self._create_event(17, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit",
                             "Baku", datetime(2024, 9, 15), EventStatus.COMPLETED,
                             "Oscar Piastri", "Charles Leclerc", "Lando Norris"),
            self._create_event(18, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit",
                             "Singapore", datetime(2024, 9, 22), EventStatus.COMPLETED,
                             "Lando Norris", "Lando Norris", "Daniel Ricciardo"),
            self._create_event(19, "United States Grand Prix", "United States", "Circuit of the Americas",
                             "Austin", datetime(2024, 10, 20), EventStatus.COMPLETED,
                             "Charles Leclerc", "Lando Norris", "Esteban Ocon"),
            self._create_event(20, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez",
                             "Mexico City", datetime(2024, 10, 27), EventStatus.COMPLETED,
                             "Carlos Sainz", "Carlos Sainz", "Charles Leclerc"),
            self._create_event(21, "São Paulo Grand Prix", "Brazil", "Autódromo José Carlos Pace",
                             "São Paulo", datetime(2024, 11, 3), EventStatus.COMPLETED,
                             "Max Verstappen", "Lando Norris", "Max Verstappen"),
            self._create_event(22, "Las Vegas Grand Prix", "Las Vegas", "Las Vegas Strip Circuit",
                             "Las Vegas", datetime(2024, 11, 24), EventStatus.COMPLETED,
                             "George Russell", "George Russell", "Oscar Piastri"),
            self._create_event(23, "Qatar Grand Prix", "Qatar", "Lusail International Circuit",
                             "Lusail", datetime(2024, 12, 1), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(24, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2024, 12, 8), EventStatus.COMPLETED,
                             "Lando Norris", "Lando Norris", "Lando Norris"),
        ]
        
        season = Season(year=2024, champion=champion_info[0], constructor_champion=champion_info[1])
        season.events = events
        return season
    
    def _create_2025_season(self) -> Season:
        """Create 2025 F1 season data (completed — mock results and champions)."""
        champion_info = self.CHAMPIONS[2025]
        
        events = [
            self._create_event(1, "Australian Grand Prix", "Australia", "Albert Park Circuit",
                             "Melbourne", datetime(2025, 3, 16), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Oscar Piastri"),
            self._create_event(2, "Chinese Grand Prix", "China", "Shanghai International Circuit",
                             "Shanghai", datetime(2025, 3, 23), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Lewis Hamilton"),
            self._create_event(3, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course",
                             "Suzuka", datetime(2025, 4, 6), EventStatus.COMPLETED,
                             "Max Verstappen", "Lando Norris", "Max Verstappen"),
            self._create_event(4, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit",
                             "Sakhir", datetime(2025, 4, 13), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Lewis Hamilton", "Charles Leclerc"),
            self._create_event(5, "Saudi Arabian Grand Prix", "Saudi Arabia", "Jeddah Corniche Circuit",
                             "Jeddah", datetime(2025, 4, 20), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Charles Leclerc"),
            self._create_event(6, "Miami Grand Prix", "Miami", "Miami International Autodrome",
                             "Miami", datetime(2025, 5, 4), EventStatus.COMPLETED,
                             "Lando Norris", "Max Verstappen", "Max Verstappen"),
            self._create_event(7, "Emilia Romagna Grand Prix", "Italy", "Autodromo Enzo e Dino Ferrari",
                             "Imola", datetime(2025, 5, 18), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(8, "Monaco Grand Prix", "Monaco", "Circuit de Monaco",
                             "Monte Carlo", datetime(2025, 5, 25), EventStatus.COMPLETED,
                             "Charles Leclerc", "Charles Leclerc", "Oscar Piastri"),
            self._create_event(9, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya",
                             "Barcelona", datetime(2025, 6, 1), EventStatus.COMPLETED,
                             "Max Verstappen", "Lando Norris", "Lando Norris"),
            self._create_event(10, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve",
                             "Montreal", datetime(2025, 6, 15), EventStatus.COMPLETED,
                             "Max Verstappen", "George Russell", "Lewis Hamilton"),
            self._create_event(11, "Austrian Grand Prix", "Austria", "Red Bull Ring",
                             "Spielberg", datetime(2025, 6, 29), EventStatus.COMPLETED,
                             "George Russell", "Max Verstappen", "Oscar Piastri"),
            self._create_event(12, "British Grand Prix", "United Kingdom", "Silverstone Circuit",
                             "Silverstone", datetime(2025, 7, 6), EventStatus.COMPLETED,
                             "Lewis Hamilton", "George Russell", "Max Verstappen"),
            self._create_event(13, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps",
                             "Spa", datetime(2025, 7, 27), EventStatus.COMPLETED,
                             "Lewis Hamilton", "Charles Leclerc", "Lando Norris"),
            self._create_event(14, "Hungarian Grand Prix", "Hungary", "Hungaroring",
                             "Budapest", datetime(2025, 8, 3), EventStatus.COMPLETED,
                             "Oscar Piastri", "Lando Norris", "Max Verstappen"),
            self._create_event(15, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort",
                             "Zandvoort", datetime(2025, 8, 31), EventStatus.COMPLETED,
                             "Lando Norris", "Lando Norris", "Lando Norris"),
            self._create_event(16, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza",
                             "Monza", datetime(2025, 9, 7), EventStatus.COMPLETED,
                             "Charles Leclerc", "Lando Norris", "Oscar Piastri"),
            self._create_event(17, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit",
                             "Baku", datetime(2025, 9, 21), EventStatus.COMPLETED,
                             "Oscar Piastri", "Charles Leclerc", "Lando Norris"),
            self._create_event(18, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit",
                             "Singapore", datetime(2025, 10, 5), EventStatus.COMPLETED,
                             "Lando Norris", "Lando Norris", "Daniel Ricciardo"),
            self._create_event(19, "United States Grand Prix", "United States", "Circuit of the Americas",
                             "Austin", datetime(2025, 10, 19), EventStatus.COMPLETED,
                             "Charles Leclerc", "Lando Norris", "Esteban Ocon"),
            self._create_event(20, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez",
                             "Mexico City", datetime(2025, 10, 26), EventStatus.COMPLETED,
                             "Carlos Sainz", "Carlos Sainz", "Charles Leclerc"),
            self._create_event(21, "São Paulo Grand Prix", "Brazil", "Autódromo José Carlos Pace",
                             "São Paulo", datetime(2025, 11, 9), EventStatus.COMPLETED,
                             "Max Verstappen", "Lando Norris", "Max Verstappen"),
            self._create_event(22, "Las Vegas Grand Prix", "Las Vegas", "Las Vegas Strip Circuit",
                             "Las Vegas", datetime(2025, 11, 22), EventStatus.COMPLETED,
                             "George Russell", "George Russell", "Oscar Piastri"),
            self._create_event(23, "Qatar Grand Prix", "Qatar", "Lusail International Circuit",
                             "Lusail", datetime(2025, 11, 30), EventStatus.COMPLETED,
                             "Max Verstappen", "Max Verstappen", "Max Verstappen"),
            self._create_event(24, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit",
                             "Abu Dhabi", datetime(2025, 12, 7), EventStatus.COMPLETED,
                             "Lando Norris", "Lando Norris", "Lando Norris"),
        ]
        
        season = Season(
            year=2025,
            champion=champion_info[0],
            constructor_champion=champion_info[1],
        )
        season.events = events
        return season
    
    def _create_2026_season(self) -> Season:
        """Create 2026 calendar; completed vs upcoming follows ``date.today()``."""
        today = date.today()
        # (round, name, country, circuit, city, race_date) — aligned with mock 2025 order
        schedule = [
            (1, "Australian Grand Prix", "Australia", "Albert Park Circuit", "Melbourne", datetime(2026, 3, 15)),
            (2, "Chinese Grand Prix", "China", "Shanghai International Circuit", "Shanghai", datetime(2026, 3, 22)),
            (3, "Japanese Grand Prix", "Japan", "Suzuka International Racing Course", "Suzuka", datetime(2026, 4, 5)),
            (4, "Bahrain Grand Prix", "Bahrain", "Bahrain International Circuit", "Sakhir", datetime(2026, 4, 12)),
            (5, "Saudi Arabian Grand Prix", "Saudi Arabia", "Jeddah Corniche Circuit", "Jeddah", datetime(2026, 4, 19)),
            (6, "Miami Grand Prix", "Miami", "Miami International Autodrome", "Miami", datetime(2026, 5, 3)),
            (7, "Emilia Romagna Grand Prix", "Italy", "Autodromo Enzo e Dino Ferrari", "Imola", datetime(2026, 5, 17)),
            (8, "Monaco Grand Prix", "Monaco", "Circuit de Monaco", "Monte Carlo", datetime(2026, 5, 24)),
            (9, "Spanish Grand Prix", "Spain", "Circuit de Barcelona-Catalunya", "Barcelona", datetime(2026, 5, 31)),
            (10, "Canadian Grand Prix", "Canada", "Circuit Gilles Villeneuve", "Montreal", datetime(2026, 6, 14)),
            (11, "Austrian Grand Prix", "Austria", "Red Bull Ring", "Spielberg", datetime(2026, 6, 28)),
            (12, "British Grand Prix", "United Kingdom", "Silverstone Circuit", "Silverstone", datetime(2026, 7, 5)),
            (13, "Belgian Grand Prix", "Belgium", "Circuit de Spa-Francorchamps", "Spa", datetime(2026, 7, 26)),
            (14, "Hungarian Grand Prix", "Hungary", "Hungaroring", "Budapest", datetime(2026, 8, 2)),
            (15, "Dutch Grand Prix", "Netherlands", "Circuit Zandvoort", "Zandvoort", datetime(2026, 8, 30)),
            (16, "Italian Grand Prix", "Italy", "Autodromo Nazionale Monza", "Monza", datetime(2026, 9, 6)),
            (17, "Azerbaijan Grand Prix", "Azerbaijan", "Baku City Circuit", "Baku", datetime(2026, 9, 20)),
            (18, "Singapore Grand Prix", "Singapore", "Marina Bay Street Circuit", "Singapore", datetime(2026, 10, 4)),
            (19, "United States Grand Prix", "United States", "Circuit of the Americas", "Austin", datetime(2026, 10, 18)),
            (20, "Mexican Grand Prix", "Mexico", "Autódromo Hermanos Rodríguez", "Mexico City", datetime(2026, 10, 25)),
            (21, "São Paulo Grand Prix", "Brazil", "Autódromo José Carlos Pace", "São Paulo", datetime(2026, 11, 8)),
            (22, "Las Vegas Grand Prix", "Las Vegas", "Las Vegas Strip Circuit", "Las Vegas", datetime(2026, 11, 21)),
            (23, "Qatar Grand Prix", "Qatar", "Lusail International Circuit", "Lusail", datetime(2026, 11, 29)),
            (24, "Abu Dhabi Grand Prix", "Abu Dhabi", "Yas Marina Circuit", "Abu Dhabi", datetime(2026, 12, 6)),
        ]
        # Mock results per round (winner, pole, fastest) when race day has passed
        mock_results = [
            ("Charles Leclerc", "Charles Leclerc", "Oscar Piastri"),
            ("Max Verstappen", "Max Verstappen", "Lewis Hamilton"),
            ("Max Verstappen", "Lando Norris", "Max Verstappen"),
            ("Lewis Hamilton", "Lewis Hamilton", "Charles Leclerc"),
            ("Max Verstappen", "Max Verstappen", "Charles Leclerc"),
            ("Lando Norris", "Max Verstappen", "Max Verstappen"),
            ("Max Verstappen", "Max Verstappen", "Max Verstappen"),
            ("Charles Leclerc", "Charles Leclerc", "Oscar Piastri"),
            ("Max Verstappen", "Lando Norris", "Lando Norris"),
            ("Max Verstappen", "George Russell", "Lewis Hamilton"),
            ("George Russell", "Max Verstappen", "Oscar Piastri"),
            ("Lewis Hamilton", "George Russell", "Max Verstappen"),
            ("Lewis Hamilton", "Charles Leclerc", "Lando Norris"),
            ("Oscar Piastri", "Lando Norris", "Max Verstappen"),
            ("Lando Norris", "Lando Norris", "Lando Norris"),
            ("Charles Leclerc", "Lando Norris", "Oscar Piastri"),
            ("Oscar Piastri", "Charles Leclerc", "Lando Norris"),
            ("Lando Norris", "Lando Norris", "Daniel Ricciardo"),
            ("Charles Leclerc", "Lando Norris", "Esteban Ocon"),
            ("Carlos Sainz", "Carlos Sainz", "Charles Leclerc"),
            ("Max Verstappen", "Lando Norris", "Max Verstappen"),
            ("George Russell", "George Russell", "Oscar Piastri"),
            ("Max Verstappen", "Max Verstappen", "Max Verstappen"),
            ("Lando Norris", "Lando Norris", "Lando Norris"),
        ]
        events = []
        for i, (rnd, name, country, circuit, city, dt) in enumerate(schedule):
            if dt.date() <= today:
                w, p, f = mock_results[i]
                events.append(
                    self._create_event(
                        rnd, name, country, circuit, city, dt,
                        EventStatus.COMPLETED, w, p, f,
                    )
                )
            else:
                events.append(
                    self._create_event(rnd, name, country, circuit, city, dt, EventStatus.UPCOMING)
                )
        
        season = Season(year=2026)
        season.events = events
        return season
