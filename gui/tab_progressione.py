"""Scheda: storico, grafico e confronto sessione su sessione (filtrabile per giorno)."""
import tkinter as tk
from tkinter import messagebox, ttk

from core import logic

from .chart import LineChart
from .common import ALL_DAYS, day_filter, exercise_names, fmt_delta, make_tree, set_columns, sync_combobox

STRENGTH_COLS = [("date", "Data", 110, "w"), ("top", "Top set", 90, "center"), ("e1rm", "e1RM", 80, "e"),
                 ("vol", "Volume", 90, "e"), ("delta", "Δ e1RM", 90, "e")]
CARDIO_COLS = [("date", "Data", 110, "w"), ("km", "Km", 80, "e"), ("min", "Minuti", 80, "e"),
               ("pace", "Passo", 100, "e"), ("speed", "Km/h", 80, "e"), ("delta", "Δ km", 90, "e")]


class TabProgressione(ttk.Frame):
    title = "Progressione"

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.rows = []
        top = ttk.Frame(self)
        top.pack(fill="x")
        self.ex, self.day = tk.StringVar(), tk.StringVar(value=ALL_DAYS)
        ttk.Label(top, text="Esercizio").pack(side="left")
        self.cb = ttk.Combobox(top, textvariable=self.ex, state="readonly", width=30)
        self.cb.pack(side="left", padx=6)
        self.cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        ttk.Label(top, text="Giorno").pack(side="left", padx=(12, 4))
        day_cb = ttk.Combobox(top, textvariable=self.day, values=[ALL_DAYS] + logic.DAYS, state="readonly", width=14)
        day_cb.pack(side="left")
        day_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.status = ttk.Label(self, wraplength=880, justify="left")
        self.status.pack(anchor="w", pady=8)
        self.chart = LineChart(self)
        self.chart.pack(fill="x")
        self.tree = make_tree(self, STRENGTH_COLS, height=9)
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.tag_configure("pos", foreground="#1a7f37")
        self.tree.tag_configure("neg", foreground="#c62828")
        ttk.Button(self, text="Elimina sessione selezionata", command=self.delete).pack(anchor="w")

    def delete(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Conferma", "Eliminare la sessione selezionata?"):
            logic.delete_session(self.app.data, self.rows[int(sel[0])]["entry"])
            self.app.changed()

    def refresh(self):
        data = self.app.data
        sync_combobox(self.cb, self.ex, exercise_names(data))
        ex, day = self.ex.get(), day_filter(self.day)
        cardio = bool(ex) and logic.is_cardio(data, ex)
        self.tree.delete(*self.tree.get_children())
        set_columns(self.tree, CARDIO_COLS if cardio else STRENGTH_COLS)
        self.rows = logic.progress_rows(data, ex, day) if ex else []
        for i, r in enumerate(self.rows):
            tag = "" if r["delta"] is None else ("pos" if r["delta"] > 0 else "neg" if r["delta"] < 0 else "")
            if cardio:
                vals = (r["date"], f"{r['km']:g}", f"{r['min']:g}", logic.fmt_pace(r["pace"]),
                        f"{r['speed']:.1f}", fmt_delta(r["delta"]))
            else:
                vals = (r["date"], r["top"], f"{r['e1rm']:.1f}", f"{r['volume']:.0f}", fmt_delta(r["delta"]))
            self.tree.insert("", "end", iid=str(i), tags=(tag,), values=vals)
        self.chart.plot([r["date"] for r in self.rows], [r["metric"] for r in self.rows],
                        "Km per sessione" if cardio else "e1RM (kg)")
        self.status.config(text=self.status_text(ex, day, cardio))

    def status_text(self, ex, day, cardio):
        data = self.app.data
        if not ex:
            return ""
        scope = "tutti i giorni" if day is None else logic.DAYS[day]
        if not self.rows:
            return f"Nessun dato per questo esercizio ({scope})."
        pr = logic.personal_records(data, ex, day)
        ss = logic.sessions(data, ex, day)
        lines = [f"Record ({scope}):"]
        if cardio:
            pace_txt = f"{logic.fmt_pace(pr['pace'])} ({pr['pace_date']})" if pr["pace"] else f"- (serve un'uscita da {logic.MIN_KM_PACE:g}+ km)"
            lines[0] += (f" distanza {pr['dist'][0]:g} km ({pr['dist_date']})  |  miglior passo {pace_txt}"
                         f"  |  uscita più lunga {pr['dur'][1]:g} min ({pr['dur_date']})")
            if logic.is_stall(ss, True):
                lines.append(f"⚠ STALLO: né distanza né passo migliorano da {logic.STALL_SESSIONS} sessioni.")
        else:
            lines[0] += (f" peso {logic.fmt(pr['weight'])} ({pr['weight_date']})  |  "
                         f"miglior e1RM {pr['e1rm']:.1f} kg da {logic.fmt(pr['e1rm_set'])} ({pr['e1rm_date']})")
            if logic.is_stall(ss):
                lines.append(f"⚠ STALLO: nessun miglioramento dell'e1RM nelle ultime {logic.STALL_SESSIONS} sessioni.")
            tip = logic.suggest(data, ex, day)
            if tip:
                lines.append("Prossima volta: " + tip)
        return "\n".join(lines)
