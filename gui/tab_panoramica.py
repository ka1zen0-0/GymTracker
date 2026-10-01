"""Scheda: panoramica di tutti gli esercizi (filtrabile per giorno), con PR e stalli."""
import tkinter as tk
from tkinter import ttk

from core import logic

from .common import ALL_DAYS, day_filter, fmt_delta, make_tree


class TabPanoramica(ttk.Frame):
    title = "Panoramica"

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 8))
        self.day = tk.StringVar(value=ALL_DAYS)
        ttk.Label(top, text="Giorno").pack(side="left")
        cb = ttk.Combobox(top, textvariable=self.day, values=[ALL_DAYS] + logic.DAYS, state="readonly", width=14)
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.tree = make_tree(self, [("name", "Esercizio", 210, "w"), ("n", "Sessioni", 70, "center"),
                                     ("last", "Ultimo", 90, "center"), ("delta", "Δ", 70, "e"),
                                     ("r1", "Record 1", 90, "center"), ("r2", "Record 2", 100, "e"),
                                     ("state", "Stato", 80, "center")], height=20)
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("stall", foreground="#c62828")
        legend = ("Forza: ultimo = top set, Δ = variazione e1RM, record = peso max / best e1RM.\n"
                  "Cardio: ultimo = km totali, Δ = variazione km, record = distanza max / miglior passo.\n"
                  f"Stallo = nessun miglioramento nelle ultime {logic.STALL_SESSIONS} sessioni.")
        ttk.Label(self, text=legend, foreground="#666", justify="left").pack(anchor="w", pady=(8, 0))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for r in logic.overview_rows(self.app.data, day_filter(self.day)):
            self.tree.insert("", "end", tags=("stall",) if r["stall"] else (),
                             values=(r["name"] + (" 🏃" if r["cardio"] else ""), r["n"], r["last"], fmt_delta(r["delta"]),
                                     r["r1"], r["r2"], "STALLO" if r["stall"] else ("ok" if r["n"] else "-")))
