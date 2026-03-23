"""Main window view for F1 Ingestor."""
import re
import tkinter as tk
from tkinter import ttk
from typing import List, Set
from controllers.season_controller import SeasonController
from models.event import Event
from views.event_card import EventCard
from views.i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_CODES,
    get_ui_string,
    language_option_display,
)
from views.filter_pill_button import FilterPillButton
from views.styles import F1Theme

# Monochrome symbols (no emoji): white/black reads on colored pills via active_text / inactive_text.
FILTER_ICONS = {
    "all": "\u2630",  # ☰ trigram — “all” scope
    "completed": "\u2713",  # ✓ check — white on green when active
    "upcoming": "\u25B6\u25B6",  # ▶▶ double forward, tight spacing
    "cancelled": "\u2715",  # ✕ cross — white on red when active
}

# Import: lighter blue than theme ACCENT_BLUE; U+21EA = upload-style arrow from bar.
IMPORT_ACTION_ICON = "\u21ea"
_IMPORT_BLUE_ACTIVE = "#4A63FF"
_IMPORT_BLUE_HOVER = "#3A52D8"

# "All" uses neutral slate — only completed/upcoming/cancelled use status colors (less visual noise).
_FILTER_ALL_ACTIVE = "#3D3D4A"
_FILTER_ALL_HOVER = "#4A4A58"


def _event_name_without_grand_prix(name: str) -> str:
    """Strip a trailing 'Grand Prix' from official titles (import list only)."""
    s = name.strip()
    shortened = re.sub(r"\s+Grand Prix\s*$", "", s, flags=re.IGNORECASE).strip()
    return shortened if shortened else s


class MainWindow(tk.Tk):
    """
    Main application window for F1 Ingestor.
    Features a modern dark theme with F1-inspired styling.
    """
    
    # Pagination settings
    EVENTS_PER_PAGE = 6  # 2 rows x 3 columns
    
    def __init__(self, controller: SeasonController):
        """
        Initialize the main window.
        
        Args:
            controller: The season controller for data management
        """
        super().__init__()
        
        self.controller = controller
        self.controller.add_observer(self._on_data_changed)
        
        self._current_filter = "all"
        self._lang = DEFAULT_LANGUAGE
        self._current_page = 1
        self._total_pages = 1
        self._import_selected_ids: Set[str] = set()
        self._import_view_active = False
        self._pagination_syncing = False
        self._pagination_prev_packed = False
        self._pagination_next_packed = False
        self._last_header_progress = 0.0
        
        self._setup_styles()
        self._setup_window()
        self._setup_ui()
        self._load_data()
    
    def _t(self, key: str) -> str:
        """Localized UI string for the current language."""
        return get_ui_string(self._lang, key)
    
    def _import_selected_heading_text(self) -> str:
        return self._t("import_selected_heading").format(year=self.controller.current_year)
    
    def _dropdown_menu_kwargs(self) -> dict:
        """Styling for tk.Menu popups (season / language)."""
        return {
            "bg": F1Theme.SURFACE_ELEVATED,
            "fg": F1Theme.TEXT_PRIMARY,
            "activebackground": F1Theme.SURFACE_HOVER,
            "activeforeground": F1Theme.TEXT_PRIMARY,
            "activeborderwidth": 0,
            "bd": 0,
            "relief": "flat",
            "font": ("Arial", 13),
        }
    
    def _post_year_menu(self, event) -> None:
        """Show year list at pointer; works when re-opening while current year is selected."""
        x, y = event.x_root, event.y_root

        def _post() -> None:
            try:
                self._year_menu.unpost()
            except (tk.TclError, AttributeError):
                pass
            try:
                self._year_menu.post(x, y)
            except tk.TclError:
                pass

        self.after_idle(_post)
    
    def _rebuild_year_menu(self) -> None:
        if not hasattr(self, "_year_menu"):
            return
        self._year_menu.delete(0, "end")
        for y in self.controller.get_available_years():
            self._year_menu.add_command(
                label=str(y),
                command=lambda yy=y: self._on_year_menu_pick(yy),
            )
    
    def _on_year_menu_pick(self, year: int) -> None:
        if int(self.year_var.get()) == year:
            return
        self.year_var.set(str(year))
        self._apply_year_change()
    
    def _apply_year_change(self) -> None:
        """Sync controller after the selected season year changes."""
        self._current_page = 1
        self.controller.current_year = int(self.year_var.get())
        self._import_selected_ids.clear()
        if self._import_view_active:
            self._import_view_active = False
            self._set_import_screen_visible(False)
        self._update_import_bar()
    
    def _post_lang_menu(self, event) -> None:
        """Show language list at pointer; works when re-opening while current language is selected."""
        x, y = event.x_root, event.y_root

        def _post() -> None:
            try:
                self._lang_menu.unpost()
            except (tk.TclError, AttributeError):
                pass
            try:
                self._lang_menu.post(x, y)
            except tk.TclError:
                pass

        self.after_idle(_post)
    
    def _on_lang_menu_pick(self, code: str) -> None:
        if code == self._lang:
            return
        self._lang = code
        self.lang_var.set(language_option_display(code))
        self._refresh_language_ui()
    
    def _setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('.', 
            background=F1Theme.SECONDARY,
            foreground=F1Theme.TEXT_PRIMARY,
            fieldbackground=F1Theme.SURFACE_ELEVATED
        )
        
        style.configure('TFrame', background=F1Theme.SECONDARY)
        style.configure('Header.TFrame', background=F1Theme.SECONDARY_DARK)
        style.configure('Card.TFrame', background=F1Theme.CARD_BG)
        style.configure('Surface.TFrame', background=F1Theme.SURFACE)
        
        style.configure('TLabel', 
            background=F1Theme.SECONDARY, 
            foreground=F1Theme.TEXT_PRIMARY,
            font=('Arial', 12)
        )
        style.configure('Header.TLabel', 
            background=F1Theme.SECONDARY_DARK, 
            foreground=F1Theme.TEXT_PRIMARY
        )
        style.configure('Title.TLabel', 
            background=F1Theme.SECONDARY_DARK, 
            foreground=F1Theme.PRIMARY,
            font=('Arial', 48, 'bold')
        )
        style.configure('Subtitle.TLabel', 
            background=F1Theme.SECONDARY_DARK, 
            foreground=F1Theme.TEXT_PRIMARY,
            font=('Arial', 32, 'bold')
        )
        style.configure('Stats.TLabel', 
            background=F1Theme.SECONDARY_DARK, 
            foreground=F1Theme.TEXT_SECONDARY,
            font=('Arial', 13)
        )
        style.configure('Muted.TLabel', 
            background=F1Theme.SECONDARY_DARK, 
            foreground=F1Theme.TEXT_MUTED,
            font=('Arial', 12, 'bold')
        )
        
        style.configure('TButton',
            background=F1Theme.SURFACE_ELEVATED,
            foreground=F1Theme.TEXT_PRIMARY,
            font=('Arial', 12, 'bold'),
            padding=(16, 8),
            focuscolor=F1Theme.SURFACE_ELEVATED
        )
        style.map('TButton',
            background=[('active', F1Theme.SURFACE_HOVER)],
            foreground=[('active', F1Theme.TEXT_PRIMARY)],
            focuscolor=[('focus', F1Theme.SURFACE_ELEVATED)]
        )
        
        style.configure('Primary.TButton',
            background=F1Theme.PRIMARY,
            foreground=F1Theme.TEXT_PRIMARY
        )
        style.map('Primary.TButton',
            background=[('active', F1Theme.PRIMARY_DARK)]
        )
        
        style.configure('Filter.TButton',
            background=F1Theme.SURFACE_ELEVATED,
            foreground=F1Theme.TEXT_PRIMARY,
            padding=(20, 6)
        )
        
        style.configure('Page.TButton',
            background=F1Theme.SURFACE_ELEVATED,
            foreground=F1Theme.TEXT_PRIMARY,
            padding=(10, 6)
        )
        style.configure('PageActive.TButton',
            background=F1Theme.PRIMARY,
            foreground=F1Theme.TEXT_PRIMARY,
            padding=(10, 6)
        )
        
        style.configure('TEntry',
            fieldbackground=F1Theme.SURFACE_ELEVATED,
            foreground=F1Theme.TEXT_PRIMARY,
            insertcolor=F1Theme.TEXT_PRIMARY,
            focuscolor=F1Theme.BORDER
        )
        style.map('TEntry',
            focuscolor=[('focus', F1Theme.BORDER)]
        )
    
    def _setup_window(self):
        """Configure the main window."""
        self.title(f"🏎️ {self._t('window_title')}")
        self.geometry(f"{F1Theme.WINDOW_MIN_WIDTH}x{F1Theme.WINDOW_MIN_HEIGHT}")
        self.minsize(F1Theme.WINDOW_MIN_WIDTH, F1Theme.WINDOW_MIN_HEIGHT)
        self.configure(bg=F1Theme.SECONDARY)
    
    def _setup_ui(self):
        """Set up the main UI components."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create UI sections
        self._create_header()
        self._create_main_content()
        self._create_footer()
    
    def _create_header(self):
        """Header: F1 + CALENDAR | bar + % with rounds summary directly under the bar (right)."""
        self._header = tk.Frame(self, bg=F1Theme.SECONDARY_DARK)
        self._header.grid(row=0, column=0, sticky="ew")
        
        top = tk.Frame(self._header, bg=F1Theme.SECONDARY_DARK)
        top.pack(fill=tk.X, padx=24, pady=(16, 12))
        top.grid_columnconfigure(1, weight=1)
        
        left = tk.Frame(top, bg=F1Theme.SECONDARY_DARK)
        
        tk.Label(
            left,
            text="F1",
            font=('Arial', 48, 'bold'),
            fg=F1Theme.PRIMARY,
            bg=F1Theme.SECONDARY_DARK,
        ).pack(side=tk.LEFT)
        
        self._calendar_title_label = tk.Label(
            left,
            text=self._t("calendar_title"),
            font=('Arial', 32, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SECONDARY_DARK,
        )
        self._calendar_title_label.pack(side=tk.LEFT, padx=(8, 0))
        
        prog_col = tk.Frame(top, bg=F1Theme.SECONDARY_DARK)
        bar_row = tk.Frame(prog_col, bg=F1Theme.SECONDARY_DARK)
        
        self._header_progress_bar_width = 280
        self._header_progress_canvas = tk.Canvas(
            bar_row,
            width=self._header_progress_bar_width,
            height=10,
            bg=F1Theme.BORDER,
            highlightthickness=0,
            bd=0,
        )
        self._header_progress_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self._header_progress_canvas.bind("<Configure>", self._on_header_progress_canvas_configure)
        
        self._header_progress_pct_label = tk.Label(
            bar_row,
            text="0%",
            font=('Arial', 12, 'bold'),
            fg=self._header_progress_accent_color(0.0),
            bg=F1Theme.SECONDARY_DARK,
        )
        self._header_progress_pct_label.pack(side=tk.LEFT)
        
        self._header_progress_summary = tk.Label(
            prog_col,
            text="",
            font=('Arial', 13),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.SECONDARY_DARK,
            anchor="e",
            justify=tk.RIGHT,
        )
        
        bar_row.pack(anchor="e")
        self._header_progress_summary.pack(anchor="e", pady=(2, 0))
        
        left.grid(row=0, column=0, sticky="nw", padx=(0, 16))
        # Align progress block with ~48px title row; bar + tight summary under it.
        prog_col.grid(row=0, column=1, sticky="ne", pady=(14, 0))
    
    def _on_header_progress_canvas_configure(self, event=None) -> None:
        self._draw_header_progress_bar(self._last_header_progress)
    
    @staticmethod
    def _header_progress_accent_color(pct: float) -> str:
        """Red below 50%, orange from 50–99%, green only when rounded to 100%."""
        p = int(round(max(0.0, min(100.0, float(pct)))))
        if p >= 100:
            return F1Theme.STATUS_COMPLETED
        if p >= 50:
            return F1Theme.ACCENT_ORANGE
        return F1Theme.PRIMARY

    def _draw_header_progress_bar(self, pct: float) -> None:
        """Fill bar; color matches % label. Track uses BORDER. pct is 0–100."""
        self._last_header_progress = max(0.0, min(100.0, float(pct)))
        fill_color = self._header_progress_accent_color(self._last_header_progress)
        c = self._header_progress_canvas
        c.delete("all")
        try:
            w = max(2, int(c.winfo_width()))
            h = max(2, int(c.winfo_height()))
        except tk.TclError:
            return
        if w < 2:
            w = self._header_progress_bar_width
        fill_w = int(w * self._last_header_progress / 100.0)
        c.create_rectangle(0, 0, w, h, fill=F1Theme.BORDER, outline="", width=0)
        if fill_w > 0:
            c.create_rectangle(0, 0, fill_w, h, fill=fill_color, outline="", width=0)
    
    def _create_main_content(self):
        """Create the main content area."""
        self._main_frame = tk.Frame(self, bg=F1Theme.SECONDARY)
        main_frame = self._main_frame
        main_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        self._create_toolbar(main_frame)
        self._create_import_bar(main_frame)
        self._create_stack(main_frame)
    
    def _create_toolbar(self, parent):
        """Create the toolbar: season, language, filters."""
        self._toolbar = tk.Frame(parent, bg=F1Theme.SURFACE, padx=16, pady=12)
        toolbar = self._toolbar
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        toolbar.grid_columnconfigure(1, weight=1)
        
        left_controls = tk.Frame(toolbar, bg=F1Theme.SURFACE)
        left_controls.grid(row=0, column=0, sticky="w")
        
        season_cluster = tk.Frame(left_controls, bg=F1Theme.SURFACE)
        season_cluster.pack(side=tk.LEFT, padx=(0, 0), anchor="center")
        
        self._season_header_label = tk.Label(
            season_cluster,
            text=self._t("season_label"),
            font=('Arial', 12, 'bold'),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.SURFACE,
        )
        self._season_header_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.year_var = tk.StringVar(value=str(self.controller.current_year))
        year_btn_frame = tk.Frame(season_cluster, bg=F1Theme.SURFACE, highlightthickness=0, bd=0)
        year_btn_frame.pack(side=tk.LEFT)
        year_row = tk.Frame(year_btn_frame, bg=F1Theme.SURFACE, cursor="hand2")
        year_row.pack()
        
        self._year_display_label = tk.Label(
            year_row,
            textvariable=self.year_var,
            font=('Arial', 16, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SURFACE,
            cursor="hand2",
        )
        self._year_display_label.pack(side=tk.LEFT, padx=(0, 6))
        
        self._year_menu_arrow = tk.Label(
            year_row,
            text="▾",
            font=('Arial', 12, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SURFACE,
            cursor="hand2",
        )
        self._year_menu_arrow.pack(side=tk.LEFT)
        
        self._year_menu = tk.Menu(self, tearoff=0, **self._dropdown_menu_kwargs())
        self._rebuild_year_menu()
        for w in (
            year_btn_frame,
            year_row,
            self._year_display_label,
            self._year_menu_arrow,
        ):
            w.bind("<Button-1>", self._post_year_menu)
        
        # Language: globe + label + chevron; menu opens on tap (no combobox field).
        lang_frame = tk.Frame(left_controls, bg=F1Theme.SURFACE)
        lang_frame.pack(side=tk.LEFT, padx=(48, 0))
        
        self._lang_globe_label = tk.Label(
            lang_frame,
            text="🌐",
            font=('Arial', 18),
            bg=F1Theme.SURFACE,
            cursor="hand2",
        )
        self._lang_globe_label.pack(side="left", padx=(0, 10))
        
        self.lang_var = tk.StringVar(value=language_option_display(self._lang))
        lang_row = tk.Frame(lang_frame, bg=F1Theme.SURFACE, cursor="hand2")
        lang_row.pack(side="left")
        
        self._lang_display_label = tk.Label(
            lang_row,
            textvariable=self.lang_var,
            font=('Arial', 13, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SURFACE,
            cursor='hand2',
        )
        self._lang_display_label.pack(side=tk.LEFT, padx=(0, 6))
        
        self._lang_menu_arrow = tk.Label(
            lang_row,
            text="▾",
            font=('Arial', 12, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SURFACE,
            cursor='hand2',
        )
        self._lang_menu_arrow.pack(side=tk.LEFT)
        
        self._lang_menu = tk.Menu(self, tearoff=0, **self._dropdown_menu_kwargs())
        for code in SUPPORTED_CODES:
            self._lang_menu.add_command(
                label=language_option_display(code),
                command=lambda c=code: self._on_lang_menu_pick(c),
            )
        for w in (
            lang_frame,
            lang_row,
            self._lang_globe_label,
            self._lang_display_label,
            self._lang_menu_arrow,
        ):
            w.bind("<Button-1>", self._post_lang_menu)
        
        # Filter buttons
        filter_frame = tk.Frame(toolbar, bg=F1Theme.SURFACE)
        filter_frame.grid(row=0, column=1, sticky="e")
        
        self._filter_header_label = tk.Label(
            filter_frame,
            text=self._t("filter_label"),
            font=('Arial', 12),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.SURFACE
        )
        self._filter_header_label.pack(side="left", padx=(0, 12))
        
        self.filter_buttons = {}
        # Capsule pills (~50px radius capped by height/2). Active status filters: white ✓ / ▶ / ✕ + label.
        filters = [
            ("all", _FILTER_ALL_ACTIVE, _FILTER_ALL_HOVER, F1Theme.TEXT_PRIMARY),
            ("completed", F1Theme.STATUS_COMPLETED, "#00A654", F1Theme.TEXT_PRIMARY),
            ("upcoming", F1Theme.STATUS_UPCOMING, "#0087CC", F1Theme.TEXT_PRIMARY),
            ("cancelled", F1Theme.STATUS_CANCELLED, "#CC3030", F1Theme.TEXT_PRIMARY),
        ]
        
        for value, active_fill, hover_fill, active_text in filters:
            is_active = value == "all"
            label = f"{FILTER_ICONS[value]}  {self._t(f'filter_{value}')}"
            btn = FilterPillButton(
                filter_frame,
                text=label,
                command=lambda v=value: self._on_filter_changed(v),
                active_fill=active_fill,
                active_hover=hover_fill,
                active_text=active_text,
                inactive_fill=F1Theme.SURFACE_ELEVATED,
                inactive_hover=F1Theme.SURFACE_HOVER,
                inactive_text=F1Theme.TEXT_SECONDARY,
                pill_height=36,
                corner_radius=50,
                bg_parent=F1Theme.SURFACE,
            )
            btn.pack(side=tk.LEFT, padx=4)
            btn.set_active(is_active)
            self.filter_buttons[value] = btn
    
    def _create_import_bar(self, parent):
        """Count of events marked for import + Import action (same row as toolbar area)."""
        self._import_bar = tk.Frame(parent, bg=F1Theme.SURFACE, padx=16, pady=10)
        self._import_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        
        self._import_count_label = tk.Label(
            self._import_bar,
            text=self._t("import_selection_count").format(count=0),
            font=('Arial', 12),
            fg=F1Theme.TEXT_SECONDARY,
            bg=F1Theme.SURFACE,
            anchor="w",
        )
        self._import_count_label.pack(side="left")
        
        # Same capsule as filters; blue + upload icon (not download / warning orange).
        self._import_btn = FilterPillButton(
            self._import_bar,
            text=f"{IMPORT_ACTION_ICON}  {self._t('import_action')}",
            command=self._on_import_go,
            active_fill=_IMPORT_BLUE_ACTIVE,
            active_hover=_IMPORT_BLUE_HOVER,
            active_text=F1Theme.TEXT_PRIMARY,
            inactive_fill="#141414",
            inactive_hover="#141414",
            inactive_text=F1Theme.TEXT_MUTED,
            pill_height=36,
            corner_radius=50,
            pad_x=20,
            bg_parent=F1Theme.SURFACE,
            allow_click_when_inactive=False,
        )
        self._import_btn.pack(side=tk.LEFT, padx=(16, 0))
        self._import_btn.set_active(False)
    
    def _create_stack(self, parent):
        """Calendar + pagination, or blank import placeholder (same panel, no new window)."""
        self._stack = tk.Frame(parent, bg=F1Theme.SECONDARY)
        self._stack.grid(row=2, column=0, sticky="nsew")
        self._stack.grid_rowconfigure(0, weight=1)
        self._stack.grid_columnconfigure(0, weight=1)
        
        self._calendar_panel = tk.Frame(self._stack, bg=F1Theme.SECONDARY)
        self._calendar_panel.grid(row=0, column=0, sticky="nsew")
        self._calendar_panel.grid_rowconfigure(0, weight=1)
        self._calendar_panel.grid_columnconfigure(0, weight=1)
        
        self._create_events_container(self._calendar_panel)
        self._create_pagination(self._calendar_panel)
        
        self._import_panel = tk.Frame(self._stack, bg=F1Theme.SECONDARY)
        import_inner = tk.Frame(self._import_panel, bg=F1Theme.SECONDARY)
        import_inner.pack(fill=tk.BOTH, expand=True)
        
        # Same strip as main header: dark bar, ← flush left, then F1 + CALENDAR (same fonts/colors)
        self._import_top_bar = tk.Frame(import_inner, bg=F1Theme.SECONDARY_DARK, height=120)
        self._import_top_bar.pack(fill=tk.X)
        self._import_top_bar.pack_propagate(False)
        
        import_header_row = tk.Frame(self._import_top_bar, bg=F1Theme.SECONDARY_DARK)
        import_header_row.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        
        self._import_back_label = tk.Label(
            import_header_row,
            text="←",
            font=('Arial', 20, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SECONDARY_DARK,
            cursor="hand2",
            padx=8,
            pady=4,
        )
        self._import_back_label.pack(side=tk.LEFT, padx=(0, 16))
        self._import_back_label.bind("<Button-1>", lambda e: self._on_import_back())
        
        import_logo_frame = tk.Frame(import_header_row, bg=F1Theme.SECONDARY_DARK)
        import_logo_frame.pack(side=tk.LEFT)
        
        tk.Label(
            import_logo_frame,
            text="F1",
            font=('Arial', 48, 'bold'),
            fg=F1Theme.PRIMARY,
            bg=F1Theme.SECONDARY_DARK,
        ).pack(side=tk.LEFT)
        
        self._import_calendar_title_label = tk.Label(
            import_logo_frame,
            text=self._t("calendar_title"),
            font=('Arial', 32, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SECONDARY_DARK,
        )
        self._import_calendar_title_label.pack(side=tk.LEFT, padx=(8, 0))
        
        self._import_body = tk.Frame(import_inner, bg=F1Theme.SECONDARY)
        self._import_body.pack(fill=tk.BOTH, expand=True, padx=28, pady=(20, 28))
        
        self._import_selected_heading_label = tk.Label(
            self._import_body,
            text=self._import_selected_heading_text(),
            font=('Arial', 12, 'bold'),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.SECONDARY,
            anchor="w",
        )
        self._import_selected_heading_label.pack(fill=tk.X, pady=(0, 22))
        
        self._import_list_container = tk.Frame(self._import_body, bg=F1Theme.SECONDARY)
        # Do not fill=X: list width follows content so two columns stay side by side, not screen halves.
        self._import_list_container.pack(anchor="w", pady=(0, 20))
        
        self._import_panel.grid_remove()
    
    def _create_events_container(self, parent):
        """Create the events container."""
        self.events_container = tk.Frame(parent, bg=F1Theme.SECONDARY)
        self.events_container.grid(row=0, column=0, sticky="nsew")
        self.events_container.grid_rowconfigure((0, 1), weight=1)
        self.events_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
    
    def _create_pagination(self, parent):
        """Pagination: ← | Page [entry] of N | → — right-aligned; arrows are labels on surface."""
        pagination_frame = tk.Frame(parent, bg=F1Theme.SURFACE, height=60)
        pagination_frame.grid(row=1, column=0, sticky="ew", pady=(16, 0))
        pagination_frame.grid_propagate(False)
        pagination_frame.grid_columnconfigure(0, weight=1)
        
        right_cluster = tk.Frame(pagination_frame, bg=F1Theme.SURFACE)
        right_cluster.grid(row=0, column=0, sticky="e", padx=(0, 16), pady=12)
        
        self._pagination_prev_arrow = tk.Label(
            right_cluster,
            text="←",
            font=('Arial', 16, 'bold'),
            bg=F1Theme.SURFACE,
            fg=F1Theme.TEXT_PRIMARY,
            padx=6,
            pady=2,
            cursor='hand2',
        )
        self._pagination_prev_arrow.bind("<Button-1>", lambda e: self._on_prev_page())
        
        page_cluster = tk.Frame(right_cluster, bg=F1Theme.SURFACE)
        self._pagination_page_cluster = page_cluster
        page_cluster.pack(side=tk.LEFT)
        
        self._pagination_page_label = tk.Label(
            page_cluster,
            text=self._t("pagination_page_word"),
            font=('Arial', 12),
            fg=F1Theme.TEXT_SECONDARY,
            bg=F1Theme.SURFACE,
        )
        self._pagination_page_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self._page_entry_var = tk.StringVar(value="1")
        self._page_entry = tk.Entry(
            page_cluster,
            textvariable=self._page_entry_var,
            width=5,
            font=('Arial', 12, 'bold'),
            justify='center',
            bg=F1Theme.SURFACE_ELEVATED,
            fg=F1Theme.TEXT_PRIMARY,
            insertbackground=F1Theme.TEXT_PRIMARY,
            relief='flat',
            highlightthickness=1,
            highlightbackground=F1Theme.BORDER,
            highlightcolor=F1Theme.BORDER,
        )
        self._page_entry.pack(side=tk.LEFT, ipady=4)
        self._page_entry.bind("<Return>", self._on_page_entry_return)
        self._page_entry.bind("<FocusOut>", self._on_page_entry_focusout)
        
        self._pagination_of_label = tk.Label(
            page_cluster,
            text=self._t("pagination_of_word"),
            font=('Arial', 12),
            fg=F1Theme.TEXT_SECONDARY,
            bg=F1Theme.SURFACE,
        )
        self._pagination_of_label.pack(side=tk.LEFT, padx=(8, 4))
        
        self._pagination_total_label = tk.Label(
            page_cluster,
            text="1",
            font=('Arial', 12, 'bold'),
            fg=F1Theme.TEXT_PRIMARY,
            bg=F1Theme.SURFACE,
        )
        self._pagination_total_label.pack(side=tk.LEFT)
        
        self._pagination_next_arrow = tk.Label(
            right_cluster,
            text="→",
            font=('Arial', 16, 'bold'),
            bg=F1Theme.SURFACE,
            fg=F1Theme.TEXT_PRIMARY,
            padx=6,
            pady=2,
            cursor='hand2',
        )
        self._pagination_next_arrow.bind("<Button-1>", lambda e: self._on_next_page())
    
    def _update_pagination_controls(self):
        """Update pagination arrows, page entry, and total count."""
        # Calculate total pages
        events = self._get_filtered_events()
        total_events = len(events)
        self._total_pages = max(1, (total_events + self.EVENTS_PER_PAGE - 1) // self.EVENTS_PER_PAGE)
        
        # Ensure current page is valid
        if self._current_page > self._total_pages:
            self._current_page = self._total_pages
        if self._current_page < 1:
            self._current_page = 1
        
        # Show ← / → only when navigation is possible (otherwise omit the widget).
        if self._current_page > 1:
            if not self._pagination_prev_packed:
                self._pagination_prev_arrow.pack(
                    side=tk.LEFT,
                    padx=(0, 6),
                    before=self._pagination_page_cluster,
                )
                self._pagination_prev_packed = True
        else:
            if self._pagination_prev_packed:
                self._pagination_prev_arrow.pack_forget()
                self._pagination_prev_packed = False
        
        if self._current_page < self._total_pages:
            if not self._pagination_next_packed:
                self._pagination_next_arrow.pack(
                    side=tk.LEFT,
                    padx=(6, 0),
                    after=self._pagination_page_cluster,
                )
                self._pagination_next_packed = True
        else:
            if self._pagination_next_packed:
                self._pagination_next_arrow.pack_forget()
                self._pagination_next_packed = False
        
        self._pagination_syncing = True
        self._page_entry_var.set(str(self._current_page))
        self._pagination_total_label.configure(text=str(self._total_pages))
        self._pagination_syncing = False
    
    def _create_footer(self):
        """Create the application footer."""
        self._footer = tk.Frame(self, bg=F1Theme.SECONDARY_DARK, height=50)
        footer = self._footer
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(0, weight=1)
        
        self.champion_label = tk.Label(
            footer,
            text="",
            font=('Arial', 13),
            fg=F1Theme.TEXT_SECONDARY,
            bg=F1Theme.SECONDARY_DARK
        )
        self.champion_label.grid(row=0, column=0, pady=12)
    
    def _load_data(self):
        """Load and display the current season data."""
        self._update_stats()
        self._update_champion_info()
        self._display_events()
    
    def _update_stats(self):
        """Season progress bar + line: GP made = completed + cancelled; totals exclude removed rounds."""
        stats = self.controller.get_season_stats()
        pct = float(stats["completion_percentage"])
        pct_color = self._header_progress_accent_color(pct)
        self._header_progress_pct_label.configure(text=f"{pct:.0f}%", fg=pct_color)
        self._draw_header_progress_bar(pct)
        summary = self._t("header_progress_summary").format(
            pct=f"{pct:.0f}",
            done=stats["rounds_counted_toward_progress"],
            total=stats["total_events"],
            completed=stats["completed"],
            upcoming=stats["upcoming"],
            cancelled=stats["cancelled"],
        )
        self._header_progress_summary.configure(text=summary)
    
    def _update_champion_info(self):
        """Update the champion information in footer."""
        stats = self.controller.get_season_stats()
        
        if stats['champion'] and stats['constructor_champion']:
            champion_text = (
                "🏆 "
                + self._t("footer_champion_both").format(
                    driver=stats["champion"],
                    constructor=stats["constructor_champion"],
                )
            )
        elif stats['champion']:
            champion_text = "🏆 " + self._t("footer_champion_driver").format(driver=stats["champion"])
        else:
            champion_text = "🏁 " + self._t("footer_season_open")
        
        self.champion_label.configure(text=champion_text)
    
    def _display_events(self):
        """Display event cards in the container with pagination."""
        # Clear existing cards
        for widget in self.events_container.winfo_children():
            widget.destroy()
        
        all_events = self._get_filtered_events()
        self._update_pagination_controls()
        
        if not all_events:
            self._show_no_results()
            return
        
        start_idx = (self._current_page - 1) * self.EVENTS_PER_PAGE
        end_idx = start_idx + self.EVENTS_PER_PAGE
        page_events = all_events[start_idx:end_idx]
        
        for i, event in enumerate(page_events):
            row = i // 3
            col = i % 3
            
            card = EventCard(
                self.events_container,
                event,
                translate=self._t,
                import_selected=event.id in self._import_selected_ids,
                on_import_toggle=self._on_import_toggle,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
    
    def _get_filtered_events(self) -> List[Event]:
        """Get events based on current status filter."""
        if self._current_filter == "all":
            return self.controller.get_events_for_current_season()
        return self.controller.filter_events_by_status(self._current_filter)
    
    def _show_no_results(self):
        """Show no results message."""
        no_results_frame = tk.Frame(self.events_container, bg=F1Theme.SURFACE)
        no_results_frame.grid(row=0, column=0, columnspan=3, padx=8, pady=40, sticky="ew")
        
        no_results_label = tk.Label(
            no_results_frame,
            text=f"🏁 {self._t('no_results')}",
            font=('Arial', 16),
            fg=F1Theme.TEXT_MUTED,
            bg=F1Theme.SURFACE
        )
        no_results_label.pack(pady=40)
    
    def _refresh_language_ui(self) -> None:
        """Update all visible strings after a language change."""
        self.title(f"🏎️ {self._t('window_title')}")
        self._calendar_title_label.configure(text=self._t("calendar_title"))
        self._season_header_label.configure(text=self._t("season_label"))
        self.lang_var.set(language_option_display(self._lang))
        self._filter_header_label.configure(text=self._t("filter_label"))
        for value, btn in self.filter_buttons.items():
            btn.set_text(f"{FILTER_ICONS[value]}  {self._t(f'filter_{value}')}")
        self._pagination_page_label.configure(text=self._t("pagination_page_word"))
        self._pagination_of_label.configure(text=self._t("pagination_of_word"))
        self._import_btn.set_text(f"{IMPORT_ACTION_ICON}  {self._t('import_action')}")
        self._import_calendar_title_label.configure(text=self._t("calendar_title"))
        self._import_selected_heading_label.configure(text=self._import_selected_heading_text())
        self._update_import_bar()
        if self._import_view_active:
            self._refresh_import_screen_list()
        self._update_stats()
        self._update_champion_info()
        self._display_events()
    
    def _on_filter_changed(self, filter_value: str):
        """Handle filter button click."""
        self._current_filter = filter_value
        self._current_page = 1
        
        for value, btn in self.filter_buttons.items():
            btn.set_active(value == filter_value)
        
        self._display_events()
    
    def _on_prev_page(self):
        """Handle previous page button click."""
        if self._current_page > 1:
            self._current_page -= 1
            self._display_events()
    
    def _on_next_page(self):
        """Handle next page button click."""
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._display_events()
    
    def _release_page_entry_focus(self) -> None:
        """Move focus off the page entry so the insertion caret does not stay visible."""
        try:
            self._page_entry.selection_clear()
        except tk.TclError:
            pass
        self.focus_set()
    
    def _apply_page_from_entry(self) -> None:
        """Parse entry: clamp 1..max; invalid/NaN → max; empty → restore current."""
        if self._pagination_syncing:
            return
        total = max(1, self._total_pages)
        raw = self._page_entry_var.get().strip()
        if raw == "":
            self._pagination_syncing = True
            self._page_entry_var.set(str(self._current_page))
            self._pagination_syncing = False
            return
        try:
            v = int(raw)
        except ValueError:
            v = total
        v = max(1, min(v, total))
        self._pagination_syncing = True
        self._page_entry_var.set(str(v))
        self._pagination_syncing = False
        if v != self._current_page:
            self._current_page = v
            self._display_events()
    
    def _on_page_entry_return(self, event=None):
        """Commit page on Enter, then drop focus so the caret vanishes."""
        self._apply_page_from_entry()
        self.after_idle(self._release_page_entry_focus)
        return "break"
    
    def _on_page_entry_focusout(self, event=None):
        """Commit on blur without stealing focus (user may have moved to another control)."""
        self._apply_page_from_entry()
    
    def _on_import_toggle(self, event: Event, selected: bool) -> None:
        """Toggle an event id in the import selection set."""
        if selected:
            self._import_selected_ids.add(event.id)
        else:
            self._import_selected_ids.discard(event.id)
        self._update_import_bar()
    
    def _update_import_bar(self) -> None:
        """Refresh the import count label and Import button state."""
        n = len(self._import_selected_ids)
        self._import_count_label.configure(text=self._t("import_selection_count").format(count=n))
        if self._import_view_active:
            self._import_btn.set_active(False)
        else:
            self._import_btn.set_active(n > 0)
    
    def _set_import_screen_visible(self, visible: bool) -> None:
        """Toggle full-window import screen: hide header/toolbar/import bar/footer; show list view."""
        if visible:
            self._header.grid_remove()
            self._footer.grid_remove()
            self._toolbar.grid_remove()
            self._import_bar.grid_remove()
            self._calendar_panel.grid_remove()
            self._import_panel.grid(row=0, column=0, sticky="nsew")
            self._refresh_import_screen_list()
        else:
            self._import_panel.grid_remove()
            self._calendar_panel.grid(row=0, column=0, sticky="nsew")
            self._header.grid(row=0, column=0, sticky="ew")
            self._footer.grid(row=2, column=0, sticky="ew")
            self._toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 16))
            self._import_bar.grid(row=1, column=0, sticky="ew", pady=(0, 12))
    
    def _refresh_import_screen_list(self) -> None:
        """Heading + two-column list (left); titles without trailing 'Grand Prix'."""
        self._import_selected_heading_label.configure(text=self._import_selected_heading_text())
        for w in self._import_list_container.winfo_children():
            w.destroy()
        events = self.controller.get_events_for_current_season()
        by_id = {e.id: e for e in events}
        ordered = sorted(
            (by_id[i] for i in self._import_selected_ids if i in by_id),
            key=lambda e: e.round_number,
        )
        # Two tight columns: pack() keeps them adjacent. Grid+weight=1 was stretching each to half the window.
        left_col = tk.Frame(self._import_list_container, bg=F1Theme.SECONDARY)
        left_col.pack(side=tk.LEFT, anchor="nw")
        right_col = tk.Frame(self._import_list_container, bg=F1Theme.SECONDARY)
        right_col.pack(side=tk.LEFT, anchor="nw", padx=(240, 0))
        for i, ev in enumerate(ordered):
            short_name = _event_name_without_grand_prix(ev.name)
            parent = left_col if i % 2 == 0 else right_col
            tk.Label(
                parent,
                text=f"{ev.flag_emoji}  {short_name}",
                font=('Arial', 14),
                fg=F1Theme.TEXT_PRIMARY,
                bg=F1Theme.SECONDARY,
                anchor="w",
                justify="left",
                wraplength=320,
            ).pack(anchor="w", pady=(0, 14), ipady=0)
    
    def _on_import_go(self) -> None:
        """Show import screen in the same window (no extra panels)."""
        if not self._import_selected_ids:
            return
        self._import_view_active = True
        self._set_import_screen_visible(True)
        self._update_import_bar()
    
    def _on_import_back(self) -> None:
        """Return to the calendar; keep import selection."""
        self._import_view_active = False
        self._set_import_screen_visible(False)
        self._update_import_bar()
        self._display_events()
    
    def _on_data_changed(self):
        """Handle data change notification from controller."""
        self.year_var.set(str(self.controller.current_year))
        self._rebuild_year_menu()
        self._current_page = 1
        self._import_selected_ids.clear()
        if self._import_view_active:
            self._import_view_active = False
            self._set_import_screen_visible(False)
        self._update_import_bar()
        self._load_data()
