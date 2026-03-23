"""F1 Theme and styling constants for the application."""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class F1Theme:
    """
    Formula 1 inspired color theme for the application.
    Uses the official F1 color palette with modern UI adaptations.
    """
    
    # Primary Colors - F1 Red
    PRIMARY: str = "#E10600"  # F1 Red
    PRIMARY_DARK: str = "#B30500"
    PRIMARY_LIGHT: str = "#FF2A24"
    
    # Secondary — black UI shell (SECONDARY_DARK is pure black; SECONDARY a hair lighter)
    SECONDARY_DARK: str = "#000000"
    SECONDARY: str = "#0A0A0A"
    SECONDARY_LIGHT: str = "#141414"
    
    # Accent Colors
    ACCENT_GOLD: str = "#FFD700"
    ACCENT_SILVER: str = "#C0C0C0"
    ACCENT_BRONZE: str = "#CD7F32"
    ACCENT_CYAN: str = "#00D2BE"  # Mercedes-inspired
    ACCENT_BLUE: str = "#0600EF"  # Red Bull-inspired
    ACCENT_ORANGE: str = "#FF8700"  # McLaren-inspired
    ACCENT_GREEN: str = "#006F62"  # Aston Martin-inspired
    
    # Text Colors
    TEXT_PRIMARY: str = "#FFFFFF"
    TEXT_SECONDARY: str = "#A0A0B0"
    TEXT_MUTED: str = "#6B6B7B"
    TEXT_DARK: str = "#15151E"
    
    # Status Colors
    STATUS_COMPLETED: str = "#00D26A"  # Green
    STATUS_UPCOMING: str = "#00A9FF"  # Blue
    STATUS_CANCELLED: str = "#FF3D3D"  # Red
    STATUS_IN_PROGRESS: str = "#FFD700"  # Gold/Yellow
    
    # Surface Colors (near-black lifts for panels / inputs)
    SURFACE: str = "#000000"
    SURFACE_ELEVATED: str = "#121212"
    SURFACE_HOVER: str = "#1A1A1A"
    
    # Border Colors
    BORDER: str = "#2A2A2A"
    BORDER_LIGHT: str = "#3D3D3D"
    
    # Card Colors
    CARD_BG: str = "#0A0A0A"
    CARD_HOVER: str = "#141414"
    CARD_BORDER: str = "#252525"
    
    # Gradient definitions (for reference)
    GRADIENT_F1_START: str = "#E10600"
    GRADIENT_F1_END: str = "#8B0000"
    
    # Font configurations
    FONT_FAMILY_TITLE: str = "Titillium Web"
    FONT_FAMILY_BODY: str = "Segoe UI"
    FONT_FAMILY_MONO: str = "JetBrains Mono"
    
    # Fallback fonts
    FONT_FAMILY_FALLBACK: str = "Arial"
    
    # Font sizes
    FONT_SIZE_HERO: int = 48
    FONT_SIZE_H1: int = 32
    FONT_SIZE_H2: int = 24
    FONT_SIZE_H3: int = 18
    FONT_SIZE_BODY: int = 14
    FONT_SIZE_SMALL: int = 12
    FONT_SIZE_TINY: int = 10
    
    # Spacing
    SPACING_XS: int = 4
    SPACING_SM: int = 8
    SPACING_MD: int = 16
    SPACING_LG: int = 24
    SPACING_XL: int = 32
    SPACING_XXL: int = 48
    
    # Border radius
    RADIUS_SM: int = 4
    RADIUS_MD: int = 8
    RADIUS_LG: int = 12
    RADIUS_XL: int = 16
    RADIUS_FULL: int = 999
    
    # Card dimensions
    CARD_WIDTH: int = 320
    CARD_HEIGHT: int = 180
    
    # Window dimensions
    WINDOW_MIN_WIDTH: int = 1280
    WINDOW_MIN_HEIGHT: int = 800
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """Get color for a given status."""
        status_colors = {
            'completed': cls.STATUS_COMPLETED,
            'upcoming': cls.STATUS_UPCOMING,
            'cancelled': cls.STATUS_CANCELLED,
            'in_progress': cls.STATUS_IN_PROGRESS,
            'deleted': cls.TEXT_MUTED,
        }
        return status_colors.get(status.lower(), cls.TEXT_SECONDARY)
    
    @classmethod
    def get_team_color(cls, team: str) -> str:
        """Get color for a given F1 team."""
        team_colors = {
            'red bull': cls.ACCENT_BLUE,
            'ferrari': cls.PRIMARY,
            'mercedes': cls.ACCENT_CYAN,
            'mclaren': cls.ACCENT_ORANGE,
            'aston martin': cls.ACCENT_GREEN,
            'alpine': '#0090FF',
            'williams': '#005AFF',
            'haas': '#B6BABD',
            'sauber': '#52E252',
            'rb': '#6692FF'
        }
        return team_colors.get(team.lower(), cls.TEXT_SECONDARY)
    
    @classmethod
    def get_position_color(cls, position: int) -> str:
        """Get color for podium positions."""
        if position == 1:
            return cls.ACCENT_GOLD
        elif position == 2:
            return cls.ACCENT_SILVER
        elif position == 3:
            return cls.ACCENT_BRONZE
        else:
            return cls.TEXT_SECONDARY
