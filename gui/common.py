"""Helper condivisi tra le schede."""
from tkinter import ttk

from core import logic

ALL_DAYS = "Tutti i giorni"


def exercise_names(data):
    return sorted(data["exercises"], key=str.lower)


def sync_combobox(cb, var, names):
    """Aggiorna le voci mantenendo la selezione se ancora valida."""
    cb["values"] = names
    if var.get() not in names:
        var.set(names[0] if names else "")


def day_filter(var):
    """Valore del filtro giorno: None = tutti, altrimenti indice 0-6."""
    return None if var.get() == ALL_DAYS else logic.DAYS.index(var.get())


def fmt_delta(d):
    return "-" if d is None else f"{d:+.1f}%"


def set_columns(tree, columns):
    """columns: lista di (id, titolo, larghezza, ancora)."""
    tree["columns"] = [c[0] for c in columns]
    for cid, title, width, anchor in columns:
        tree.heading(cid, text=title)
        tree.column(cid, width=width, anchor=anchor)


def make_tree(parent, columns, height=10):
    tree = ttk.Treeview(parent, show="headings", height=height)
    set_columns(tree, columns)
    return tree
