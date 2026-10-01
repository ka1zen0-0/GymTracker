# Gym Tracker

Run with: python main.py (requires Python 3.9+ with tkinter, already included on Windows/macOS).

main.py: entry point, opens the GUI
core/: pure logic (logic.py) and JSON storage (storage.py)
gui/: window and tabs (Workout, Progress, Overview, Week, Exercises)
data/gym_data.json: your data (created on first save)

Exercises are either Strength (weight x reps, optional double progression) or Cardio (km and minutes). Each session is tied to a day of the week: progression, PRs and plateaus can be filtered by day.
