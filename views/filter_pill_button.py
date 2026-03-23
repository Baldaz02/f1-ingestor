"""Pill-shaped filter button (tkinter Canvas): capsule ends, radius capped like CSS pill + 50px preference."""
from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional


class FilterPillButton(tk.Canvas):
    """
    Single-row pill: left/right semicircles + center bar (no extra dependencies).
    Requested corner radius is applied up to min(radius, height/2, width/2).
    """

    def __init__(
        self,
        parent: tk.Misc,
        *,
        text: str,
        command: Callable[[], None],
        active_fill: str,
        active_hover: str,
        active_text: str,
        inactive_fill: str,
        inactive_hover: str,
        inactive_text: str,
        pill_height: int = 36,
        corner_radius: int = 50,
        pad_x: int = 18,
        bg_parent: str = "#000000",
        allow_click_when_inactive: bool = True,
    ) -> None:
        """
        allow_click_when_inactive: True for filter chips (unselected still clickable).
        False for e.g. Import when "inactive" means disabled (no click, arrow cursor).
        """
        self._command = command
        self._text = text
        self._allow_click_when_inactive = allow_click_when_inactive
        self._active_fill = active_fill
        self._active_hover = active_hover
        self._active_text = active_text
        self._inactive_fill = inactive_fill
        self._inactive_hover = inactive_hover
        self._inactive_text = inactive_text
        self._pill_height = pill_height
        self._corner_radius = corner_radius
        self._pad_x = pad_x
        self._font = tkfont.Font(family="Arial", size=11, weight="bold")
        self._is_active = False
        self._hover = False
        self._fill_id: Optional[int] = None
        self._text_id: Optional[int] = None

        w = int(self._font.measure(text)) + 2 * pad_x
        w = max(w, 72)

        super().__init__(
            parent,
            width=w,
            height=pill_height,
            bg=bg_parent,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        if not self._allow_click_when_inactive:
            self.configure(cursor="arrow")

        self._redraw()

    def _current_fill(self) -> str:
        if self._is_active:
            return self._active_hover if self._hover else self._active_fill
        return self._inactive_hover if self._hover else self._inactive_fill

    def _current_text_color(self) -> str:
        return self._active_text if self._is_active else self._inactive_text

    def _redraw(self) -> None:
        self.delete("all")
        fill = self._current_fill()
        fg = self._current_text_color()
        w = int(self["width"])
        h = int(self["height"])
        x1, y1, x2, y2 = 0, 0, w, h
        r = min(self._corner_radius, h // 2, w // 2)
        if w < 2 or h < 2:
            return
        # Center rectangle (capsule barrel)
        if w > 2 * r:
            self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=fill, width=0)
        # Left and right semicircle caps
        self.create_oval(x1, y1, x1 + 2 * r, y1 + 2 * r, fill=fill, outline=fill, width=0)
        self.create_oval(x2 - 2 * r, y1, x2, y1 + 2 * r, fill=fill, outline=fill, width=0)
        self.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=self._text,
            font=self._font,
            fill=fg,
        )

    def _on_enter(self, event=None) -> None:
        if not self._allow_click_when_inactive and not self._is_active:
            return
        self._hover = True
        self._redraw()

    def _on_leave(self, event=None) -> None:
        self._hover = False
        self._redraw()

    def _on_click(self, event=None) -> None:
        if not self._allow_click_when_inactive and not self._is_active:
            return
        self._command()

    def set_active(self, active: bool) -> None:
        self._is_active = active
        if not self._allow_click_when_inactive:
            self.configure(cursor="hand2" if active else "arrow")
        self._redraw()

    def set_text(self, text: str) -> None:
        self._text = text
        w = int(self._font.measure(text)) + 2 * self._pad_x
        w = max(w, 72)
        self.configure(width=w)
        self._redraw()
