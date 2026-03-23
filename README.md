# 🏎️ F1 Ingestor

A desktop application for viewing Formula 1 race schedules from 2019 to 2026. Built with Python using the **MVC (Model-View-Controller)** architecture pattern and **tkinter** for a dark-themed UI.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)
![Architecture](https://img.shields.io/badge/Architecture-MVC-orange.svg)

## ✨ Features

- **📅 Season Browser**: View F1 race calendars from 2019 to 2026
- **🔍 Search**: Find events by name, country, circuit, or city
- **🎯 Filters**: Filter events by status (All, Completed, Upcoming)
- **📊 Statistics**: See season completion progress and champion information
- **🏆 Race Results**: View winners, pole positions, and fastest laps for completed races
- **🎨 Modern UI**: F1-inspired dark theme with smooth hover effects
- **📱 Responsive**: Cards adapt to window size

## 🏗️ Project Architecture

This project follows the **MVC (Model-View-Controller)** pattern:

```
f1_ingestor/
├── models/                    # Data layer
│   ├── __init__.py
│   ├── event.py              # Event dataclass model
│   ├── season.py             # Season model with event collections
│   └── data_store.py         # Mock data store (2019-2026 seasons)
│
├── views/                     # Presentation layer
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── event_card.py         # Event card widget & detail modal
│   └── styles.py             # F1 theme colors and constants
│
├── controllers/               # Business logic layer
│   ├── __init__.py
│   └── season_controller.py  # Manages data flow and state
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_models.py        # Model tests
│   ├── test_controllers.py   # Controller tests
│   └── test_views.py         # View/theme tests
│
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd f1_ingestor
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python main.py
```

The application will launch with a dark-themed interface showing the F1 Ingestor schedule view.

## 🧪 Running Tests

The project includes comprehensive tests for models, controllers, and views.

### Run all tests:
```bash
pytest
```

### Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test files:
```bash
pytest tests/test_models.py -v
pytest tests/test_controllers.py -v
pytest tests/test_views.py -v
```

### Run tests with verbose output:
```bash
pytest -v
```

## 🎨 UI Components

### Main Window
- **Header**: F1 logo, season selector, and statistics
- **Toolbar**: Search bar and filter buttons
- **Events Grid**: Scrollable grid of event cards
- **Footer**: Champion information

### Event Cards
- Round number with status indicator
- Country flag and event name
- Circuit and location info
- Date display
- Results section (for completed events)
- Hover effects

### Event Detail Modal
- Full event information
- Race results (winner, pole position, fastest lap)

## 📊 Data Structure

### Event Model
```python
@dataclass
class Event:
    id: str                    # Unique identifier
    name: str                  # Grand Prix name
    country: str               # Country name
    circuit: str               # Circuit name
    city: str                  # City name
    date: datetime             # Race date
    round_number: int          # Round in season
    status: EventStatus        # upcoming/completed/cancelled
    winner: Optional[str]      # Race winner
    pole_position: Optional[str]
    fastest_lap: Optional[str]
    flag_emoji: str            # Country flag
```

### Season Model
```python
@dataclass
class Season:
    year: int
    events: List[Event]
    champion: Optional[str]           # Driver champion
    constructor_champion: Optional[str]
```

## 🎯 MVC Pattern Implementation

### Model Layer (`models/`)
- **Event**: Represents a single Grand Prix with all race data
- **Season**: Collection of events with champion information
- **DataStore**: Centralized data management with mock F1 data

### View Layer (`views/`)
- **MainWindow**: Root application window with layout
- **EventCard**: Reusable card widget for displaying events
- **F1Theme**: Design system with colors, spacing, and typography

### Controller Layer (`controllers/`)
- **SeasonController**: Mediates between Model and View
  - Manages current season state
  - Provides filtered/searched data
  - Implements observer pattern for UI updates

## 🏁 Available Seasons

| Year | Events | Champion | Constructor |
|------|--------|----------|-------------|
| 2019 | 21 | Lewis Hamilton | Mercedes |
| 2020 | 17 | Lewis Hamilton | Mercedes |
| 2021 | 22 | Max Verstappen | Red Bull Racing |
| 2022 | 22 | Max Verstappen | Red Bull Racing |
| 2023 | 22 | Max Verstappen | Red Bull Racing |
| 2024 | 24 | Max Verstappen | Red Bull Racing |
| 2025 | 24 | TBD (In Progress) | TBD |
| 2026 | 24 | TBD (Future) | TBD |

## 🛠️ Development

### Code Style
The project follows PEP 8 style guidelines. Format code using:
```bash
black .
flake8 .
```

### Type Checking
```bash
mypy .
```

## 📝 License

This project is for educational purposes. Formula 1, F1, and related marks are trademarks of Formula One Licensing B.V.

## 🙏 Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- Formula 1 - For the inspiration and data reference

---

Made with ❤️ and 🏎️ by F1 enthusiasts
