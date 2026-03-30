"""Build ``Event`` instances from FastF1 season schedules (online)."""
from __future__ import annotations

import sys
import warnings
from datetime import date, datetime
from typing import Any, Callable, List, Optional

from models.data_store import DataStore
from models.event import Event, EventStatus

# Normalize country labels from the schedule to keys in ``DataStore.FLAGS``.
_COUNTRY_ALIASES = {
    "USA": "United States",
    "United States of America": "United States",
    "UK": "United Kingdom",
    "Great Britain": "United Kingdom",
    "UAE": "United Arab Emirates",
    "United Arab Emirates": "United Arab Emirates",
}


def _enable_fastf1_cache() -> None:
    import fastf1
    from pathlib import Path

    cache_dir = Path.home() / ".cache" / "f1_ingestor" / "fastf1"
    cache_dir.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fastf1.Cache.enable_cache(cache_dir)


def _normalize_country(raw: str) -> str:
    s = (raw or "").strip()
    return _COUNTRY_ALIASES.get(s, s)


def _pick_race_datetime(row: Any) -> Optional[datetime]:
    """Prefer EventDate (always present on schedules), then Race session UTC, then other sessions."""
    import pandas as pd

    if "EventDate" in row.index and pd.notna(row["EventDate"]):
        return pd.Timestamp(row["EventDate"]).to_pydatetime()
    for i in range(1, 6):
        s_name = f"Session{i}"
        s_dt = f"Session{i}DateUtc"
        if s_name not in row.index or s_dt not in row.index:
            continue
        if pd.isna(row[s_dt]):
            continue
        name = str(row.get(s_name, "")).lower()
        if "race" in name:
            return pd.Timestamp(row[s_dt]).to_pydatetime()
    for col in ("Session5DateUtc", "Session4DateUtc", "Session3DateUtc", "Session2DateUtc", "Session1DateUtc"):
        if col in row.index and pd.notna(row[col]):
            return pd.Timestamp(row[col]).to_pydatetime()
    return None


def _event_status_for_race_date(race_dt: datetime) -> EventStatus:
    today = date.today()
    d = race_dt.date()
    if d < today:
        return EventStatus.COMPLETED
    return EventStatus.UPCOMING


def _circuit_name(row: Any) -> str:
    import pandas as pd

    for key in ("CircuitShortName", "Location", "OfficialEventName", "EventName"):
        if key in row.index and pd.notna(row[key]) and str(row[key]).strip():
            return str(row[key]).strip()
    return "Circuit"


def events_from_fastf1_schedule(
    year: int,
    *,
    on_chunk: Optional[Callable[[List[Event]], None]] = None,
    on_schedule_progress: Optional[Callable[[int, int, List[Event]], None]] = None,
) -> List[Event]:
    """Load the championship schedule for ``year`` and return ``Event`` rows (rounds only).

    If ``on_chunk`` is set, it is called on the worker thread after each event is appended
    (pass a copy of the list so far) so the UI can refresh incrementally via ``after``.
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError(
            f"pandas is not installed for this Python interpreter:\n  {sys.executable}\n"
            f"Install into the same environment you use to run the app, e.g.:\n"
            f"  {sys.executable} -m pip install pandas\n"
            f"Original error: {e}"
        ) from e
    try:
        import fastf1
    except ImportError as e:
        raise RuntimeError(
            f"fastf1 is not installed for this Python interpreter:\n  {sys.executable}\n"
            f"Install into the same environment you use to run the app, e.g.:\n"
            f"  {sys.executable} -m pip install fastf1\n"
            f"Original error: {e}"
        ) from e

    _enable_fastf1_cache()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            schedule = fastf1.get_event_schedule(year, include_testing=False)
        except TypeError:
            schedule = fastf1.get_event_schedule(year)

    if schedule is None or len(schedule) == 0:
        raise ValueError(f"No schedule returned for season {year}.")

    schedule_row_total = len(schedule)
    events: List[Event] = []
    schedule_idx = 0
    for _, row in schedule.iterrows():
        rn = row.get("RoundNumber")
        if rn is None or pd.isna(rn):
            continue
        try:
            round_num = int(rn)
        except (TypeError, ValueError):
            continue
        if round_num < 1:
            continue

        race_dt = _pick_race_datetime(row)
        if race_dt is None:
            continue

        short = str(row.get("EventName") or "").strip()
        long_name = str(row.get("OfficialEventName") or "").strip()
        if short and long_name:
            display_name = short
            official_name = long_name
        elif short:
            display_name = short
            official_name = None
        elif long_name:
            display_name = long_name
            official_name = None
        else:
            display_name = "Grand Prix"
            official_name = None

        country = _normalize_country(str(row.get("Country", "")))
        city = str(row.get("Location", "") or "").strip() or country
        circuit = _circuit_name(row)
        status = _event_status_for_race_date(race_dt)
        flag = DataStore.FLAGS.get(country, "🏁")

        ev = Event(
            id=f"{year}-R{round_num:02d}",
            name=display_name,
            country=country,
            circuit=circuit,
            city=city,
            date=race_dt,
            round_number=round_num,
            status=status,
            winner=None,
            pole_position=None,
            fastest_lap=None,
            qualifying_fastest_lap=None,
            flag_emoji=flag,
            official_name=official_name,
        )
        events.append(ev)
        schedule_idx += 1
        events.sort(key=lambda e: e.round_number)
        if on_chunk is not None:
            on_chunk(list(events))
        if on_schedule_progress is not None:
            on_schedule_progress(schedule_idx, schedule_row_total, list(events))

    events.sort(key=lambda e: e.round_number)
    if not events:
        raise ValueError(f"No race events parsed from FastF1 schedule for {year}.")
    return events
