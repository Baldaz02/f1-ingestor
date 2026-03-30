"""Orchestrate FastF1 schedule load, session enrichment, and Ergast champions for import flows."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Callable, List, Optional, Set

from models.event import Event
from services.fastf1_enrichment import (
    enrich_events_from_fastf1_sessions,
    fetch_season_champions_from_ergast,
)
from services.fastf1_schedule import events_from_fastf1_schedule


class _FastF1LogHandler(logging.Handler):
    """Send ``fastf1`` log records to a UI callback."""

    def __init__(self, on_log: Callable[[str], None]) -> None:
        super().__init__()
        self._on_log = on_log

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._on_log(self.format(record))
        except Exception:
            pass


@contextmanager
def _fastf1_logging_to_callback(on_log: Optional[Callable[[str], None]]):
    """Forward ``logging`` records from the ``fastf1`` namespace to ``on_log``."""
    if on_log is None:
        yield
        return
    handler = _FastF1LogHandler(on_log)
    handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    log = logging.getLogger("fastf1")
    prev_level = log.level
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    try:
        yield
    finally:
        log.removeHandler(handler)
        log.setLevel(prev_level)


def run_fastf1_import(
    year: int,
    *,
    selected_round_numbers: Optional[Set[int]] = None,
    on_progress: Optional[Callable[[float, str, Optional[int]], None]] = None,
    on_log: Optional[Callable[[str], None]] = None,
    on_chunk: Optional[Callable[[List[Event]], None]] = None,
) -> tuple[List[Event], Optional[str], Optional[str]]:
    """
    Used from the checkbox import screen only: load schedule, enrich rounds (optional filter),
    then fetch driver/constructor champions when the season is complete.

    Enrichment fills race winner, qualifying fastest lap, and race fastest lap (not pole).
    The calendar “Import events” action loads the schedule alone — no enrichment.
    """
    events: List[Event] = []

    def _prog(pct: float, step: str, round_num: Optional[int] = None) -> None:
        if on_progress is not None:
            on_progress(pct, step, round_num)

    def _sched_progress(idx: int, total: int, evs: List[Event]) -> None:
        pct = (idx / max(total, 1)) * 45.0
        _prog(pct, "schedule", None)
        if on_chunk is not None:
            on_chunk(list(evs))

    def _round_filter(ev: Event) -> bool:
        if selected_round_numbers is None:
            return True
        return ev.round_number in selected_round_numbers

    def _enrich_progress(pct: float, step: str, round_num: Optional[int] = None) -> None:
        _prog(pct, step, round_num)

    with _fastf1_logging_to_callback(on_log):
        events = events_from_fastf1_schedule(
            year,
            on_chunk=None,
            on_schedule_progress=_sched_progress,
        )
        enrich_events_from_fastf1_sessions(
            year,
            events,
            on_chunk=on_chunk,
            on_progress=_enrich_progress,
            round_filter=_round_filter,
            include_pole=False,
        )

    _prog(94.0, "champions", None)
    d_ch, c_ch = fetch_season_champions_from_ergast(year, events)
    if d_ch and on_log:
        on_log(f"Driver champion: {d_ch}")
    if c_ch and on_log:
        on_log(f"Constructor champion: {c_ch}")
    _prog(100.0, "done", None)

    return events, d_ch, c_ch
