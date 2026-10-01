# Gym Tracker

Avvio: `python main.py` (serve Python 3.9+ con tkinter, già incluso su Windows/macOS).

- `main.py`: entry point, apre la GUI
- `core/`: logica pura (`logic.py`) e salvataggio JSON (`storage.py`)
- `gui/`: finestra e schede (Allenamento, Progressione, Panoramica, Settimana, Esercizi)
- `data/gym_data.json`: i tuoi dati (creato al primo salvataggio)

Esercizi di tipo **Forza** (peso x reps, double progression opzionale) o **Cardio** (km e minuti).
Ogni sessione è legata a un giorno della settimana: progressione, PR e stalli si possono filtrare per giorno.
