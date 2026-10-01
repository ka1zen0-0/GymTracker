"""Logica pura (nessuna dipendenza dalla GUI): progressione, PR, stalli, cardio, giorni."""
from datetime import date

DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
STALL_SESSIONS = 3  # sessioni senza miglioramento => stallo
MIN_KM_PACE = 1.0  # il PR di passo conta solo per uscite di almeno questa distanza


# ---------- utilità generali ----------
def is_cardio(data, ex):
    return data["exercises"].get(ex, {}).get("kind", "strength") == "cardio"


def weekday(d):
    return date.fromisoformat(d).weekday()


def log_day(l):
    """Giorno della scheda a cui appartiene la sessione (retrocompatibile con i vecchi dati)."""
    return l["day"] if l.get("day") is not None else weekday(l["date"])


def sessions(data, ex, day=None):
    return sorted((l for l in data["logs"] if l["exercise"] == ex and (day is None or log_day(l) == day)),
                  key=lambda l: l["date"])


def items(l):
    return l["runs"] if "runs" in l else l["sets"]


def pct(new, old):
    return (new - old) / old * 100 if old else None


# ---------- forza ----------
def e1rm(w, r):
    """Massimale stimato (Epley)."""
    return w if r <= 1 else w * (1 + r / 30)


def fmt(s):
    return f"{s[0]:g}x{s[1]}"


def volume(sets):
    return sum(w * r for w, r in sets)


def best_set(sets):
    return max(sets, key=lambda s: e1rm(*s))


# ---------- cardio ----------
def pace(km, mins):
    return mins / km if km else None


def fmt_pace(p):
    if p is None:
        return "-"
    m, s = divmod(round(p * 60), 60)
    return f"{m}:{s:02d} /km"


def fmt_run(r):
    return f"{r[0]:g} km in {r[1]:g} min"


def cardio_totals(runs):
    km, mins = sum(r[0] for r in runs), sum(r[1] for r in runs)
    return km, mins, pace(km, mins)


def fmt_item(s, cardio):
    return fmt_run(s) if cardio else fmt(s)


# ---------- stalli ----------
def is_stall(ss, cardio=False):
    """Forza: l'e1RM non supera il best precedente. Cardio: né distanza né passo migliorano."""
    if len(ss) <= STALL_SESSIONS:
        return False
    old, new = ss[:-STALL_SESSIONS], ss[-STALL_SESSIONS:]
    if cardio:
        km = lambda L: max(cardio_totals(x["runs"])[0] for x in L)
        pc = lambda L: min(cardio_totals(x["runs"])[2] for x in L)
        return km(new) <= km(old) + 1e-9 and pc(new) >= pc(old) - 1e-9
    best = lambda L: max(e1rm(*best_set(x["sets"])) for x in L)
    return best(new) <= best(old) + 1e-9


# ---------- esercizi e piano settimanale ----------
def add_exercise(data, name, dp=False, lo=0, hi=0, step=0.0, kind="strength"):
    name = name.strip()
    if not name:
        raise ValueError("Nome mancante.")
    if name.lower() in (n.lower() for n in data["exercises"]):
        raise ValueError("Esercizio già presente.")
    if kind == "strength" and dp and not (0 < lo < hi and step > 0):
        raise ValueError("Range rep o incremento non validi.")
    data["exercises"][name] = {"kind": kind, "dp": dp and kind == "strength", "lo": lo, "hi": hi, "step": step}


def delete_exercise(data, name):
    data["exercises"].pop(name, None)
    data["logs"] = [l for l in data["logs"] if l["exercise"] != name]
    for lst in data["plan"].values():
        if name in lst:
            lst.remove(name)


def plan_get(data, day):
    return data["plan"].get(str(day), [])


def plan_add(data, day, ex):
    lst = data["plan"].setdefault(str(day), [])
    if ex not in lst:
        lst.append(ex)


def plan_remove(data, day, ex):
    if ex in plan_get(data, day):
        data["plan"][str(day)].remove(ex)


# ---------- suggerimenti e PR ----------
def suggest(data, ex, day=None):
    """Suggerimento di double progression (solo forza), basato sull'ultima sessione di quel giorno."""
    if is_cardio(data, ex):
        return None
    ss = sessions(data, ex, day) or sessions(data, ex)
    if not ss:
        return None
    cfg = data["exercises"][ex]
    w = max(s[0] for s in ss[-1]["sets"])
    reps = [r for ww, r in ss[-1]["sets"] if ww == w]
    if not cfg["dp"]:
        return f"Ultima volta top {w:g} kg x {max(reps)}: prova +1 rep o più carico."
    if min(reps) >= cfg["hi"]:
        return f"Tutte le serie a {cfg['hi']}+ rep: sali a {w + cfg['step']:g} kg e riparti da {cfg['lo']} rep."
    return f"Resta a {w:g} kg e punta a {min(cfg['hi'], min(reps) + 1)}+ rep su ogni serie (ultima: {reps})."


def check_prs(prior_sets, new_sets):
    """Forza: PR di peso, e1RM, reps a parità di carico."""
    if not prior_sets:
        return [(s, ["primo dato"]) for s in new_sets]
    max_w = max(s[0] for s in prior_sets)
    max_e = max(e1rm(*s) for s in prior_sets)
    reps_at = {}
    for w, r in prior_sets:
        reps_at[w] = max(reps_at.get(w, 0), r)
    out = []
    for w, r in new_sets:
        flags = []
        if w > max_w:
            flags.append("PR PESO")
        if e1rm(w, r) > max_e + 1e-9:
            flags.append("PR e1RM")
        if w in reps_at and r > reps_at[w]:
            flags.append(f"PR REPS a {w:g} kg")
        max_w, max_e = max(max_w, w), max(max_e, e1rm(w, r))
        reps_at[w] = max(reps_at.get(w, 0), r)
        out.append(([w, r], flags))
    return out


def check_prs_cardio(prior, new):
    """Cardio: PR di distanza, durata e passo."""
    if not prior:
        return [(r, ["primo dato"]) for r in new]
    max_km, max_min = max(r[0] for r in prior), max(r[1] for r in prior)
    paces = [pace(*r) for r in prior if r[0] >= MIN_KM_PACE]
    best_p = min(paces) if paces else None
    out = []
    for km, mn in new:
        flags, p = [], pace(km, mn)
        if km > max_km:
            flags.append("PR DISTANZA")
        if mn > max_min:
            flags.append("PR DURATA")
        if km >= MIN_KM_PACE:
            if best_p is None or p < best_p - 1e-9:
                flags.append("PR PASSO")
            best_p = p if best_p is None else min(best_p, p)
        max_km, max_min = max(max_km, km), max(max_min, mn)
        out.append(([km, mn], flags))
    return out


def personal_records(data, ex, day=None):
    ss = sessions(data, ex, day)
    if is_cardio(data, ex):
        rows = [(l["date"], r) for l in ss for r in l["runs"]]
        if not rows:
            return None
        dd, rd = max(rows, key=lambda x: x[1][0])
        dt, rt = max(rows, key=lambda x: x[1][1])
        fast = [x for x in rows if x[1][0] >= MIN_KM_PACE]
        out = {"kind": "cardio", "dist": rd, "dist_date": dd, "dur": rt, "dur_date": dt,
               "pace": None, "pace_run": None, "pace_date": None}
        if fast:
            dp_, rp = min(fast, key=lambda x: pace(*x[1]))
            out.update(pace=pace(*rp), pace_run=rp, pace_date=dp_)
        return out
    rows = [(l["date"], s) for l in ss for s in l["sets"]]
    if not rows:
        return None
    dw, sw = max(rows, key=lambda x: (x[1][0], x[1][1]))
    de, se = max(rows, key=lambda x: e1rm(*x[1]))
    return {"kind": "strength", "weight": sw, "weight_date": dw,
            "e1rm": e1rm(*se), "e1rm_set": se, "e1rm_date": de}


# ---------- log ----------
def add_log(data, ex, d, new_items, day=None):
    """Registra serie/uscite (unendole se esiste già la sessione di quel giorno). Ritorna i PR."""
    cardio = is_cardio(data, ex)
    key = "runs" if cardio else "sets"
    prior = [x for l in sessions(data, ex) for x in items(l)]
    result = (check_prs_cardio if cardio else check_prs)(prior, new_items)
    entry = next((l for l in data["logs"] if l["exercise"] == ex and l["date"] == d), None)
    if entry:
        entry[key] += new_items
    else:
        data["logs"].append({"date": d, "exercise": ex, "day": weekday(d) if day is None else day, key: new_items})
    return result


def delete_session(data, entry):
    data["logs"].remove(entry)


# ---------- tabelle per la GUI ----------
def progress_rows(data, ex, day=None):
    """Una riga per sessione. 'metric' è il valore del grafico (e1RM per forza, km per cardio)."""
    out, prev = [], None
    cardio = is_cardio(data, ex)
    for l in sessions(data, ex, day):
        if cardio:
            km, mn, p = cardio_totals(l["runs"])
            out.append({"entry": l, "date": l["date"], "km": km, "min": mn, "pace": p,
                        "speed": km / (mn / 60), "delta": pct(km, prev), "metric": km})
            prev = km
        else:
            b = best_set(l["sets"])
            e = e1rm(*b)
            out.append({"entry": l, "date": l["date"], "top": fmt(b), "e1rm": e, "volume": volume(l["sets"]),
                        "delta": pct(e, prev), "metric": e})
            prev = e
    return out


def overview_rows(data, day=None):
    out = []
    for ex in sorted(data["exercises"], key=str.lower):
        ss = sessions(data, ex, day)
        if day is not None and not ss and ex not in plan_get(data, day):
            continue
        cardio = is_cardio(data, ex)
        row = {"name": ex, "cardio": cardio, "n": len(ss), "last": "-", "delta": None, "r1": "-", "r2": "-", "stall": False}
        if ss:
            pr = personal_records(data, ex, day)
            if cardio:
                row["last"] = f"{cardio_totals(ss[-1]['runs'])[0]:g} km"
                if len(ss) > 1:
                    row["delta"] = pct(cardio_totals(ss[-1]["runs"])[0], cardio_totals(ss[-2]["runs"])[0])
                row["r1"], row["r2"] = f"{pr['dist'][0]:g} km", fmt_pace(pr["pace"])
            else:
                b = best_set(ss[-1]["sets"])
                row["last"] = fmt(b)
                if len(ss) > 1:
                    row["delta"] = pct(e1rm(*b), e1rm(*best_set(ss[-2]["sets"])))
                row["r1"], row["r2"] = fmt(pr["weight"]), f"{pr['e1rm']:.1f}"
            row["stall"] = is_stall(ss, cardio)
        out.append(row)
    return out
