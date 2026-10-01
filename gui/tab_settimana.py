"""Scheda: piano settimanale (quali esercizi in quale giorno)."""
import tkinter as tk
from datetime import date
from tkinter import ttk

from core import logic

from .common import exercise_names, sync_combobox


class TabSettimana(ttk.Frame):
    title = "Settimana"

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.sel = date.today().weekday()
        left = ttk.Frame(self)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Giorni").pack(anchor="w")
        self.days = tk.Listbox(left, height=7, width=16, exportselection=False)
        self.days.pack(fill="y")
        for d in logic.DAYS:
            self.days.insert("end", d)
        self.days.bind("<<ListboxSelect>>", self.on_select)

        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))
        self.header = ttk.Label(right, font=("TkDefaultFont", 11, "bold"))
        self.header.pack(anchor="w")
        self.lst = tk.Listbox(right, exportselection=False)
        self.lst.pack(fill="both", expand=True, pady=8)
        row = ttk.Frame(right)
        row.pack(fill="x")
        self.ex = tk.StringVar()
        self.cb = ttk.Combobox(row, textvariable=self.ex, state="readonly", width=30)
        self.cb.pack(side="left")
        ttk.Button(row, text="Aggiungi al giorno", command=self.add).pack(side="left", padx=6)
        ttk.Button(right, text="Rimuovi selezionato", command=self.remove).pack(anchor="w", pady=(8, 0))

    def on_select(self, _=None):
        s = self.days.curselection()
        if s:
            self.sel = s[0]
            self.render()

    def render(self):
        data = self.app.data
        self.days.selection_clear(0, "end")
        self.days.selection_set(self.sel)
        self.header.config(text=f"Esercizi di {logic.DAYS[self.sel]}")
        self.lst.delete(0, "end")
        for n in logic.plan_get(data, self.sel):
            self.lst.insert("end", n + (" (cardio)" if logic.is_cardio(data, n) else ""))

    def add(self):
        if self.ex.get():
            logic.plan_add(self.app.data, self.sel, self.ex.get())
            self.app.changed()

    def remove(self):
        s = self.lst.curselection()
        if s:
            logic.plan_remove(self.app.data, self.sel, logic.plan_get(self.app.data, self.sel)[s[0]])
            self.app.changed()

    def refresh(self):
        sync_combobox(self.cb, self.ex, exercise_names(self.app.data))
        self.render()
