"""Single source of truth for the edit: VO placement, cuts, text beats, sound events.
All times in seconds. 120 BPM grid (beat = 0.5 s)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
VO_DIR = os.path.join(HERE, "..", "vo")
FPS = 30
W, H = 1080, 1920
DURATION = 24.6

# VO line start times (trimmed clips)
VO = {
    "L01": 0.25, "L02": 2.50, "L03": 4.30, "L04": 5.85, "L05": 9.00,
    "L06": 10.50, "L07": 12.50, "L08": 14.75, "L09": 18.50, "L10": 20.50, "L11": 21.55,
}
_meta = json.load(open(os.path.join(VO_DIR, "final_meta.json")))

def word_time(line, word_idx):
    """absolute start time of a word in a VO line"""
    return VO[line] + max(0.0, _meta[line]["words"][word_idx][1])

def line_end(line):
    return VO[line] + _meta[line]["dur"]

# Shot list: (start, end, shot_id)
SHOTS = [
    (0.00, 2.50, "cells"),        # 37 trillion cells
    (2.50, 4.25, "eye"),          # who do you trust with them?
    (4.25, 5.75, "marketing"),    # a marketing team?  (glitch, tape stop)
    (5.75, 9.00, "mousa"),        # top 1%
    (9.00, 10.50, "patents"),     # 400+
    (10.50, 12.50, "pubs"),       # 1,000+
    (12.50, 14.75, "citations"),  # 33,000+
    (14.75, 18.50, "harakeh"),    # 2x Nobel laureate
    (18.50, 20.15, "capsule"),    # together, they built this
    (20.15, 20.40, "black"),      # suck-out
    (20.40, DURATION, "logo"),    # OMNIA + tagline
]

# Key sync points
T_TRILLION = word_time("L01", 1)      # counter lands
T_CELLS = word_time("L01", 2)
T_TRUST = word_time("L02", 3)
T_THEM = word_time("L02", 5)
T_MARKETING = word_time("L03", 1)
T_TOP = word_time("L04", 6)
T_PERCENT = word_time("L04", 8)
T_PATENTS = word_time("L05", 2)
T_PUBS = word_time("L06", 2)
T_CITES = word_time("L07", 2)
T_COFOUNDER = word_time("L08", 1)
T_TWOTIME = word_time("L08", 5)
T_NOBEL = word_time("L08", 6)
T_TOGETHER = word_time("L09", 0)
T_THIS = word_time("L09", 4)
T_LOGO = 20.40
T_TAGLINE = VO["L11"]
T_WITHIN = word_time("L11", 3)

if __name__ == "__main__":
    for k in sorted(VO):
        print(k, f"{VO[k]:6.2f} -> {line_end(k):6.2f}", _meta[k]["text"])
    for n in ["T_TRILLION","T_CELLS","T_TRUST","T_THEM","T_MARKETING","T_TOP","T_PERCENT","T_PATENTS","T_PUBS","T_CITES","T_COFOUNDER","T_TWOTIME","T_NOBEL","T_TOGETHER","T_THIS","T_LOGO","T_TAGLINE","T_WITHIN"]:
        print(n, round(globals()[n], 3))

def capsule_heartbeats():
    out, t, per = [], 18.5, 0.5
    while t < 20.05:
        out.append(t); t += per; per = max(0.17, per * 0.82)
    return out

T_HARAKEH_CUT = 16.30      # cut from co-founder portrait to vintage lab
LAND = {"patents": T_PATENTS - 0.15, "pubs": T_PUBS - 0.20, "cites": T_CITES - 0.25}
