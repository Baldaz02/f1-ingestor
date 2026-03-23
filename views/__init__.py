"""F1 Ingestor views package."""
from .styles import F1Theme

# MainWindow and EventCard use tkinter, import only when needed
# to avoid issues during testing
__all__ = ['F1Theme']
