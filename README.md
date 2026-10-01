<img width="360" height="360" alt="360_F_207114637_7o5RqH69WsjqgHUbQtBMIxcX93e9p5Un" src="https://github.com/user-attachments/assets/0397dc2b-2d4c-4d7d-b732-3015dc6fc7d3" />
# Gym Tracker

Avvio: `python main.py` (serve Python 3.9+ con tkinter, già incluso su Windows/macOS).

- `main.py`: entry point, apre la GUI
- `core/`: logica pura (`logic.py`) e salvataggio JSON (`storage.py`)
- `gui/`: finestra e schede (Allenamento, Progressione, Panoramica, Settimana, Esercizi)
- `data/gym_data.json`: i tuoi dati (creato al primo salvataggio)

Esercizi di tipo **Forza** (peso x reps, double progression opzionale) o **Cardio** (km e minuti).
Ogni sessione è legata a un giorno della settimana: progressione, PR e stalli si possono filtrare per giorno.
