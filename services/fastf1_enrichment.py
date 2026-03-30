"""Enrich FastF1-imported events with session results and season champions."""
from __future__ import annotations

import json
import ssl
import sys
import urllib.error
import urllib.request
import warnings
from datetime import date
from typing import Any, Callable, List, Optional, Tuple

from models.event import Event, EventStatus


def _enable_fastf1_cache() -> None:
    import fastf1
    from pathlib import Path

    cache_dir = Path.home() / ".cache" / "f1_ingestor" / "fastf1"
    cache_dir.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fastf1.Cache.enable_cache(cache_dir)


def _import_fastf1_pandas():
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError(
            f"pandas is required. Install with: {sys.executable} -m pip install pandas"
        ) from e
    return pd


def _driver_name_from_results_row(row: Any, pd: Any) -> Optional[str]:
    if row is None or len(row) == 0:
        return None
    if "FullName" in row.index and pd.notna(row["FullName"]):
        return str(row["FullName"]).strip()
    if "BroadcastName" in row.index and pd.notna(row["BroadcastName"]):
        return str(row["BroadcastName"]).strip()
    if "Abbreviation" in row.index and pd.notna(row["Abbreviation"]):
        return str(row["Abbreviation"]).strip()
    return None


def _winner_from_race_session(session: Any, pd: Any) -> Optional[str]:
    r = session.results
    if r is None or len(r) == 0:
        return None
    pos = pd.to_numeric(r["Position"], errors="coerce")
    top = r[pos == 1]
    if len(top) == 0:
        top = r.sort_values("Position", na_position="last").head(1)
    if len(top) == 0:
        return None
    return _driver_name_from_results_row(top.iloc[0], pd)


def _fastest_lap_driver(session: Any, pd: Any) -> Optional[str]:
    try:
        fastest = session.laps.pick_fastest()
    except Exception:
        return None
    if fastest is None or len(fastest) == 0:
        return None
    try:
        abbr = fastest["Driver"]
    except Exception:
        return None
    res = session.results
    if res is None or len(res) == 0:
        return str(abbr) if abbr is not None else None
    match = res[res["Abbreviation"] == abbr]
    if len(match) == 0:
        return str(abbr)
    return _driver_name_from_results_row(match.iloc[0], pd)


def _load_qualifying_session(fastf1: Any, year: int, round_num: int) -> Any:
    for ident in ("Q", "SQ"):
        try:
            s = fastf1.get_session(year, round_num, ident)
            s.load()
            if s.laps is not None and len(s.laps) > 0:
                return s
        except Exception:
            continue
    return None


def _fill_event_sessions(
    year: int,
    ev: Event,
    fastf1: Any,
    pd: Any,
    *,
    include_pole: bool = True,
) -> None:
    if ev.status != EventStatus.COMPLETED:
        return
    try:
        session_r = fastf1.get_session(year, ev.round_number, "R")
        session_r.load()
    except Exception:
        return

    w = _winner_from_race_session(session_r, pd)
    if w:
        ev.winner = w
    rfl = _fastest_lap_driver(session_r, pd)
    if rfl:
        ev.fastest_lap = rfl

    session_q = _load_qualifying_session(fastf1, year, ev.round_number)
    if session_q is not None:
        qfl = _fastest_lap_driver(session_q, pd)
        if qfl:
            ev.qualifying_fastest_lap = qfl
        if not include_pole:
            return
        try:
            qr = session_q.results
            pos = pd.to_numeric(qr["Position"], errors="coerce")
            pole = qr[pos == 1]
            if len(pole) > 0:
                ev.pole_position = _driver_name_from_results_row(pole.iloc[0], pd)
        except Exception:
            pass


def enrich_events_from_fastf1_sessions(
    year: int,
    events: List[Event],
    *,
    on_chunk: Optional[Callable[[List[Event]], None]] = None,
    on_progress: Optional[Callable[[float, str, Optional[int]], None]] = None,
    round_filter: Optional[Callable[[Event], bool]] = None,
    include_pole: bool = True,
) -> List[Event]:
    """Load race and qualifying sessions for completed rounds; fill winner, laps, pole (optional)."""
    try:
        import fastf1
    except ImportError as e:
        raise RuntimeError(
            f"fastf1 is required. Install with: {sys.executable} -m pip install fastf1"
        ) from e
    pd = _import_fastf1_pandas()
    _enable_fastf1_cache()
    ordered = sorted(events, key=lambda e: e.round_number)
    to_process = [
        ev
        for ev in ordered
        if ev.status == EventStatus.COMPLETED
        and (round_filter is None or round_filter(ev))
    ]
    n = len(to_process)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i, ev in enumerate(to_process):
            _fill_event_sessions(
                year, ev, fastf1, pd, include_pole=include_pole
            )
            if on_progress is not None and n > 0:
                pct = 45.0 + (i + 1) / n * 48.0
                on_progress(pct, "enrichment", ev.round_number)
            if on_chunk is not None:
                on_chunk(list(events))
    return events


def _season_last_round(events: List[Event]) -> int:
    return max(e.round_number for e in events) if events else 1


def _season_complete(events: List[Event]) -> bool:
    if not events:
        return False
    last = max(e.date for e in events)
    return last.date() < date.today()


def fetch_season_champions_from_ergast(year: int, events: List[Event]) -> Tuple[Optional[str], Optional[str]]:
    """Driver and constructor champions after the final round (Ergast JSON API)."""
    if not _season_complete(events):
        return None, None
    last_round = _season_last_round(events)
    base = "https://ergast.com/api/f1"
    ctx = ssl.create_default_context()
    driver_name: Optional[str] = None
    constructor_name: Optional[str] = None
    ua = {"User-Agent": "F1-Ingestor/1.0 (https://github.com/Baldaz02/f1-ingestor)"}

    try:
        url_d = f"{base}/{year}/{last_round}/driverStandings.json"
        req_d = urllib.request.Request(url_d, headers=ua)
        with urllib.request.urlopen(req_d, context=ctx, timeout=45) as resp:
            data = json.loads(resp.read().decode())
        lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists") or []
        if lists:
            standings = lists[0].get("DriverStandings") or []
            for s in standings:
                if str(s.get("position")) == "1":
                    d = s.get("Driver") or {}
                    gn = d.get("givenName", "")
                    fn = d.get("familyName", "")
                    driver_name = f"{gn} {fn}".strip()
                    break
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        pass

    try:
        url_c = f"{base}/{year}/{last_round}/constructorStandings.json"
        req_c = urllib.request.Request(url_c, headers=ua)
        with urllib.request.urlopen(req_c, context=ctx, timeout=45) as resp:
            data = json.loads(resp.read().decode())
        lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists") or []
        if lists:
            standings = lists[0].get("ConstructorStandings") or []
            for s in standings:
                if str(s.get("position")) == "1":
                    c = s.get("Constructor") or {}
                    constructor_name = c.get("name")
                    break
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        pass

    return driver_name, constructor_name
