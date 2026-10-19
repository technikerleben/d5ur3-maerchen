"""Bewertung (Festlegung C, 19.10.2026): je Kompetenz 0–4 Punkte nach Standard; Notengrenzen in Prozent der Punkte."""
from __future__ import annotations

import json
import math

from satz import ROOT, esc

P = json.loads((ROOT / "inhalt" / "pruefung.json").read_text("utf-8"))
STANDARDS = P["standards"]          # [["nicht erkennbar", 0], ["in Ansätzen", 1], ...]
GRENZEN = P["notengrenzen"]         # [["sehr gut", 87], ...]


def notenschluessel(maximum: int) -> list[tuple[str, int, int]]:
    """(Note, ab Punkte, bis Punkte); Untergrenze = Prozent der Höchstpunktzahl, aufgerundet."""
    aus, oben = [], maximum
    for note, pct in GRENZEN:
        ab = math.ceil(pct * maximum / 100 - 1e-9)
        aus.append((note, ab, oben))
        oben = ab - 1
    return aus


KURZ = {"nicht erkennbar": "–", "in Ansätzen": "Ansätze", "Mindeststandard": "Mindest", "Regelstandard": "Regel", "Leistungsstandard": "Leistung"}


def kopf_standards() -> str:
    return "".join("<th class=st>%d<br>%s</th>" % (p, KURZ[n]) for n, p in STANDARDS)


def legende() -> str:
    return " · ".join("%d = %s" % (p, esc(n)) for n, p in STANDARDS)


def kaestchen() -> str:
    return "<td class=k>☐</td>" * len(STANDARDS)


def schluessel_html(maximum: int) -> str:
    return ("<table class=ns style='margin-top:3mm'><tr><th>Note</th>%s</tr><tr><th>Punkte</th>%s</tr></table>" % (
        "".join("<td>%s</td>" % n for n, _, _ in notenschluessel(maximum)),
        "".join("<td>%d–%d</td>" % (a, b) if a != b else "<td>%d</td>" % a for _, a, b in notenschluessel(maximum))))


BEW_CSS = """
.st{font-size:14pt;font-weight:700;text-align:center;width:19mm;line-height:1.15;padding:1.5mm .5mm}
.ns{width:100%;border-collapse:collapse;font-size:14pt}.ns td,.ns th{border:1pt solid #111;padding:1.5mm 1mm;text-align:center;white-space:nowrap}
"""
