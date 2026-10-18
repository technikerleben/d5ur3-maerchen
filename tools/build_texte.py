#!/usr/bin/env python3
"""Märchentexte als Schülerfassung: A4, Zeilennummern alle 5 Zeilen, Fußnoten am Seitenende.

Quelle: inhalt/texte.json (gesperrt, Gate C). Ausgabe: ausgabe/texte/<id>_A4.pdf und
ausgabe/texte/zeilen.json (Zeilenzahl, Seiten, Zeilen je Seite, Zeile jeder Fußnote).

    python3 tools/build_texte.py              # alle Texte
    python3 tools/build_texte.py frau-holle   # einzelne Texte

Satz: 15 pt Text, 14 pt Fußnoten und Fußzeile; gedruckt wird auf A5 verkleinert (Material) bzw.
in A4 Originalgröße (Probearbeit, LEK). Kinderseiten nie unter 14 pt (Fußnotenzeichen ausgenommen).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from satz import ROOT, esc, fussnoten_positionen, kleinste_schrift, render_seiten, wort_spans  # noqa: E402

QUELLE = ROOT / "inhalt" / "texte.json"
AUS = ROOT / "ausgabe" / "texte"

ROLLEN = {
    "beispielmaerchen": "Beispielmärchen", "uebungsmaerchen_blatt5": "Übungsmärchen",
    "etappe5_wahl1": "Etappe 5 · Märchenanfang zur Wahl", "etappe5_wahl2": "Etappe 5 · Märchenanfang zur Wahl",
    "probearbeit": "Probearbeit", "lek_v1": "Lernerfolgskontrolle", "lek_v2": "Lernerfolgskontrolle",
    "training_ue1": "Training", "training_ue2": "Training",
}

CSS = """
.meta{font-size:14pt;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#444}
h1{font-size:30pt;line-height:1.15;margin:1mm 0 1mm}
.quelle{font-size:14pt;font-style:italic;color:#444;margin-bottom:5mm}
.par{font-size:15pt;line-height:1.5;padding-left:13mm;margin-bottom:2.5mm}
.par.vers{padding-left:23mm;font-style:italic;margin-bottom:0}
.par.vers + .par:not(.vers){margin-top:2.5mm}
.hint{font-size:14pt;color:#444;margin-top:4mm}
"""


def text_html(t: dict) -> tuple[str, list[dict]]:
    absaetze = [p.get("absatz") or "\n".join(p["vers"]) for p in t["text"]]
    marken = fussnoten_positionen(absaetze, t.get("fussnoten", []))
    # Nummern in Lesereihenfolge vergeben
    reihen = sorted(marken.items(), key=lambda kv: kv[0])
    nummern, nr = {}, 0
    for _, idx in reihen:
        for i in idx:
            nr += 1
            nummern[i] = nr
    teile = []
    kopf = ROLLEN.get(t["rolle"], t["rolle"])
    teile.append("<div class=meta>%s</div><h1>%s</h1><div class=quelle>%s</div>" % (esc(kopf), esc(t["titel"]), esc(t["quelle"])))
    for a, p in enumerate(t["text"]):
        if "vers" in p:
            # jeder Vers eine eigene Zeile: Absatz je Vers, Fundstellen über Gesamttext des Absatzes
            versatz, start = [], 0
            for v in p["vers"]:
                sub = {(a, e - start): i for (aa, e), i in marken.items() if aa == a and start < e <= start + len(v)}
                versatz.append("<div class='par vers'>%s</div>" % wort_spans(v, a, sub, nummern))
                start += len(v) + 1
            teile.append("".join(versatz))
        else:
            teile.append("<div class=par>%s</div>" % wort_spans(p["absatz"], a, marken, nummern))
    if not t.get("vollstaendig", True) or t.get("eigen"):
        teile.append("<div class=hint>Hier endet der Anfang. Wie geht es weiter?</div>")
    fns = [{"nr": nummern[i], "stelle": esc(f["stelle"]), "erklaerung": esc(f["erklaerung"])}
           for i, f in enumerate(t.get("fussnoten", []))]
    return "".join(teile), fns


def main(ids: list[str]) -> int:
    daten = json.loads(QUELLE.read_text(encoding="utf-8"))
    texte = [t for t in daten["texte"] if not ids or t["id"] in ids]
    zeilen_alt = json.loads((AUS / "zeilen.json").read_text(encoding="utf-8")) if (AUS / "zeilen.json").exists() else {}
    fehler = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page()
        for t in texte:
            inhalt, fns = text_html(t)
            pdf = AUS / f"{t['id']}_A4.pdf"
            info = render_seiten(pg, inhalt, CSS, fns, pdf, fuss_rechts=t["titel"])
            # Zeile jeder Fußnote ermitteln
            fz = pg  # Seite ist nach dem Rendern noch im DOM
            fn_zeilen = fz.evaluate("""() => [...document.querySelectorAll('sup.fz')].map(s => {
                const l = s.closest('.ln'); return [+s.dataset.fn, l && l.dataset.zeile ? +l.dataset.zeile : null]; })""")
            mn = kleinste_schrift(pdf, ausnahmen=(11.0,))
            ok = mn >= 14
            fehler += not ok
            zeilen_alt[t["id"]] = {"zeilen": info["zeilen"], "seiten": info["seiten"], "zeilen_je_seite": info["zeilen_je_seite"],
                                   "fussnoten": {t["fussnoten"][i]["stelle"]: z for i, z in fn_zeilen}}
            print("%-18s %3d Zeilen  %d S.  %2d Fußnoten  min %.1f pt %s" % (
                t["id"], info["zeilen"], info["seiten"], len(fns), mn, "" if ok else "  << unter 14 pt"))
        browser.close()
    (AUS / "zeilen.json").write_text(json.dumps(zeilen_alt, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
