"""Event card widget for displaying F1 Grand Prix events."""
import tkinter as tk
from typing import Callable, Optional
from models.event import Event, EventStatus
from views.i18n import DEFAULT_LANGUAGE, make_translate
from views.styles import F1Theme


class EventCard(tk.Frame):
    """
    A modern card widget that displays F1 event information.
    Features hover effects, status indicators, and detailed event info.
    """
    
    def __init__(
        self,
        parent,
        event: Event,
        translate: Optional[Callable[[str], str]] = None,
        import_selected: bool = False,
        on_import_toggle: Optional[Callable[[Event, bool], None]] = None,
        **kwargs
    ):
        """
        Initialize the event card.
        
        Args:
            parent: Parent widget
            event: The F1 event to display
            translate: UI string lookup for the current language
            import_selected: Whether this event is marked for import
            on_import_toggle: Callback (event, selected) when the import checkbox changes
        """
        super().__init__(
            parent,
            bg=F1Theme.CARD_BG,
            highlightbackground=F1Theme.CARD_BORDER,
            highlightthickness=1,
            **kwargs
        )
        
        self.event = event
        self._import_selected = import_selected
        self.on_import_toggle = on_import_toggle
        self._t = translate or make_translate(DEFAULT_LANGUAGE)
        self._is_hovered = False
        
        self._setup_ui()
        self._bind_events()
    
    def _setup_ui(self):
        """Set up the card UI components."""
        # Main content frame
        self.content_frame = tk.Frame(self, bg=F1Theme.CARD_BG)
        self.content_frame.pack(fill='both', expand=True, padx=16, pady=16)
        
        # Top section with round badge and event details
        top_frame = tk.Frame(self.content_frame, bg=F1Theme.CARD_BG)
        top_frame.pack(fill='x')
        
        # Left side - Round number badge
        self._create_round_badge(top_frame)
        
        # Right side - Event details
        self._create_event_details(top_frame)
        
        # Bottom - Results (if completed) or note if round was removed from calendar
        if self.event.is_deleted:
            self._create_removed_notice()
        elif self.event.is_completed:
            self._create_results_section()
    
    def _create_round_badge(self, parent):
        """Create optional import checkbox and the round number badge with status indicator."""
        round_row = tk.Frame(parent, bg=F1Theme.CARD_BG)
        round_row.pack(side='left', padx=(0, 16))
        
        if self.on_import_toggle is not None:
            self._import_var = tk.BooleanVar(value=self._import_selected)
            cb = tk.Checkbutton(
                round_row,
                variable=self._import_var,
                command=lambda: self.on_import_toggle(self.event, self._import_var.get()),
                bg=F1Theme.CARD_BG,
                fg=F1Theme.TEXT_PRIMARY,
                selectcolor=F1Theme.SURFACE_ELEVATED,
                activebackground=F1Theme.CARD_BG,
                activeforeground=F1Theme.TEXT_PRIMARY,
                highlightthickness=0,
                bd=0,
                indicatoron=True,
            )
            cb.pack(side='left', padx=(0, 8))
        
        badge_frame = tk.Frame(
            round_row,
            bg=self._get_status_bg_color(),
            width=60,
            height=60
        )
        badge_frame.pack(side='left')
        badge_frame.pack_propagate(False)
        
        # Round number
        round_label = tk.Label(
            badge_frame,
            text=f"R{self.event.round_number:02d}",
            font=('Arial', 16, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=self._get_status_bg_color()
        )
        round_label.pack(expand=True)
        
        # Status indicator dot
        status_color = F1Theme.get_status_color(self.event.status.value)
        status_dot = tk.Label(
            badge_frame,
            text="●",
            font=('Arial', 10),
            fg=status_color,
            bg=self._get_status_bg_color()
        )
        status_dot.pack()
    
    def _create_event_details(self, parent):
        """Create the main event details section."""
        details_frame = tk.Frame(parent, bg=F1Theme.CARD_BG)
        details_frame.pack(side='left', fill='both', expand=True)
        
        # Country flag and name row
        header_frame = tk.Frame(details_frame, bg=F1Theme.CARD_BG)
        header_frame.pack(fill='x', anchor='w')
        
        # Flag emoji
        flag_label = tk.Label(
            header_frame,
            text=self.event.flag_emoji,
            font=('Arial', 20),
            bg=F1Theme.CARD_BG
        )
        flag_label.pack(side='left', padx=(0, 8))
        
        # Event name
        name_label = tk.Label(
            header_frame,
            text=self.event.name,
            font=('Arial', 14, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.CARD_BG,
            anchor='w'
        )
        name_label.pack(side='left', fill='x')
        if self.event.official_name:
            name_label._f1_tooltip_widget = True
            self._attach_tooltip(name_label, self.event.official_name)
        
        # Location
        city_label = tk.Label(
            details_frame,
            text=f"📍 {self.event.city}, {self.event.country}",
            font=('Arial', 10),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.CARD_BG,
            anchor='w'
        )
        city_label.pack(fill='x', pady=(4, 0))
        
        # Date and status row
        date_frame = tk.Frame(details_frame, bg=F1Theme.CARD_BG)
        date_frame.pack(fill='x', pady=(8, 0))
        
        date_label = tk.Label(
            date_frame,
            text=f"📅 {self.event.formatted_date}",
            font=('Arial', 11, 'bold'),
            fg=F1Theme.ACCENT_CYAN,
            bg=F1Theme.CARD_BG
        )
        date_label.pack(side='left')
        
        # Status badge (translated)
        status_key = f"status_{self.event.status.value}"
        status_label = tk.Label(
            date_frame,
            text=f"  {self._t(status_key)}",
            font=('Arial', 9, 'bold'),
            fg=F1Theme.get_status_color(self.event.status.value),
            bg=F1Theme.CARD_BG
        )
        status_label.pack(side='left', padx=(12, 0))
    
    def _create_removed_notice(self):
        """Note when a round was removed from the calendar (excluded from season totals)."""
        tk.Label(
            self.content_frame,
            text=self._t("event_removed_detail"),
            font=('Arial', 12),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.CARD_BG,
            anchor="w",
        ).pack(fill=tk.X, pady=(12, 0))
    
    def _create_results_section(self):
        """Create the results section for completed events."""
        results_frame = tk.Frame(self.content_frame, bg=F1Theme.SURFACE_ELEVATED)
        results_frame.pack(fill='x', pady=(12, 0), ipady=6)
        
        # Create a horizontal layout for results
        results_inner = tk.Frame(results_frame, bg=F1Theme.SURFACE_ELEVATED)
        results_inner.pack(fill='x', padx=8, pady=6)
        
        # Winner
        if self.event.winner:
            self._create_result_item(
                results_inner, "🏆", self.event.winner, F1Theme.ACCENT_GOLD,
                self._t("result_tooltip_winner"),
            )

        # Fastest lap in qualifying
        if self.event.qualifying_fastest_lap:
            self._create_result_item(
                results_inner, "⚡", self.event.qualifying_fastest_lap, F1Theme.ACCENT_ORANGE,
                self._t("result_tooltip_qualifying_fastest"),
            )
        
        # Pole Position
        if self.event.pole_position:
            self._create_result_item(
                results_inner, "Ⓠ", self.event.pole_position, F1Theme.ACCENT_CYAN,
                self._t("result_tooltip_pole"),
            )
        
        # Fastest Lap
        if self.event.fastest_lap:
            self._create_result_item(
                results_inner, "⏱️", self.event.fastest_lap, F1Theme.PRIMARY,
                self._t("result_tooltip_fastest_lap"),
            )
    
    def _attach_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Show a short explanation after a brief hover (trophy / pole / fastest lap)."""
        state = {"tw": None, "after": None}

        def cancel_pending() -> None:
            aid = state["after"]
            if aid is not None:
                try:
                    widget.after_cancel(aid)
                except tk.TclError:
                    pass
                state["after"] = None

        def destroy_tip() -> None:
            tw = state["tw"]
            if tw is not None:
                try:
                    tw.destroy()
                except tk.TclError:
                    pass
                state["tw"] = None

        def show_tip() -> None:
            cancel_pending()
            if state["tw"] is not None:
                return
            tip_bg = F1Theme.SURFACE_ELEVATED
            tw = tk.Toplevel(widget)
            # Hide until styled and placed — avoids a one-frame default (white) shell flash on macOS.
            tw.withdraw()
            tw.wm_overrideredirect(True)
            tw.configure(bg=tip_bg, highlightthickness=0, bd=0)
            try:
                tw.wm_attributes("-topmost", True)
            except tk.TclError:
                pass
            tk.Label(
                tw,
                text=text,
                font=("Arial", 10),
                fg=F1Theme.TEXT_PRIMARY,
                bg=tip_bg,
                padx=10,
                pady=6,
                justify="left",
                wraplength=280,
            ).pack()
            tw.update_idletasks()
            x = widget.winfo_rootx()
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            tw.wm_geometry(f"+{x}+{y}")
            tw.deiconify()
            try:
                tw.lift()
            except tk.TclError:
                pass
            state["tw"] = tw

        def on_enter(event=None) -> None:
            self._on_enter(event)
            cancel_pending()
            state["after"] = widget.after(400, show_tip)

        def on_leave(event=None) -> None:
            cancel_pending()
            destroy_tip()
            self._on_leave(event)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _create_result_item(
        self,
        parent,
        icon: str,
        value: str,
        color: str,
        tooltip: str,
    ):
        """Create a single result item using pack layout."""
        frame = tk.Frame(parent, bg=F1Theme.SURFACE_ELEVATED)
        frame.pack(side='left', expand=True, fill='x')
        
        # Icon and value in one line
        label_widget = tk.Label(
            frame,
            text=f"{icon} {value}",
            font=('Arial', 10, 'bold'),
            fg=color,
            bg=F1Theme.SURFACE_ELEVATED,
            cursor="hand2",
        )
        # Fill the column so the whole result cell is hoverable (not only the text bbox).
        label_widget.pack(anchor='center', expand=True, fill='both')
        # Skip duplicate hover bind in _bind_hover_children; tooltip handlers call _on_enter/_on_leave.
        label_widget._f1_tooltip_widget = True
        self._attach_tooltip(label_widget, tooltip)
    
    def _get_status_bg_color(self) -> str:
        """Get background color based on status."""
        status_bg = {
            EventStatus.COMPLETED: "#0F1A0F",
            EventStatus.UPCOMING: "#0F0F1A",
            EventStatus.CANCELLED: "#1A0F0F",
            EventStatus.IN_PROGRESS: "#1A170F",
            EventStatus.DELETED: "#141418",
        }
        return status_bg.get(self.event.status, F1Theme.SURFACE)
    
    def _bind_events(self):
        """Bind hover only (no card click — import uses the checkbox)."""
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._bind_hover_children(self)
    
    def _bind_hover_children(self, widget):
        """Recursively bind hover to children (skip checkboxes; skip result tooltips — own bindings)."""
        for child in widget.winfo_children():
            if getattr(child, "_f1_tooltip_widget", False):
                self._bind_hover_children(child)
                continue
            if child.winfo_class() != "Checkbutton":
                child.bind("<Enter>", self._on_enter)
                child.bind("<Leave>", self._on_leave)
            self._bind_hover_children(child)
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        if not self._is_hovered:
            self._is_hovered = True
            self.configure(bg=F1Theme.CARD_HOVER, highlightbackground=F1Theme.BORDER_LIGHT)
            self._update_children_bg(self, F1Theme.CARD_HOVER)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        # Check if mouse is still within the card
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        
        if widget is None or not str(widget).startswith(str(self)):
            self._is_hovered = False
            self.configure(bg=F1Theme.CARD_BG, highlightbackground=F1Theme.CARD_BORDER)
            self._update_children_bg(self, F1Theme.CARD_BG)
    
    def _update_children_bg(self, widget, color):
        """Update background color of children (except special colored frames)."""
        for child in widget.winfo_children():
            try:
                if child.winfo_class() == "Checkbutton":
                    child.configure(bg=color, activebackground=color)
                    self._update_children_bg(child, color)
                    continue
                current_bg = child.cget('bg')
                # Don't change special colored backgrounds
                if current_bg in [F1Theme.CARD_BG, F1Theme.CARD_HOVER]:
                    child.configure(bg=color)
                elif current_bg == F1Theme.SURFACE_ELEVATED:
                    pass  # Keep results section color
                elif current_bg in ["#0F1A0F", "#0F0F1A", "#1A0F0F", "#1A170F", "#141418"]:
                    pass  # Keep status badge colors
            except tk.TclError:
                pass
            self._update_children_bg(child, color)
