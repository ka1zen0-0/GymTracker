"""Finestra principale: contiene le schede e i dati condivisi."""
import tkinter as tk
from tkinter import ttk

from core import storage

from .tab_allenamento import TabAllenamento
from .tab_esercizi import TabEsercizi
from .tab_panoramica import TabPanoramica
from .tab_progressione import TabProgressione
from .tab_settimana import TabSettimana


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gym Tracker")
        self.geometry("960x700")
        self.minsize(800, 580)
        self.data = storage.load()
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        self.tabs = [TabAllenamento(nb, self), TabProgressione(nb, self), TabPanoramica(nb, self),
                     TabSettimana(nb, self), TabEsercizi(nb, self)]
        for t in self.tabs:
            nb.add(t, text=t.title)
        self.refresh_all()

    def changed(self):
        """Da chiamare dopo ogni modifica ai dati: salva e aggiorna tutte le schede."""
        storage.save(self.data)
        self.refresh_all()

    def refresh_all(self):
        for t in self.tabs:
            t.refresh()
