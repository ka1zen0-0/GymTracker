"""Grafico a linee minimale su Canvas (nessuna dipendenza esterna)."""
import tkinter as tk

COLOR = "#2b6cb0"


class LineChart(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg="white", highlightthickness=1, highlightbackground="#cccccc", height=200, **kw)
        self.labels, self.values, self.title = [], [], ""
        self.bind("<Configure>", lambda e: self.draw())

    def plot(self, labels, values, title=""):
        self.labels, self.values, self.title = labels, values, title
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        L, R, T, B = 50, 20, 20, 30
        vals, n = self.values, len(self.values)
        if not vals:
            self.create_text(w / 2, h / 2, text="Nessun dato", fill="#888")
            return
        lo, hi = min(vals), max(vals)
        if hi - lo < 1e-9:
            lo, hi = lo - 1, hi + 1
        pad = (hi - lo) * 0.1
        lo, hi = lo - pad, hi + pad
        x = lambda i: L + (w - L - R) * (i / (n - 1) if n > 1 else 0.5)
        y = lambda v: T + (h - T - B) * (1 - (v - lo) / (hi - lo))
        small = ("TkDefaultFont", 8)
        self.create_text(L, 8, text=self.title, anchor="w", fill="#666", font=small)
        for k in range(5):
            v = lo + (hi - lo) * k / 4
            self.create_line(L, y(v), w - R, y(v), fill="#e5e5e5")
            self.create_text(L - 6, y(v), text=f"{v:.1f}", anchor="e", fill="#666", font=small)
        pts = [(x(i), y(v)) for i, v in enumerate(vals)]
        if n > 1:
            self.create_line(*[c for p in pts for c in p], fill=COLOR, width=2)
        for i, (px, py) in enumerate(pts):
            self.create_oval(px - 4, py - 4, px + 4, py + 4, fill=COLOR, outline="white")
            if n <= 12:
                self.create_text(px, py - 12, text=f"{vals[i]:.1f}", fill="#333", font=small)
            if n <= 6 or i in (0, n - 1):
                self.create_text(px, h - B + 14, text=self.labels[i], fill="#666", font=small)
