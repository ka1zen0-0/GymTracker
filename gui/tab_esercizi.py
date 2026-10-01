"""Scheda: aggiunta/rimozione esercizi (forza o cardio)."""
import tkinter as tk
from tkinter import messagebox, ttk

from core import logic

from .common import exercise_names, make_tree


class TabEsercizi(ttk.Frame):
    title = "Esercizi"

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        form = ttk.LabelFrame(self, text="Nuovo esercizio", padding=10)
        form.pack(fill="x")
        self.name, self.kind, self.dp = tk.StringVar(), tk.StringVar(value="strength"), tk.BooleanVar()
        self.lo, self.hi, self.step = tk.StringVar(value="8"), tk.StringVar(value="12"), tk.StringVar(value="2.5")
        ttk.Label(form, text="Nome").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.name, width=32).grid(row=0, column=1, columnspan=5, sticky="w", padx=6)
        ttk.Label(form, text="Tipo").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Radiobutton(form, text="Forza (peso x reps)", variable=self.kind, value="strength",
                        command=self._toggle).grid(row=1, column=1, columnspan=2, sticky="w")
        ttk.Radiobutton(form, text="Cardio (km e minuti)", variable=self.kind, value="cardio",
                        command=self._toggle).grid(row=1, column=3, columnspan=3, sticky="w")
        self.dpcb = ttk.Checkbutton(form, text="Double progression", variable=self.dp, command=self._toggle)
        self.dpcb.grid(row=2, column=0, columnspan=2, sticky="w")
        self.fields = []
        for col, (label, var) in enumerate([("Rep min", self.lo), ("Rep max", self.hi), ("Incremento kg", self.step)]):
            ttk.Label(form, text=label).grid(row=3, column=col * 2, sticky="e", padx=(8, 2))
            e = ttk.Entry(form, textvariable=var, width=6)
            e.grid(row=3, column=col * 2 + 1, sticky="w")
            self.fields.append(e)
        ttk.Button(form, text="Aggiungi", command=self.add).grid(row=4, column=0, pady=(10, 0), sticky="w")
        self._toggle()

        self.tree = make_tree(self, [("name", "Esercizio", 280, "w"), ("prog", "Tipo / progressione", 340, "w")], height=14)
        self.tree.pack(fill="both", expand=True, pady=10)
        ttk.Button(self, text="Elimina esercizio selezionato", command=self.delete).pack(anchor="w")

    def _toggle(self):
        strength = self.kind.get() == "strength"
        self.dpcb.configure(state="normal" if strength else "disabled")
        on = strength and self.dp.get()
        for e in self.fields:
            e.configure(state="normal" if on else "disabled")

    def add(self):
        kind, dp = self.kind.get(), self.dp.get() and self.kind.get() == "strength"
        try:
            lo, hi, step = (int(self.lo.get()), int(self.hi.get()), float(self.step.get().replace(",", "."))) if dp else (0, 0, 0.0)
        except ValueError:
            messagebox.showerror("Errore", "Valori di rep o incremento non validi.")
            return
        try:
            logic.add_exercise(self.app.data, self.name.get(), dp, lo, hi, step, kind)
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            return
        self.name.set("")
        self.app.changed()

    def delete(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Conferma", f"Eliminare '{sel[0]}' e tutto il suo storico?"):
            logic.delete_exercise(self.app.data, sel[0])
            self.app.changed()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for n in exercise_names(self.app.data):
            c = self.app.data["exercises"][n]
            if c.get("kind") == "cardio":
                prog = "Cardio (km, minuti)"
            elif c["dp"]:
                prog = f"Forza, double progression {c['lo']}-{c['hi']} rep, +{c['step']:g} kg"
            else:
                prog = "Forza, progressione libera"
            self.tree.insert("", "end", iid=n, values=(n, prog))
