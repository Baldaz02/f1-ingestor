#!/usr/bin/env python3
"""
F1 Ingestor — Formula 1 schedule application

A desktop application for viewing Formula 1 race schedules from 2019 to 2026.
Built with Python using the MVC architecture pattern and tkinter.

Version: 1.0.0
"""

import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.season_controller import SeasonController
from views.main_window import MainWindow


def main():
    """Main entry point for F1 Ingestor."""
    print("🏎️  Starting F1 Ingestor...")
    if sys.platform == "darwin" and "CommandLineTools" in sys.executable:
        print(
            "\n⚠️  You are using Apple Command Line Tools Python. Its Tk GUI often "
            "aborts on macOS 15 with a version check (e.g. 1507 vs 1506).\n"
            "   Use the project venv instead:\n"
            "   ./venv/bin/python3 main.py\n"
        )

    # Initialize the controller (MVC pattern)
    controller = SeasonController()

    print("🚀 Launching GUI...")
    
    # Create and run the main window (View)
    app = MainWindow(controller)
    app.mainloop()
    
    print("👋 F1 Ingestor closed. Goodbye!")


if __name__ == "__main__":
    main()
