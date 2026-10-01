"""Scheda: registrazione di un allenamento (forza o cardio) in un giorno della settimana."""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from core import logic

from .common import exercise_names, sync_combobox


class TabAllenamento(ttk.Frame):
    title = "Allenamento"

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.pending = []
        self.last_date = str(date.today())
        self.ex, self.date = tk.StringVar(), tk.StringVar(value=self.last_date)
        self.day = tk.StringVar(value=logic.DAYS[date.today().weekday()])
        self.show_all = tk.BooleanVar()

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Data (AAAA-MM-GG)").grid(row=0, column=0)
        de = ttk.Entry(top, textvariable=self.date, width=12)
        de.grid(row=0, column=1, padx=6)
        de.bind("<FocusOut>", self.date_to_day)
        ttk.Label(top, text="Giorno").grid(row=0, column=2, padx=(12, 4))
        day_cb = ttk.Combobox(top, textvariable=self.day, values=logic.DAYS, state="readonly", width=12)
        day_cb.grid(row=0, column=3)
        day_cb.bind("<<ComboboxSelected>>", lambda e: self.on_day_change())
        ttk.Label(top, text="Esercizio").grid(row=1, column=0, pady=8)
        self.cb = ttk.Combobox(top, textvariable=self.ex, state="readonly", width=32)
        self.cb.grid(row=1, column=1, columnspan=3, sticky="w", padx=6)
        self.cb.bind("<<ComboboxSelected>>", lambda e: self.on_exercise_change())
        ttk.Checkbutton(top, text="Mostra tutti gli esercizi", variable=self.show_all,
                        command=self.on_day_change).grid(row=1, column=4, padx=12)

        self.info = ttk.Label(self, wraplength=880, justify="left")
        self.info.pack(anchor="w", pady=12)

        row = ttk.Frame(self)
        row.pack(fill="x")
        self.lbl_a, self.lbl_b = ttk.Label(row, text="Peso (kg)"), ttk.Label(row, text="Reps")
        self.a, self.b = ttk.Entry(row, width=8), ttk.Entry(row, width=8)
        self.lbl_a.pack(side="left")
        self.a.pack(side="left", padx=6)
        self.lbl_b.pack(side="left")
        self.b.pack(side="left", padx=6)
        ttk.Button(row, text="Aggiungi", command=self.add_item).pack(side="left", padx=6)
        self.a.bind("<Return>", lambda e: self.b.focus())
        self.b.bind("<Return>", lambda e: self.add_item())

        self.listbox = tk.Listbox(self, height=8)
        self.listbox.pack(fill="both", expand=True, pady=10)
        btns = ttk.Frame(self)
        btns.pack(fill="x")
        ttk.Button(btns, text="Rimuovi ultimo inserimento", command=self.undo_item).pack(side="left")
        ttk.Button(btns, text="Salva allenamento", command=self.save).pack(side="right")
        self.result = ttk.Label(self, wraplength=880, justify="left", foreground="#1a7f37")
        self.result.pack(anchor="w", pady=(10, 0))

    # ---- helpers ----
    def day_idx(self):
        return logic.DAYS.index(self.day.get())

    def cardio(self):
        return logic.is_cardio(self.app.data, self.ex.get())

    def available(self):
        data = self.app.data
        if not self.show_all.get():
            planned = [n for n in logic.plan_get(data, self.day_idx()) if n in data["exercises"]]
            if planned:
                return planned
        return exercise_names(data)

    # ---- eventi ----
    def date_to_day(self, _=None):
        if self.date.get() == self.last_date:
            return
        self.last_date = self.date.get()
        try:
            self.day.set(logic.DAYS[logic.weekday(self.last_date)])
        except ValueError:
            return
        self.on_day_change()

    def on_day_change(self):
        old = self.ex.get()
        self.refresh()
        if self.ex.get() != old:
            self.on_exercise_change()

    def on_exercise_change(self):
        self.pending.clear()
        self.render_pending()
        self.result.config(text="")
        self.update_labels()
        self.update_info()

    def update_labels(self):
        c = self.cardio()
        self.lbl_a.config(text="Km" if c else "Peso (kg)")
        self.lbl_b.config(text="Minuti" if c else "Reps")

    def update_info(self):
        ex, data = self.ex.get(), self.app.data
        if not ex:
            self.info.config(text="Aggiungi prima un esercizio dalla scheda 'Esercizi'.")
            return
        d = self.day_idx()
        ss = logic.sessions(data, ex, d) or logic.sessions(data, ex)
        if ss:
            l = ss[-1]
            text = (f"Ultima sessione ({l['date']}, {logic.DAYS[logic.log_day(l)]}): "
                    + " | ".join(logic.fmt_item(s, self.cardio()) for s in logic.items(l)))
        else:
            text = "Nessuna sessione precedente."
        tip = logic.suggest(data, ex, d)
        self.info.config(text=text + (f"\nSuggerimento: {tip}" if tip else ""))

    def render_pending(self):
        self.listbox.delete(0, "end")
        for i, s in enumerate(self.pending, 1):
            self.listbox.insert("end", f"{i}. {logic.fmt_item(s, self.cardio())}")

    def add_item(self):
        try:
            a, b = float(self.a.get().replace(",", ".")), float(self.b.get().replace(",", "."))
            if self.cardio():
                if a <= 0 or b <= 0:
                    raise ValueError
            else:
                if a < 0 or b <= 0 or b != int(b):
                    raise ValueError
                b = int(b)
        except ValueError:
            messagebox.showerror("Errore", "Inserisci valori numerici validi.")
            return
        self.pending.append([a, b])
        self.render_pending()
        self.b.delete(0, "end")
        (self.a if self.cardio() else self.b).focus()

    def undo_item(self):
        if self.pending:
            self.pending.pop()
            self.render_pending()

    def save(self):
        if not self.ex.get() or not self.pending:
            messagebox.showwarning("Attenzione", "Seleziona un esercizio e aggiungi almeno un inserimento.")
            return
        try:
            logic.weekday(self.date.get())
        except ValueError:
            messagebox.showerror("Errore", "Data non valida (AAAA-MM-GG).")
            return
        cardio = self.cardio()
        res = logic.add_log(self.app.data, self.ex.get(), self.date.get(), self.pending, self.day_idx())
        lines = [f"{logic.fmt_item(s, cardio)}  ->  {', '.join(f)}" for s, f in res if f]
        self.pending = []
        self.render_pending()
        self.app.changed()
        self.result.config(text="Salvato." + ("\n" + "\n".join(lines) if lines else ""))

    def refresh(self):
        sync_combobox(self.cb, self.ex, self.available())
        self.update_labels()
        self.update_info()
