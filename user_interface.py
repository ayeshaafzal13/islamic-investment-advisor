"""
USER INTERFACE FOR INVESTMENT ADVISOR EXPERT SYSTEM
Beautiful Tkinter GUI - Dark Islamic Finance Theme
"""
import colorsys
import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time

from knowledge_base import INVESTMENT_DATABASE, BEGINNER_PROFILE_QUESTIONS
from inference_engine import InvestmentInferenceEngine


# ─── THEME COLORS ───────────────────────────────────────────────────────────

COLORS = {
    "bg_dark":       "#0A0E14",
    "bg_card":       "#13191F",
    "bg_card2":      "#1A2232",
    "accent_gold":   "#F0C040",
    "accent_green":  "#3CC468",
    "accent_red":    "#F05050",
    "accent_yellow": "#F5C842",
    "accent_blue":   "#5B9CF6",
    "text_primary":  "#FFFFFF",
    "text_secondary":"#BDC8D8",
    "text_muted":    "#637080",
    "border":        "#252D3A",
    "border_gold":   "#F0C040",
    "halal_green":   "#1A6B38",
    "haram_red":     "#8B1A1A",
    "conditional":   "#7A4C10",
    "hover":         "#1E2A38",
}

FONTS = {
    "title":    ("Segoe UI", 24, "bold"),
    "heading":  ("Segoe UI", 15, "bold"),
    "subhead":  ("Segoe UI", 12, "bold"),
    "body":     ("Segoe UI", 11),
    "body_b":   ("Segoe UI", 11, "bold"),
    "small":    ("Segoe UI", 10),
    "badge":    ("Segoe UI", 9, "bold"),
    "large":    ("Segoe UI", 13),
    "score":    ("Segoe UI", 28, "bold"),
}


# ─── CUSTOM WIDGETS ──────────────────────────────────────────────────────────

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg=None, fg=None,
                 width=180, height=40, radius=8, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg or COLORS["accent_gold"]
        self.fg_color = fg or COLORS["bg_dark"]
        self.text = text
        self.width = width
        self.height = height
        self.radius = radius
        self._draw()
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, color=None):
        self.delete("all")
        c = color or self.bg_color
        r = self.radius
        w, h = self.width, self.height
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=c, outline=c)
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=c, outline=c)
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=c, outline=c)
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=c, outline=c)
        self.create_rectangle(r, 0, w-r, h, fill=c, outline=c)
        self.create_rectangle(0, r, w, h-r, fill=c, outline=c)
        self.create_text(w//2, h//2, text=self.text, fill=self.fg_color,
                         font=FONTS["body_b"])

    def _on_click(self, e):
        if self.command:
            self.command()

    def _on_enter(self, e):
        import colorsys
        self._draw(self._lighten(self.bg_color))

    def _on_leave(self, e):
        self._draw()

    def _lighten(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        v = min(1.0, v + 0.15)
        r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
        return "#{:02x}{:02x}{:02x}".format(int(r2*255), int(g2*255), int(b2*255))


class StatusBadge(tk.Label):
    STATUS_STYLES = {
        "HALAL":       (COLORS["halal_green"],  COLORS["text_primary"], "● HALAL"),
        "HARAM":       (COLORS["haram_red"],    COLORS["text_primary"], "● HARAM"),
        "CONDITIONAL": (COLORS["conditional"],  COLORS["text_primary"], "◆ CONDITIONAL"),
        "UNKNOWN":     (COLORS["text_muted"],   COLORS["text_primary"], "? UNKNOWN"),
    }

    def __init__(self, parent, status, **kwargs):
        bg, fg, label = self.STATUS_STYLES.get(status, self.STATUS_STYLES["UNKNOWN"])
        super().__init__(parent, text=label, bg=bg, fg=fg,
                         font=FONTS["badge"], padx=8, pady=3, **kwargs)


class Card(tk.Frame):
    def __init__(self, parent, title=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1, **kwargs)
        if title:
            header = tk.Frame(self, bg=COLORS["bg_card2"],
                              highlightbackground=COLORS["border"],
                              highlightthickness=0)
            header.pack(fill="x")
            tk.Label(header, text=title, bg=COLORS["bg_card2"],
                     fg=COLORS["accent_gold"], font=FONTS["subhead"],
                     padx=14, pady=8).pack(anchor="w")
            tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")


class ProgressBar(tk.Canvas):
    def __init__(self, parent, width=400, height=12, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS["bg_card2"], highlightthickness=0, **kwargs)
        self._width = width
        self._height = height
        self._draw(0)

    def set_value(self, pct):
        self._draw(max(0, min(100, pct)))

    def _draw(self, pct):
        self.delete("all")
        self.create_rectangle(0, 0, self._width, self._height,
                              fill=COLORS["bg_dark"], outline="")
        if pct > 0:
            color = (COLORS["accent_green"] if pct >= 60
                     else COLORS["accent_yellow"] if pct >= 30
                     else COLORS["accent_red"])
            self.create_rectangle(0, 0, int(self._width * pct / 100),
                                  self._height, fill=color, outline="")


# ─── MAIN APPLICATION ────────────────────────────────────────────────────────

class InvestmentUI:
    def __init__(self):
        self.engine = InvestmentInferenceEngine()
        self.profile_score = 0
        self.question_answers = []
        self.current_question = 0
        self.selected_investment = None

        self.root = tk.Tk()
        self.root.title("💼 Islamic Investment Advisor — Expert System")
        self.root.geometry("1050x720")
        self.root.minsize(900, 650)
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)

        # ttk style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=COLORS["bg_card2"],
                         background=COLORS["bg_card2"],
                         foreground=COLORS["text_primary"],
                         selectbackground=COLORS["accent_gold"],
                         bordercolor=COLORS["border"])

        self._build_layout()
        self._show_page("welcome")

    # ── LAYOUT ──────────────────────────────────────────────────────────────

    def _build_layout(self):
        # Top bar
        topbar = tk.Frame(self.root, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["border"],
                          highlightthickness=1, height=58)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        left_bar = tk.Frame(topbar, bg=COLORS["bg_card"])
        left_bar.pack(side="left", padx=18, pady=8)

        tk.Label(left_bar, text="☪", bg=COLORS["bg_card"],
                 fg=COLORS["accent_gold"], font=("Segoe UI", 18)).pack(side="left", padx=(0, 8))
        tk.Label(left_bar, text="Islamic Investment Advisor",
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                 font=FONTS["heading"]).pack(side="left")
        tk.Label(left_bar, text="  Expert System v2.0",
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                 font=FONTS["small"]).pack(side="left")

        # Nav buttons
        self.nav_frame = tk.Frame(topbar, bg=COLORS["bg_card"])
        self.nav_frame.pack(side="right", padx=18)

        self.nav_buttons = {}
        nav_items = [
            ("🏠 Home",    "welcome"),
            ("📚 Guide",   "guide"),
            ("👤 Profile", "profile"),
            ("📊 Analyze", "analyze"),
            ("🔍 Compare", "compare"),
        ]
        for label, page in nav_items:
            btn = tk.Button(self.nav_frame, text=label,
                            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                            font=FONTS["small"], relief="flat", bd=0,
                            padx=10, pady=6,
                            activebackground=COLORS["hover"],
                            activeforeground=COLORS["text_primary"],
                            cursor="hand2",
                            command=lambda p=page: self._show_page(p))
            btn.pack(side="left")
            self.nav_buttons[page] = btn

        # Content area
        self.content = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.content.pack(fill="both", expand=True)

        # Status bar
        self.statusbar = tk.Frame(self.root, bg=COLORS["bg_card"],
                                  height=28,
                                  highlightbackground=COLORS["border"],
                                  highlightthickness=1)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)
        self.status_label = tk.Label(self.statusbar,
                                      text="  Ready — Complete your profile to get started",
                                      bg=COLORS["bg_card"],
                                      fg=COLORS["text_muted"], font=FONTS["small"])
        self.status_label.pack(side="left")

        self.profile_status = tk.Label(self.statusbar, text="Profile: Not Set",
                                        bg=COLORS["bg_card"],
                                        fg=COLORS["text_muted"], font=FONTS["small"])
        self.profile_status.pack(side="right", padx=12)

    def _set_status(self, msg):
        self.status_label.config(text=f"  {msg}")

    def _update_nav(self, active_page):
        for page, btn in self.nav_buttons.items():
            if page == active_page:
                btn.config(fg=COLORS["accent_gold"],
                           bg=COLORS["hover"])
            else:
                btn.config(fg=COLORS["text_secondary"],
                           bg=COLORS["bg_card"])

    def _show_page(self, page):
        for w in self.content.winfo_children():
            w.destroy()
        self._update_nav(page)
        pages = {
            "welcome": self._page_welcome,
            "guide":   self._page_guide,
            "profile": self._page_profile,
            "analyze": self._page_analyze,
            "compare": self._page_compare,
        }
        pages.get(page, self._page_welcome)()

    # ── PAGE: WELCOME ────────────────────────────────────────────────────────

    def _page_welcome(self):
        self._set_status("Welcome — Select a section from the navigation above")
        outer = tk.Frame(self.content, bg=COLORS["bg_dark"])
        outer.pack(fill="both", expand=True, padx=40, pady=30)

        # Hero
        hero = tk.Frame(outer, bg=COLORS["bg_dark"])
        hero.pack(fill="x", pady=(0, 30))

        tk.Label(hero, text="☪", bg=COLORS["bg_dark"],
                 fg=COLORS["accent_gold"], font=("Segoe UI", 48)).pack()
        tk.Label(hero, text="Islamic Investment Advisor",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=("Segoe UI", 26, "bold")).pack()
        tk.Label(hero, text="Find Halal investments tailored to your beginner profile",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=("Segoe UI", 13)).pack(pady=(4, 0))

        # Divider
        tk.Frame(outer, bg=COLORS["accent_gold"], height=2).pack(fill="x", pady=20)

        # Feature cards row
        cards_row = tk.Frame(outer, bg=COLORS["bg_dark"])
        cards_row.pack(fill="x")

        features = [
            ("🕌", "Halal Screening",    "Every investment is checked\nagainst Islamic finance rules",  COLORS["accent_gold"]),
            ("👶", "Beginner Focus",     "Complexity & capital requirements\nmatched to your level",     COLORS["accent_green"]),
            ("📊", "Risk Analysis",      "Risk, return and time horizon\nprofiled for each option",      COLORS["accent_blue"]),
            ("⚖️", "Compare & Rank",     "Side-by-side comparison of\nmultiple investments",            COLORS["accent_yellow"]),
        ]
        for icon, title, desc, accent in features:
            card = tk.Frame(cards_row, bg=COLORS["bg_card2"],
                            highlightbackground=accent,
                            highlightthickness=2)
            card.pack(side="left", expand=True, fill="both", padx=6, pady=6, ipady=18, ipadx=12)
            tk.Label(card, text=icon, bg=COLORS["bg_card2"],
                     fg=accent, font=("Segoe UI", 28)).pack(pady=(14, 6))
            tk.Label(card, text=title, bg=COLORS["bg_card2"],
                     fg=accent, font=FONTS["subhead"]).pack()
            tk.Frame(card, bg=accent, height=1).pack(fill="x", padx=20, pady=(6, 0))
            tk.Label(card, text=desc, bg=COLORS["bg_card2"],
                     fg=COLORS["text_primary"], font=FONTS["small"],
                     justify="center").pack(pady=(6, 14))

        # CTA
        cta = tk.Frame(outer, bg=COLORS["bg_dark"])
        cta.pack(pady=28)

        if self.profile_score == 0:
            tk.Label(cta, text="Start by building your investor profile →",
                     bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                     font=FONTS["body"]).pack(pady=(0, 10))
            RoundedButton(cta, "Build My Profile",
                          command=lambda: self._show_page("profile"),
                          bg=COLORS["accent_gold"], fg=COLORS["bg_dark"],
                          width=200, height=42).pack()
        else:
            tk.Label(cta, text=f"✓ Profile complete — Score: {self.profile_score:.0f}/100",
                     bg=COLORS["bg_dark"], fg=COLORS["accent_green"],
                     font=FONTS["body_b"]).pack(pady=(0, 10))
            RoundedButton(cta, "Analyze Investments",
                          command=lambda: self._show_page("analyze"),
                          bg=COLORS["accent_green"], fg=COLORS["text_primary"],
                          width=220, height=42).pack()

        # Disclaimer
        disc = tk.Label(outer,
                        text="⚠️  DISCLAIMER: This is educational content, not professional financial advice. "
                             "Consult a certified advisor before investing.",
                        bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                        font=FONTS["small"], wraplength=700, justify="center")
        disc.pack(pady=(10, 0))

    # ── PAGE: GUIDE ──────────────────────────────────────────────────────────

    def _page_guide(self):
        self._set_status("Islamic Finance Guide — Learn what makes an investment Halal or Haram")

        outer = tk.Frame(self.content, bg=COLORS["bg_dark"])
        outer.pack(fill="both", expand=True)

        # Scrollable
        canvas = tk.Canvas(outer, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = tk.Frame(canvas, bg=COLORS["bg_dark"])
        window = canvas.create_window((0, 0), window=frame, anchor="nw")

        def _resize(e):
            canvas.itemconfig(window, width=e.width)
        canvas.bind("<Configure>", _resize)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        inner = tk.Frame(frame, bg=COLORS["bg_dark"], padx=40, pady=20)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="📚 Islamic Finance Guide",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["title"]).pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Understanding Halal & Haram in investing",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["body"]).pack(anchor="w", pady=(0, 20))
        tk.Frame(inner, bg=COLORS["accent_gold"], height=2).pack(fill="x", pady=(0, 24))

        # Two columns
        cols = tk.Frame(inner, bg=COLORS["bg_dark"])
        cols.pack(fill="x", pady=(0, 20))

        # HARAM column
        haram_card = Card(cols, title="🚫  HARAM — FORBIDDEN")
        haram_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        haram_items = [
            ("Riba (Interest)",     "Any product that earns or charges interest.\nExamples: Bank bonds, savings accounts, fixed-return deposits."),
            ("Gharar (Speculation)","Excessive uncertainty & pure gambling.\nExamples: Forex trading, options contracts, crypto (disputed)."),
            ("Haram Businesses",    "Companies operating in forbidden industries.\nExamples: Alcohol, pork, gambling, conventional banking."),
            ("Unclear Contracts",   "Deals without transparent or clearly defined terms."),
        ]
        for title, desc in haram_items:
            item = tk.Frame(haram_card, bg=COLORS["bg_card"], padx=12, pady=8)
            item.pack(fill="x", padx=10, pady=(6, 0))
            tk.Label(item, text=f"✗  {title}", bg=COLORS["bg_card"],
                     fg=COLORS["accent_red"], font=FONTS["body_b"]).pack(anchor="w")
            tk.Label(item, text=desc, bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"], font=FONTS["small"],
                     justify="left", wraplength=320).pack(anchor="w", padx=14)

        # HALAL column
        halal_card = Card(cols, title="✅  HALAL — PERMITTED")
        halal_card.pack(side="left", fill="both", expand=True, padx=(8, 0))

        halal_items = [
            ("Halal Stocks",        "Shares in companies with permissible business activities.\nScreened for haram revenue sources."),
            ("Real Estate",         "Physical property ownership & rental income.\nTangible asset, no interest involved."),
            ("Sukuk",               "Islamic bonds backed by real assets.\nProfit-sharing, no interest (Riba)."),
            ("Islamic Mutual Funds","Professionally managed, Shariah-screened portfolios.\nBest starting point for beginners."),
            ("Gold & Silver",       "Physical precious metals as a store of value.\nTangible, universally accepted assets."),
        ]
        for title, desc in halal_items:
            item = tk.Frame(halal_card, bg=COLORS["bg_card"], padx=12, pady=8)
            item.pack(fill="x", padx=10, pady=(6, 0))
            tk.Label(item, text=f"✓  {title}", bg=COLORS["bg_card"],
                     fg=COLORS["accent_green"], font=FONTS["body_b"]).pack(anchor="w")
            tk.Label(item, text=desc, bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"], font=FONTS["small"],
                     justify="left", wraplength=320).pack(anchor="w", padx=14)

        # Simple rule box
        rule_card = tk.Frame(inner, bg=COLORS["bg_card2"],
                             highlightbackground=COLORS["accent_gold"],
                             highlightthickness=1, padx=20, pady=16)
        rule_card.pack(fill="x", pady=20)
        tk.Label(rule_card, text="💡  The Golden Rule of Islamic Finance",
                 bg=COLORS["bg_card2"], fg=COLORS["accent_gold"],
                 font=FONTS["subhead"]).pack(anchor="w")
        tk.Label(rule_card,
                 text="HALAL = Real business activity  ·  Profit & risk sharing  ·  No interest  ·  Asset-backed\n"
                      "HARAM = Interest (Riba)  ·  Excessive speculation  ·  Forbidden industries  ·  Unclear contracts",
                 bg=COLORS["bg_card2"], fg=COLORS["text_primary"],
                 font=FONTS["body"], justify="left").pack(anchor="w", pady=(6, 0))

        # Four pillars
        tk.Label(inner, text="The Four Pillars of Islamic Finance",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["heading"]).pack(anchor="w", pady=(10, 12))

        pillars = [
            ("1", "No Riba",        COLORS["accent_red"],    "Zero interest in any form"),
            ("2", "No Gharar",      COLORS["accent_yellow"], "No excessive uncertainty or speculation"),
            ("3", "Halal Business", COLORS["accent_green"],  "Company must operate in permitted industries"),
            ("4", "Asset-Backed",   COLORS["accent_blue"],   "Investment must represent a real, tangible asset"),
        ]
        pillars_row = tk.Frame(inner, bg=COLORS["bg_dark"])
        pillars_row.pack(fill="x", pady=(0, 20))

        for num, title, color, desc in pillars:
            p = tk.Frame(pillars_row, bg=COLORS["bg_card"],
                         highlightbackground=color, highlightthickness=2)
            p.pack(side="left", expand=True, fill="both", padx=5, ipadx=10, ipady=10)
            tk.Label(p, text=num, bg=COLORS["bg_card"], fg=color,
                     font=("Segoe UI", 20, "bold")).pack()
            tk.Label(p, text=title, bg=COLORS["bg_card"], fg=color,
                     font=FONTS["subhead"]).pack()
            tk.Label(p, text=desc, bg=COLORS["bg_card"],
                     fg=COLORS["text_secondary"], font=FONTS["small"],
                     wraplength=180, justify="center").pack(pady=(4, 0))

    # ── PAGE: PROFILE ────────────────────────────────────────────────────────

    def _page_profile(self):
        self._set_status("Investor Profile — Answer 5 questions to build your profile")

        self.question_answers = []
        self.current_question = 0

        outer = tk.Frame(self.content, bg=COLORS["bg_dark"])
        outer.pack(fill="both", expand=True, padx=60, pady=30)

        tk.Label(outer, text="👤  Build Your Investor Profile",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["title"]).pack(anchor="w")
        tk.Label(outer, text="5 quick questions to match you with the right investments",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["body"]).pack(anchor="w", pady=(2, 16))
        tk.Frame(outer, bg=COLORS["accent_gold"], height=2).pack(fill="x", pady=(0, 20))

        # Progress row
        prog_row = tk.Frame(outer, bg=COLORS["bg_dark"])
        prog_row.pack(fill="x", pady=(0, 20))
        self.prog_label = tk.Label(prog_row, text="Question 1 of 5",
                                   bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                                   font=FONTS["small"])
        self.prog_label.pack(anchor="w")
        self.prog_bar = ProgressBar(prog_row, width=600, height=8)
        self.prog_bar.pack(anchor="w", pady=(4, 0))

        # Question card
        self.q_card = Card(outer)
        self.q_card.pack(fill="x", pady=(0, 16))

        self.q_inner = tk.Frame(self.q_card, bg=COLORS["bg_card"], padx=20, pady=16)
        self.q_inner.pack(fill="both")

        self.q_label = tk.Label(self.q_inner, text="",
                                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                font=FONTS["heading"], wraplength=700, justify="left")
        self.q_label.pack(anchor="w", pady=(0, 16))

        self.radio_var = tk.IntVar(value=-1)
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.q_inner, variable=self.radio_var, value=i,
                                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                                font=FONTS["body"],
                                selectcolor=COLORS["bg_card2"],
                                activebackground=COLORS["bg_card"],
                                activeforeground=COLORS["accent_gold"],
                                cursor="hand2")
            rb.pack(anchor="w", padx=10, pady=3)
            self.radio_buttons.append(rb)

        # Buttons
        btn_row = tk.Frame(outer, bg=COLORS["bg_dark"])
        btn_row.pack(anchor="w")

        self.btn_next = RoundedButton(btn_row, "Next →",
                                      command=self._profile_next,
                                      bg=COLORS["accent_gold"], fg=COLORS["bg_dark"],
                                      width=140, height=40)
        self.btn_next.pack(side="left", padx=(0, 10))

        # Score display (hidden until complete)
        self.score_frame = tk.Frame(outer, bg=COLORS["bg_dark"])
        self.score_display = tk.Label(self.score_frame, text="",
                                      bg=COLORS["bg_dark"], fg=COLORS["accent_gold"],
                                      font=FONTS["score"])

        self._load_question()

    def _load_question(self):
        idx = self.current_question
        q = BEGINNER_PROFILE_QUESTIONS[idx]
        self.prog_label.config(text=f"Question {idx+1} of {len(BEGINNER_PROFILE_QUESTIONS)}")
        self.prog_bar.set_value((idx / len(BEGINNER_PROFILE_QUESTIONS)) * 100)
        self.q_label.config(text=f"Q{idx+1}:  {q['question']}")
        self.radio_var.set(-1)
        for i, rb in enumerate(self.radio_buttons):
            rb.config(text=f"  {q['options'][i]}")

    def _profile_next(self):
        if self.radio_var.get() == -1:
            messagebox.showwarning("Selection Required",
                                   "Please select an option before continuing.")
            return

        q = BEGINNER_PROFILE_QUESTIONS[self.current_question]
        score = q["scores"][self.radio_var.get()]
        self.question_answers.append(score)
        self.current_question += 1

        if self.current_question < len(BEGINNER_PROFILE_QUESTIONS):
            self._load_question()
        else:
            # Done
            self.profile_score = sum(self.question_answers) / len(self.question_answers)
            self.prog_bar.set_value(100)
            self.prog_label.config(text="Profile Complete ✓")
            self.q_label.config(text="")
            for rb in self.radio_buttons:
                rb.pack_forget()
            self.btn_next.pack_forget()

            # Show score in card
            for w in self.q_inner.winfo_children():
                w.destroy()

            tk.Label(self.q_inner, text="Profile Complete!",
                     bg=COLORS["bg_card"], fg=COLORS["accent_gold"],
                     font=FONTS["heading"]).pack(pady=(10, 4))

            score_val = self.profile_score
            color = (COLORS["accent_green"] if score_val >= 60
                     else COLORS["accent_yellow"] if score_val >= 30
                     else COLORS["accent_red"])

            tk.Label(self.q_inner, text=f"{score_val:.0f}",
                     bg=COLORS["bg_card"], fg=color,
                     font=("Segoe UI", 48, "bold")).pack()
            tk.Label(self.q_inner, text="out of 100",
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                     font=FONTS["body"]).pack()

            if score_val >= 80:
                level = "Advanced Investor Profile"
            elif score_val >= 60:
                level = "Intermediate Investor Profile"
            else:
                level = "Conservative / Beginning Investor Profile"

            tk.Label(self.q_inner, text=level,
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     font=FONTS["body_b"]).pack(pady=(6, 10))

            pb = ProgressBar(self.q_inner, width=500, height=14)
            pb.pack(pady=(0, 14))
            pb.set_value(score_val)

            RoundedButton(self.q_inner, "→ Analyze Investments",
                          command=lambda: self._show_page("analyze"),
                          bg=COLORS["accent_green"], fg=COLORS["text_primary"],
                          width=220, height=40).pack(pady=(0, 10))

            self.profile_status.config(
                text=f"Profile Score: {score_val:.0f}/100",
                fg=COLORS["accent_gold"])
            self._set_status(f"Profile complete — Score: {score_val:.0f}/100")

    # ── PAGE: ANALYZE ────────────────────────────────────────────────────────

    def _page_analyze(self):
        self._set_status("Investment Analyzer — Select an investment to get a full analysis")

        if self.profile_score == 0:
            self._no_profile_warning("analyze")
            return

        outer = tk.Frame(self.content, bg=COLORS["bg_dark"])
        outer.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(outer, text="📊  Investment Analyzer",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["title"]).pack(anchor="w")
        tk.Label(outer, text="Select an investment to see its Halal status and suitability for you",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["body"]).pack(anchor="w", pady=(2, 12))
        tk.Frame(outer, bg=COLORS["accent_gold"], height=2).pack(fill="x", pady=(0, 16))

        # Two-column layout
        cols = tk.Frame(outer, bg=COLORS["bg_dark"])
        cols.pack(fill="both", expand=True)

        # LEFT: Investment list
        left = tk.Frame(cols, bg=COLORS["bg_dark"], width=320)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="Choose Investment",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["small"]).pack(anchor="w", pady=(0, 6))

        list_canvas = tk.Canvas(left, bg=COLORS["bg_dark"], highlightthickness=0)
        list_scroll = tk.Scrollbar(left, orient="vertical", command=list_canvas.yview)
        list_canvas.configure(yscrollcommand=list_scroll.set)
        list_scroll.pack(side="right", fill="y")
        list_canvas.pack(fill="both", expand=True)

        list_frame = tk.Frame(list_canvas, bg=COLORS["bg_dark"])
        list_win = list_canvas.create_window((0, 0), window=list_frame, anchor="nw")
        list_canvas.bind("<Configure>", lambda e: list_canvas.itemconfig(list_win, width=e.width))
        list_frame.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))

        self.inv_buttons = {}
        self.selected_inv_key = tk.StringVar()

        halal_icon = {"HALAL": "✅", "HARAM": "❌", "CONDITIONAL": "⚠️"}
        halal_colors = {"HALAL": COLORS["accent_green"], "HARAM": COLORS["accent_red"],
                        "CONDITIONAL": COLORS["accent_yellow"]}

        for key, inv in INVESTMENT_DATABASE.items():
            status = inv["halal_status"]
            icon = halal_icon.get(status, "?")
            btn = tk.Button(list_frame,
                            text=f"{icon}  {inv['name']}",
                            bg=COLORS["bg_card"],
                            fg=halal_colors.get(status, COLORS["text_primary"]),
                            font=FONTS["small"], relief="flat", bd=0,
                            anchor="w", padx=12, pady=8,
                            activebackground=COLORS["hover"],
                            activeforeground=COLORS["text_primary"],
                            cursor="hand2",
                            highlightbackground=COLORS["border"],
                            highlightthickness=1,
                            wraplength=270, justify="left",
                            command=lambda k=key: self._analyze_investment(k))
            btn.pack(fill="x", pady=2)
            self.inv_buttons[key] = btn

        # RIGHT: Result panel
        self.result_panel = tk.Frame(cols, bg=COLORS["bg_dark"])
        self.result_panel.pack(side="left", fill="both", expand=True)

        self._show_analyze_placeholder()

    def _show_analyze_placeholder(self):
        for w in self.result_panel.winfo_children():
            w.destroy()
        holder = tk.Frame(self.result_panel, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["border"],
                          highlightthickness=1)
        holder.pack(fill="both", expand=True)
        tk.Label(holder, text="←  Select an investment\nfrom the list to analyze it",
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                 font=FONTS["large"], justify="center").pack(expand=True)

    def _analyze_investment(self, key):
        # Highlight selected
        for k, btn in self.inv_buttons.items():
            inv = INVESTMENT_DATABASE[k]
            status = inv["halal_status"]
            colors = {"HALAL": COLORS["accent_green"], "HARAM": COLORS["accent_red"],
                      "CONDITIONAL": COLORS["accent_yellow"]}
            btn.config(bg=COLORS["bg_card2"] if k == key else COLORS["bg_card"],
                       relief="flat")

        result = self.engine.analyze_investment(key, self.profile_score)
        self._display_result(result)
        self._set_status(f"Analyzed: {result['investment']}")

    def _display_result(self, result):
        for w in self.result_panel.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.result_panel, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.result_panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        frame = tk.Frame(canvas, bg=COLORS["bg_dark"], padx=4, pady=4)
        win = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Header row
        header = tk.Frame(frame, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text=result["investment"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["heading"]).pack(side="left")
        StatusBadge(header, result["halal_status"]).pack(side="left", padx=10)
        tk.Label(header, text=f"Beginner Suitable: {'✅ YES' if result['beginner_suitable'] else '❌ NO'}",
                 bg=COLORS["bg_dark"],
                 fg=COLORS["accent_green"] if result["beginner_suitable"] else COLORS["accent_red"],
                 font=FONTS["body_b"]).pack(side="left", padx=4)

        # Recommendation banner
        rec_colors = {
            "✅": COLORS["halal_green"],
            "❌": COLORS["haram_red"],
            "⚠️": COLORS["conditional"],
            "✓": "#1a3a2a",
        }
        first_char = result["recommendation"][0]
        rec_bg = rec_colors.get(first_char, COLORS["bg_card2"])
        rec_card = tk.Frame(frame, bg=rec_bg,
                            highlightbackground=COLORS["border"],
                            highlightthickness=1, padx=14, pady=12)
        rec_card.pack(fill="x", pady=(0, 12))
        tk.Label(rec_card, text=result["recommendation"],
                 bg=rec_bg, fg=COLORS["text_primary"],
                 font=FONTS["body_b"], wraplength=580, justify="left").pack(anchor="w")
        tk.Label(rec_card, text=f"Confidence: {result['confidence']*100:.0f}%",
                 bg=rec_bg, fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w", pady=(4, 0))

        # Stats row
        stats_row = tk.Frame(frame, bg=COLORS["bg_dark"])
        stats_row.pack(fill="x", pady=(0, 12))

        def stat_box(parent, label, value, color):
            box = tk.Frame(parent, bg=COLORS["bg_card"],
                           highlightbackground=color, highlightthickness=1)
            box.pack(side="left", expand=True, fill="x", padx=3, ipadx=10, ipady=8)
            tk.Label(box, text=label, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=FONTS["small"]).pack()
            tk.Label(box, text=value, bg=COLORS["bg_card"],
                     fg=color, font=FONTS["body_b"]).pack()

        risk_colors = {"VERY HIGH": COLORS["accent_red"], "HIGH": COLORS["accent_yellow"],
                       "MODERATE": COLORS["accent_blue"], "LOW": COLORS["accent_green"],
                       "VERY LOW": COLORS["accent_green"]}

        stat_box(stats_row, "Risk Level", result["risk_level"],
                 risk_colors.get(result["risk_level"], COLORS["text_primary"]))
        stat_box(stats_row, "Return Potential", result["return_level"],
                 risk_colors.get(result["return_level"], COLORS["text_primary"]))
        stat_box(stats_row, "Time Horizon", result["time_horizon"], COLORS["accent_blue"])
        stat_box(stats_row, "Confidence", f"{result['confidence']*100:.0f}%", COLORS["accent_gold"])

        # Confidence bar
        conf_row = tk.Frame(frame, bg=COLORS["bg_dark"])
        conf_row.pack(fill="x", pady=(0, 12))
        tk.Label(conf_row, text="Analysis Confidence",
                 bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
                 font=FONTS["small"]).pack(anchor="w")
        pb = ProgressBar(conf_row, width=600, height=10)
        pb.pack(anchor="w", pady=(4, 0))
        pb.set_value(result["confidence"] * 100)

        # Reasons & Warnings
        if result["reasons"]:
            r_card = Card(frame, title="✓  Positive Factors")
            r_card.pack(fill="x", pady=(0, 8))
            inner = tk.Frame(r_card, bg=COLORS["bg_card"], padx=14, pady=8)
            inner.pack(fill="x")
            for reason in result["reasons"]:
                tk.Label(inner, text=reason, bg=COLORS["bg_card"],
                         fg=COLORS["accent_green"], font=FONTS["body"],
                         justify="left", wraplength=580).pack(anchor="w", pady=2)

        if result["warnings"]:
            w_card = Card(frame, title="⚠️  Warnings")
            w_card.pack(fill="x", pady=(0, 8))
            inner = tk.Frame(w_card, bg=COLORS["bg_card"], padx=14, pady=8)
            inner.pack(fill="x")
            for warning in result["warnings"]:
                tk.Label(inner, text=warning, bg=COLORS["bg_card"],
                         fg=COLORS["accent_yellow"], font=FONTS["body"],
                         justify="left", wraplength=580).pack(anchor="w", pady=2)

    # ── PAGE: COMPARE ────────────────────────────────────────────────────────

    def _page_compare(self):
        self._set_status("Compare Investments — Select multiple investments to rank them")

        if self.profile_score == 0:
            self._no_profile_warning("compare")
            return

        outer = tk.Frame(self.content, bg=COLORS["bg_dark"])
        outer.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(outer, text="🔍  Investment Comparison",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["title"]).pack(anchor="w")
        tk.Label(outer, text="Select investments to compare side-by-side and get a ranked recommendation",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["body"]).pack(anchor="w", pady=(2, 12))
        tk.Frame(outer, bg=COLORS["accent_gold"], height=2).pack(fill="x", pady=(0, 16))

        # Checkboxes
        chk_label = tk.Label(outer, text="Select investments to compare:",
                             bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                             font=FONTS["small"])
        chk_label.pack(anchor="w", pady=(0, 8))

        chk_frame = tk.Frame(outer, bg=COLORS["bg_dark"])
        chk_frame.pack(fill="x", pady=(0, 12))

        self.chk_vars = {}
        halal_icon = {"HALAL": "✅", "HARAM": "❌", "CONDITIONAL": "⚠️"}
        cols_per_row = 3
        keys = list(INVESTMENT_DATABASE.keys())
        for i, key in enumerate(keys):
            inv = INVESTMENT_DATABASE[key]
            var = tk.BooleanVar()
            self.chk_vars[key] = var
            col = i % cols_per_row
            row = i // cols_per_row
            icon = halal_icon.get(inv["halal_status"], "?")
            cb = tk.Checkbutton(chk_frame,
                                text=f"{icon}  {inv['name']}",
                                variable=var,
                                bg=COLORS["bg_dark"],
                                fg=COLORS["text_primary"],
                                font=FONTS["small"],
                                selectcolor=COLORS["bg_card2"],
                                activebackground=COLORS["bg_dark"],
                                activeforeground=COLORS["accent_gold"],
                                cursor="hand2")
            cb.grid(row=row, column=col, sticky="w", padx=10, pady=3)

        RoundedButton(outer, "Compare Selected",
                      command=self._run_compare,
                      bg=COLORS["accent_gold"], fg=COLORS["bg_dark"],
                      width=200, height=40).pack(anchor="w", pady=(4, 14))

        # Results area
        self.compare_result_frame = tk.Frame(outer, bg=COLORS["bg_dark"])
        self.compare_result_frame.pack(fill="both", expand=True)

    def _run_compare(self):
        selected = [k for k, v in self.chk_vars.items() if v.get()]
        if len(selected) < 2:
            messagebox.showwarning("Select More", "Please select at least 2 investments to compare.")
            return

        results = self.engine.compare_investments(selected, self.profile_score)

        for w in self.compare_result_frame.winfo_children():
            w.destroy()

        tk.Label(self.compare_result_frame,
                 text=f"Ranking Results  ({len(results)} investments compared)",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["small"]).pack(anchor="w", pady=(0, 8))

        halal_colors = {"HALAL": COLORS["accent_green"],
                        "HARAM": COLORS["accent_red"],
                        "CONDITIONAL": COLORS["accent_yellow"]}
        rank_medal = {1: "🥇", 2: "🥈", 3: "🥉"}

        canvas = tk.Canvas(self.compare_result_frame, bg=COLORS["bg_dark"],
                           highlightthickness=0)
        scrollbar = tk.Scrollbar(self.compare_result_frame, orient="vertical",
                                 command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        frame = tk.Frame(canvas, bg=COLORS["bg_dark"])
        win = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for rank, result in enumerate(results, 1):
            medal = rank_medal.get(rank, f"#{rank}")
            status = result["halal_status"]
            color = halal_colors.get(status, COLORS["text_muted"])

            row_card = tk.Frame(frame, bg=COLORS["bg_card"],
                                highlightbackground=color if rank == 1 else COLORS["border"],
                                highlightthickness=2 if rank == 1 else 1)
            row_card.pack(fill="x", padx=4, pady=4, ipady=8)

            inner = tk.Frame(row_card, bg=COLORS["bg_card"])
            inner.pack(fill="x", padx=14)

            # Rank medal
            tk.Label(inner, text=medal, bg=COLORS["bg_card"],
                     font=("Segoe UI", 18)).pack(side="left", padx=(0, 8))

            # Name & badges
            info = tk.Frame(inner, bg=COLORS["bg_card"])
            info.pack(side="left", expand=True, fill="x")
            tk.Label(info, text=result["investment"], bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"], font=FONTS["body_b"]).pack(anchor="w")
            badge_row = tk.Frame(info, bg=COLORS["bg_card"])
            badge_row.pack(anchor="w", pady=(2, 0))
            StatusBadge(badge_row, status).pack(side="left", padx=(0, 6))
            suit = "✅ Beginner OK" if result["beginner_suitable"] else "❌ Not for Beginners"
            tk.Label(badge_row, text=suit, bg=COLORS["bg_card"],
                     fg=COLORS["accent_green"] if result["beginner_suitable"] else COLORS["accent_red"],
                     font=FONTS["badge"], padx=6, pady=3).pack(side="left")

            # Stats on right
            stats = tk.Frame(inner, bg=COLORS["bg_card"])
            stats.pack(side="right")
            tk.Label(stats, text=f"Risk: {result['risk_level']}",
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     font=FONTS["small"]).pack(anchor="e")
            tk.Label(stats, text=f"Return: {result['return_level']}",
                     bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                     font=FONTS["small"]).pack(anchor="e")
            tk.Label(stats, text=f"Confidence: {result['confidence']*100:.0f}%",
                     bg=COLORS["bg_card"], fg=COLORS["accent_gold"],
                     font=FONTS["small"]).pack(anchor="e")

            # Confidence bar
            pb = ProgressBar(frame, width=700, height=6)
            pb.pack(padx=18, anchor="w")
            pb.set_value(result["confidence"] * 100)

        self._set_status(f"Comparison complete — {len(results)} investments ranked")

    # ── HELPERS ──────────────────────────────────────────────────────────────

    def _no_profile_warning(self, redirect_page):
        frame = tk.Frame(self.content, bg=COLORS["bg_dark"])
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="⚠️", bg=COLORS["bg_dark"],
                 fg=COLORS["accent_yellow"], font=("Segoe UI", 40)).pack(pady=(80, 10))
        tk.Label(frame, text="Profile Required",
                 bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                 font=FONTS["heading"]).pack()
        tk.Label(frame, text="Please complete your investor profile first to unlock this feature.",
                 bg=COLORS["bg_dark"], fg=COLORS["text_secondary"],
                 font=FONTS["body"]).pack(pady=(4, 20))
        RoundedButton(frame, "Go to Profile",
                      command=lambda: self._show_page("profile"),
                      bg=COLORS["accent_gold"], fg=COLORS["bg_dark"],
                      width=180, height=40).pack()

    def run(self):
        self.root.mainloop()


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ui = InvestmentUI()
    ui.run()