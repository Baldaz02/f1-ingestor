"""Tests for F1 Ingestor views (non-GUI tests)."""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.event import Event, EventStatus

# Import F1Theme directly to avoid importing tkinter-dependent modules
# We need to import it directly from the file, not through views/__init__.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "styles", 
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "views", "styles.py")
)
styles_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(styles_module)
F1Theme = styles_module.F1Theme


class TestF1Theme:
    """Test cases for F1Theme styling constants."""
    
    def test_primary_colors_exist(self):
        """Test primary color constants exist."""
        assert F1Theme.PRIMARY == "#E10600"
        assert F1Theme.PRIMARY_DARK == "#B30500"
        assert F1Theme.PRIMARY_LIGHT == "#FF2A24"
    
    def test_secondary_colors_exist(self):
        """Test secondary color constants exist."""
        assert F1Theme.SECONDARY == "#0A0A0A"
        assert F1Theme.SECONDARY_DARK == "#000000"
        assert F1Theme.SECONDARY_LIGHT == "#141414"
    
    def test_status_colors_exist(self):
        """Test status color constants exist."""
        assert F1Theme.STATUS_COMPLETED == "#00D26A"
        assert F1Theme.STATUS_UPCOMING == "#00A9FF"
        assert F1Theme.STATUS_CANCELLED == "#FF3D3D"
        assert F1Theme.STATUS_IN_PROGRESS == "#FFD700"
    
    def test_get_status_color(self):
        """Test getting color for status."""
        assert F1Theme.get_status_color("completed") == F1Theme.STATUS_COMPLETED
        assert F1Theme.get_status_color("upcoming") == F1Theme.STATUS_UPCOMING
        assert F1Theme.get_status_color("cancelled") == F1Theme.STATUS_CANCELLED
        assert F1Theme.get_status_color("in_progress") == F1Theme.STATUS_IN_PROGRESS
        assert F1Theme.get_status_color("deleted") == F1Theme.TEXT_MUTED
    
    def test_get_status_color_invalid(self):
        """Test getting color for invalid status."""
        assert F1Theme.get_status_color("invalid") == F1Theme.TEXT_SECONDARY
    
    def test_get_team_color(self):
        """Test getting team colors."""
        assert F1Theme.get_team_color("red bull") == F1Theme.ACCENT_BLUE
        assert F1Theme.get_team_color("ferrari") == F1Theme.PRIMARY
        assert F1Theme.get_team_color("mercedes") == F1Theme.ACCENT_CYAN
        assert F1Theme.get_team_color("mclaren") == F1Theme.ACCENT_ORANGE
        assert F1Theme.get_team_color("aston martin") == F1Theme.ACCENT_GREEN
    
    def test_get_team_color_case_insensitive(self):
        """Test team color lookup is case insensitive."""
        assert F1Theme.get_team_color("RED BULL") == F1Theme.ACCENT_BLUE
        assert F1Theme.get_team_color("Ferrari") == F1Theme.PRIMARY
        assert F1Theme.get_team_color("MERCEDES") == F1Theme.ACCENT_CYAN
    
    def test_get_team_color_unknown_team(self):
        """Test unknown team returns default color."""
        assert F1Theme.get_team_color("unknown team") == F1Theme.TEXT_SECONDARY
    
    def test_get_position_color(self):
        """Test podium position colors."""
        assert F1Theme.get_position_color(1) == F1Theme.ACCENT_GOLD
        assert F1Theme.get_position_color(2) == F1Theme.ACCENT_SILVER
        assert F1Theme.get_position_color(3) == F1Theme.ACCENT_BRONZE
        assert F1Theme.get_position_color(4) == F1Theme.TEXT_SECONDARY
        assert F1Theme.get_position_color(10) == F1Theme.TEXT_SECONDARY
    
    def test_font_sizes(self):
        """Test font size constants."""
        assert F1Theme.FONT_SIZE_HERO == 48
        assert F1Theme.FONT_SIZE_H1 == 32
        assert F1Theme.FONT_SIZE_H2 == 24
        assert F1Theme.FONT_SIZE_H3 == 18
        assert F1Theme.FONT_SIZE_BODY == 14
        assert F1Theme.FONT_SIZE_SMALL == 12
        assert F1Theme.FONT_SIZE_TINY == 10
    
    def test_spacing(self):
        """Test spacing constants."""
        assert F1Theme.SPACING_XS == 4
        assert F1Theme.SPACING_SM == 8
        assert F1Theme.SPACING_MD == 16
        assert F1Theme.SPACING_LG == 24
        assert F1Theme.SPACING_XL == 32
        assert F1Theme.SPACING_XXL == 48
    
    def test_border_radius(self):
        """Test border radius constants."""
        assert F1Theme.RADIUS_SM == 4
        assert F1Theme.RADIUS_MD == 8
        assert F1Theme.RADIUS_LG == 12
        assert F1Theme.RADIUS_XL == 16
        assert F1Theme.RADIUS_FULL == 999
    
    def test_window_dimensions(self):
        """Test window dimension constants."""
        assert F1Theme.WINDOW_MIN_WIDTH == 1280
        assert F1Theme.WINDOW_MIN_HEIGHT == 800
    
    def test_card_dimensions(self):
        """Test card dimension constants."""
        assert F1Theme.CARD_WIDTH == 320
        assert F1Theme.CARD_HEIGHT == 180
    
    def test_text_colors(self):
        """Test text color constants."""
        assert F1Theme.TEXT_PRIMARY == "#FFFFFF"
        assert F1Theme.TEXT_SECONDARY == "#A0A0B0"
        assert F1Theme.TEXT_MUTED == "#6B6B7B"
        assert F1Theme.TEXT_DARK == "#15151E"
    
    def test_surface_colors(self):
        """Test surface color constants."""
        assert F1Theme.SURFACE == "#000000"
        assert F1Theme.SURFACE_ELEVATED == "#121212"
        assert F1Theme.SURFACE_HOVER == "#1A1A1A"
    
    def test_card_colors(self):
        """Test card color constants."""
        assert F1Theme.CARD_BG == "#0A0A0A"
        assert F1Theme.CARD_HOVER == "#141414"
        assert F1Theme.CARD_BORDER == "#252525"
    
    def test_accent_colors(self):
        """Test accent color constants."""
        assert F1Theme.ACCENT_GOLD == "#FFD700"
        assert F1Theme.ACCENT_SILVER == "#C0C0C0"
        assert F1Theme.ACCENT_BRONZE == "#CD7F32"
        assert F1Theme.ACCENT_CYAN == "#00D2BE"
        assert F1Theme.ACCENT_BLUE == "#0600EF"
        assert F1Theme.ACCENT_ORANGE == "#FF8700"
        assert F1Theme.ACCENT_GREEN == "#006F62"


class TestEventCardLogic:
    """Test the logic within EventCard (without GUI)."""
    
    def test_completed_event_has_results_section(self):
        """Test completed events should show results."""
        event = Event(
            id="2024-R01",
            name="Test GP",
            country="Test",
            circuit="Test Circuit",
            city="Test City",
            date=datetime(2024, 3, 24),
            round_number=1,
            status=EventStatus.COMPLETED,
            winner="Max Verstappen"
        )
        
        assert event.is_completed
        assert event.winner is not None
    
    def test_upcoming_event_no_results(self):
        """Test upcoming events don't have results."""
        event = Event(
            id="2024-R01",
            name="Test GP",
            country="Test",
            circuit="Test Circuit",
            city="Test City",
            date=datetime(2024, 3, 24),
            round_number=1,
            status=EventStatus.UPCOMING
        )
        
        assert event.is_upcoming
        assert event.winner is None
        assert event.pole_position is None
        assert event.fastest_lap is None


class TestViewsIntegration:
    """Integration tests for views (mocked - no GUI)."""
    
    def test_controller_has_required_interface_for_views(self):
        """Test controller has all methods needed by views."""
        # Import directly to avoid tkinter
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from controllers.season_controller import SeasonController
        
        controller = SeasonController()
        
        # Test controller has necessary methods for MainWindow
        assert hasattr(controller, 'get_events_for_current_season')
        assert hasattr(controller, 'get_season_stats')
        assert hasattr(controller, 'add_observer')
        assert hasattr(controller, 'current_year')
        assert hasattr(controller, 'get_available_years')
        assert hasattr(controller, 'get_upcoming_events')
        assert hasattr(controller, 'get_completed_events')
        assert hasattr(controller, 'search_events')
        assert hasattr(controller, 'filter_events_by_status')
    
    def test_event_card_data_requirements(self):
        """Test event provides all data needed for card."""
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
            fastest_lap="Lando Norris",
            flag_emoji="🇦🇺"
        )
        
        # All fields needed by EventCard are accessible
        assert event.name
        assert event.country
        assert event.circuit
        assert event.city
        assert event.formatted_date
        assert event.round_number
        assert event.status
        assert event.flag_emoji
        assert event.winner
        assert event.pole_position
        assert event.fastest_lap


class TestColorHexValues:
    """Test that all color values are valid hex codes."""
    
    def test_primary_colors_valid_hex(self):
        """Test primary colors are valid hex."""
        colors = [
            F1Theme.PRIMARY,
            F1Theme.PRIMARY_DARK,
            F1Theme.PRIMARY_LIGHT
        ]
        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7
            int(color[1:], 16)  # Should not raise
    
    def test_status_colors_valid_hex(self):
        """Test status colors are valid hex."""
        colors = [
            F1Theme.STATUS_COMPLETED,
            F1Theme.STATUS_UPCOMING,
            F1Theme.STATUS_CANCELLED,
            F1Theme.STATUS_IN_PROGRESS
        ]
        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7
            int(color[1:], 16)
    
    def test_text_colors_valid_hex(self):
        """Test text colors are valid hex."""
        colors = [
            F1Theme.TEXT_PRIMARY,
            F1Theme.TEXT_SECONDARY,
            F1Theme.TEXT_MUTED,
            F1Theme.TEXT_DARK
        ]
        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7
            int(color[1:], 16)
    
    def test_surface_colors_valid_hex(self):
        """Test surface colors are valid hex."""
        colors = [
            F1Theme.SURFACE,
            F1Theme.SURFACE_ELEVATED,
            F1Theme.SURFACE_HOVER
        ]
        for color in colors:
            assert color.startswith('#')
            assert len(color) == 7
            int(color[1:], 16)


class TestThemeConsistency:
    """Test theme consistency and relationships."""
    
    def test_dark_variants_are_darker(self):
        """Test dark color variants have lower values."""
        def hex_to_brightness(hex_color):
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return (r + g + b) / 3
        
        assert hex_to_brightness(F1Theme.PRIMARY_DARK) < hex_to_brightness(F1Theme.PRIMARY)
        assert hex_to_brightness(F1Theme.SECONDARY_DARK) < hex_to_brightness(F1Theme.SECONDARY)
    
    def test_light_variants_are_lighter(self):
        """Test light color variants have higher values."""
        def hex_to_brightness(hex_color):
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return (r + g + b) / 3
        
        assert hex_to_brightness(F1Theme.PRIMARY_LIGHT) > hex_to_brightness(F1Theme.PRIMARY)
        assert hex_to_brightness(F1Theme.SECONDARY_LIGHT) > hex_to_brightness(F1Theme.SECONDARY)
    
    def test_spacing_increases(self):
        """Test spacing values increase progressively."""
        spacings = [
            F1Theme.SPACING_XS,
            F1Theme.SPACING_SM,
            F1Theme.SPACING_MD,
            F1Theme.SPACING_LG,
            F1Theme.SPACING_XL,
            F1Theme.SPACING_XXL
        ]
        for i in range(len(spacings) - 1):
            assert spacings[i] < spacings[i + 1]
    
    def test_font_sizes_increase(self):
        """Test font sizes increase progressively."""
        sizes = [
            F1Theme.FONT_SIZE_TINY,
            F1Theme.FONT_SIZE_SMALL,
            F1Theme.FONT_SIZE_BODY,
            F1Theme.FONT_SIZE_H3,
            F1Theme.FONT_SIZE_H2,
            F1Theme.FONT_SIZE_H1,
            F1Theme.FONT_SIZE_HERO
        ]
        for i in range(len(sizes) - 1):
            assert sizes[i] < sizes[i + 1]
    
    def test_radius_increases(self):
        """Test radius values increase progressively."""
        radii = [
            F1Theme.RADIUS_SM,
            F1Theme.RADIUS_MD,
            F1Theme.RADIUS_LG,
            F1Theme.RADIUS_XL,
            F1Theme.RADIUS_FULL
        ]
        for i in range(len(radii) - 1):
            assert radii[i] < radii[i + 1]
