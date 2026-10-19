#!/usr/bin/env python3
"""Lernerfolgskontrolle (V1/V2 + F) und Training (1/2) aus inhalt/pruefung.json.

    python3 tools/build_pruefung.py

Ausgabe ausgabe/abschluss/:
  LEK_V1_A4.pdf, LEK_V2_A4.pdf        Märchenanfang, Aufgaben, Bewertungsseite (A4 Original)
  LEK_Erwartungshorizont_A4.pdf       Lehrkraft, beide Varianten
  foerder/LEK_V1F_A4.pdf, LEK_V2F_A4.pdf
  Training_1_A4.pdf, Training_2_A4.pdf     Märchenanfang + Auftrag
  Training_1_Muster_A4.pdf, ...            Musterfortsetzung für den Kiosk
Vorher: python3 tools/build_texte.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_material import (F_JS, FOERDER_CSS, GN_CSS, PROBE_CSS, TEXTE, doc, drucke, esc,  # noqa: E402
                            f_auftrag, md, verbinde)
from satz import ROOT, bild_uri  # noqa: E402
from bewertung import BEW_CSS, STANDARDS, kaestchen, kopf_standards, legende, schluessel_html  # noqa: E402

P = json.loads((ROOT / "inhalt" / "pruefung.json").read_text("utf-8"))
TITEL = {t["id"]: t["titel"] for t in json.loads((ROOT / "inhalt" / "texte.json").read_text("utf-8"))["texte"]}
SUMME = sum(k["punkte"] for k in P["kriterien"])


def checkliste_tabelle() -> str:
    return "<table class=ck style='margin-top:2mm'><tr><th>Kriterium</th><th>Prüffrage</th><th class=k>✓</th></tr>%s</table>" % "".join(
        "<tr><td><b>%s</b> %s</td><td>%s</td><td class=k>☐</td></tr>" % (k, esc(t), esc(f)) for k, t, f in P["checkliste"])


def aufgaben_html(meta: str, titel: str, maerchen: str, hinweis: str, termin: bool) -> str:
    kopf = ("<div class=kopfzeile><div><div class=meta>%s</div><h1>%s</h1></div><img src='%s' alt=''></div>"
            % (esc(meta), esc(titel), bild_uri("weiterschreiben")))
    namen = "<div class=namen><span>Name:</span><span>Datum:</span></div>"
    if termin:
        namen += "<div class=namen><span>Termin: ☐ früh &nbsp; ☐ spät</span><span>Arbeitszeit: %s</span></div>" % esc(P["arbeitszeit"])
    teile = [kopf, namen, "<div class=hinweis>%s</div>" % hinweis]
    for n, a in enumerate(P["aufgaben"], 1):
        text = md(a["text"].replace("{T}", TITEL[maerchen]))
        linien = "<div class=linie></div>" * a["linien"]
        if a.get("rand"):
            teile.append("<div class=auf><span class=nr>%d.</span> %s</div><div class=zeilen>%s</div>" % (n, text, linien))
        else:
            teile.append("<div class=auf><span class=nr>%d.</span> %s%s%s</div>" % (
                n, text, checkliste_tabelle() if a.get("checkliste") else "", linien))
    return doc(PROBE_CSS, "".join(teile))


def bewertung_html(v: str) -> str:
    rows = "".join("<tr><td><b>%s</b> %s</td>%s</tr>" % (k["k"], esc(k["titel"]), kaestchen()) for k in P["kriterien"])
    return doc(GN_CSS + BEW_CSS, (
        "<div class=meta>Lernerfolgskontrolle · Variante %s · Bewertung</div><h1>Das hast du gezeigt</h1>"
        "<table><tr><th>Kompetenz</th>%s</tr>%s</table>"
        "<div class=erg><b>Punkte: ____ / %d</b> &nbsp;&nbsp; <b>Note: ______</b></div>%s"
        "<div class=feld><b>Das gelingt dir schon:</b></div><div class=feld><b>Dein nächster Schritt:</b></div>"
        "<div style='font-size:14pt;margin-top:3mm'>Datum, Unterschrift der Lehrkraft: ______________________</div>"
        "<div style='font-size:14pt;margin-top:2mm'>Unterschrift einer erziehungsberechtigten Person: ______________________</div>")
        % (v, kopf_standards(), rows, SUMME, schluessel_html(SUMME)))


def erwartung_html() -> str:
    teile = ["<div class=meta>Lehrkraft · Lernerfolgskontrolle</div><h1>Erwartungshorizont</h1>",
             "<p style='font-size:14pt;margin-bottom:3mm'>Gleicher Aufbau wie die Probearbeit. Arbeitszeit %s. Hilfen: keine (Merkblatt und Märchenkarten bleiben in der Tasche). "
             "Jede Kompetenz wird einem Standard zugeordnet: %s. Höchstpunktzahl %d. Aufgabe 1 (Plan) fließt in K3 ein; "
             "K5 bewertet Prüfbeleg und Verbesserungen, nicht die Fehlerzahl.</p>" % (esc(P["arbeitszeit"]), legende(), SUMME)]
    for k in P["kriterien"]:
        teile.append("<table style='margin-bottom:3mm'><tr><th colspan=2>%s · %s</th></tr>%s</table>" % (k["k"], esc(k["titel"]), "".join(
            "<tr><td style='width:34mm'><b>%d</b> %s</td><td>%s</td></tr>" % (p, esc(n), esc(t))
            for (n, p), t in zip(STANDARDS[1:], k["stufen"]))))
    teile.append("<h2 style='font-size:17pt;margin:4mm 0 2mm'>Notenschlüssel</h2>%s<p style='font-size:14pt;margin-top:2mm'>Grenzen: %s; darunter ungenügend. "
                 "Untergrenzen aufgerundet.</p>" % (schluessel_html(SUMME), " · ".join("%s ab %d %%" % (n, g) for n, g in P["notengrenzen"][:-1])))
    for v, var in P["lek"].items():
        teile.append("<h2 style='font-size:17pt;margin:5mm 0 2mm'>Variante %s · „%s“</h2><p style='font-size:14pt'>%s</p>"
                     "<p style='font-size:14pt;margin-top:2mm'><b>Grimm-Original (nur Orientierung, kein Maßstab):</b> %s</p>"
                     % (v, esc(TITEL[var["maerchen"]]), esc(var["anknuepfung"]), esc(var["original"])))
    teile.append("<p style='font-size:14pt;margin-top:4mm'>Jede schlüssige Fortsetzung gilt.</p>")
    return doc(GN_CSS + BEW_CSS, "".join(teile))


def f_html(v: str, var: dict) -> tuple[str, str]:
    f = var["f"]
    kopf = ("<div class=fkopf><div class=meta>Lernerfolgskontrolle F · Variante %s</div><h1>%s</h1>"
            "<div style='display:flex;gap:8mm;font-size:14pt;margin-bottom:3mm'><span style='flex:1;border-bottom:1pt solid #111'>Name:</span>"
            "<span style='flex:1;border-bottom:1pt solid #111'>Datum:</span></div></div>" % (v, esc(f["titel"])))
    auf = doc(FOERDER_CSS, "<div id=q>%s%s</div>%s" % (
        kopf, "".join(re.sub(r"data-loes='[^']*'", "data-loes=''", f_auftrag(a)) for a in f["auftraege"]), F_JS))
    rows = "".join("<tr><td>%s</td>%s</tr>" % (esc(z["kind"]), kaestchen()) for z in P["f_ziele"])
    summe = sum(z["punkte"] for z in P["f_ziele"])
    rueck = doc(GN_CSS + BEW_CSS, (
        "<div class=meta>Lernerfolgskontrolle F · Variante %s · Bewertung</div><h1>Das hast du gezeigt</h1>"
        "<table><tr><th>Dein Ziel</th>%s</tr>%s</table>"
        "<div class=erg><b>Punkte: ____ / %d</b> &nbsp;&nbsp; <b>Note: ______</b></div>%s"
        "<div class=feld><b>Das gelingt dir schon:</b></div><div class=feld><b>Dein nächster Schritt:</b></div>"
        "<div style='font-size:14pt;margin-top:3mm'>Lehrkraft-Hinweis (zieldifferent nach Förderplan): %s</div>")
        % (v, kopf_standards(), rows, summe, schluessel_html(summe), esc(" · ".join("%s %s" % (z["id"], z["lehrkraft"]) for z in P["f_ziele"]))))
    return auf, rueck


def training_html(nr: str, t: dict) -> str:
    hinweis = ("Training vor der Lernerfolgskontrolle. Arbeite wie in der Lernerfolgskontrolle, aber du darfst <b>Merkblatt 5</b> und die "
               "<b>Checkliste</b> benutzen. Plane die Zeit: etwa 10 Minuten planen, 25 Minuten schreiben, 10 Minuten prüfen.")
    teile = ["<div class=kopfzeile><div><div class=meta>Training %s</div><h1>%s</h1></div><img src='%s' alt=''></div>"
             % (nr, esc(TITEL[t["maerchen"]]), bild_uri("weiterschreiben")),
             "<div class=hinweis>%s</div>" % hinweis,
             "<div class=auf><span class=nr>1.</span> Lies den Märchenanfang. Plane deine Fortsetzung in Stichworten im Heft: <b>Weg · Prüfung · Lösung · Ende</b>.</div>",
             "<div class=auf><span class=nr>2.</span> Schreibe die Fortsetzung ins Heft und führe das Märchen zu Ende. Schreibe in jede zweite Zeile.</div>",
             "<div class=auf><span class=nr>3.</span> Mach den Prüfbeleg: Satzanfänge einkreisen, Verben unterstreichen, Redezeichen markieren. Prüfe mit deiner <b>Checkliste K1–K5</b> und verbessere mindestens zwei Stellen.</div>",
             "<div class=auf><span class=nr>4.</span> Hol dir am Kiosk die <b>Musterfortsetzung</b>. Vergleiche: Was hat das Muster, was du auch hast? "
             "Was möchtest du dir abschauen? Schreibe einen Satz ins Heft.</div>",
             "<div class=karten>%s</div>" % esc("Dir fehlt eine Idee? Deine Märchenkarten zeigen dir Figuren, Orte, Zauberdinge und Märchenmerkmale.")]
    return doc(PROBE_CSS, "".join(teile))


def muster_html(nr: str, t: dict) -> str:
    rows = "".join("<tr><td><b>%s</b></td><td>%s</td></tr>" % (k, md(s)) for k, s in t["muster_k"])
    return doc(GN_CSS, (
        "<div class=kopfzeile><div><div class=meta>Training %s · Kiosk</div><h1>Eine mögliche Fortsetzung</h1></div><img src='%s' alt=''></div>"
        "<div class=hinweis>Das ist <b>eine</b> Möglichkeit. Deine Fortsetzung darf ganz anders sein – sie muss nur zum Anfang passen und die Kriterien erfüllen.</div>"
        "<div class=anfang><b>„%s“ – so könnte es weitergehen</b><div style='margin-top:1.5mm'>%s</div></div>"
        "<h2 style='font-size:17pt;margin:4mm 0 2mm'>So erfüllt das Muster die Kriterien</h2><table>%s</table>"
        "<h2 style='font-size:17pt;margin:4mm 0 2mm'>Eine ganz andere Idee</h2><div class=hinweis>%s</div>"
        "<div style='font-size:14pt'>Vergleiche mit deinem Text: Welche Kriterien erfüllst du auch? Was fehlt dir noch?</div>")
        % (nr, bild_uri("lupe"), esc(TITEL[t["maerchen"]]), esc(t["muster"]), rows, md(t["andere_idee"])))


def main() -> int:
    aus = ROOT / "ausgabe" / "abschluss"
    tmp = aus / "_teile"
    (aus / "foerder").mkdir(parents=True, exist_ok=True)
    tmp.mkdir(exist_ok=True)
    bericht, fehler = [], []
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page()

        def mach(h: str, pdf: Path, fuss: str, minpt: float = 14) -> Path:
            mn = drucke(pg, h, pdf, fuss)
            bericht.append("%-34s %d S.  min %.1f pt%s" % (pdf.name, len(fitz.open(pdf)), mn, "" if mn >= minpt else "  << unter %g pt" % minpt))
            if mn < minpt:
                fehler.append(pdf.name)
            return pdf

        hinweis = "Du brauchst: den Märchenanfang „%s“ (vorne). Schreibe auf diese Blätter. Arbeite allein. Merkblatt und Märchenkarten bleiben in der Tasche."
        for v, var in P["lek"].items():
            a = mach(aufgaben_html("Lernerfolgskontrolle · Variante " + v, "Ein Märchen weiterschreiben", var["maerchen"],
                                   hinweis % esc(TITEL[var["maerchen"]]), True), tmp / f"lek_{v}.pdf", f"LEK {v}")
            b = mach(bewertung_html(v), tmp / f"lek_{v}_bew.pdf", f"LEK {v} · Bewertung")
            s = verbinde([TEXTE / f"{var['maerchen']}_A4.pdf", a, b], aus / f"LEK_{v}_A4.pdf")
            bericht.append("%-34s %d S.  (Märchenanfang, Aufgaben, Bewertung)" % (f"LEK_{v}_A4.pdf", s))
            fa, fb = f_html(v, var)
            a = mach(fa, tmp / f"lekf_{v}.pdf", f"LEK F {v}")
            b = mach(fb, tmp / f"lekf_{v}_bew.pdf", f"LEK F {v} · Bewertung")
            s = verbinde([a, b], aus / "foerder" / f"LEK_{v}F_A4.pdf")
            bericht.append("%-34s %d S." % (f"foerder/LEK_{v}F_A4.pdf", s))
        mach(erwartung_html(), aus / "LEK_Erwartungshorizont_A4.pdf", "LEK · Lehrkraft", 12)
        for nr, t in P["training"].items():
            a = mach(training_html(nr, t), tmp / f"tr_{nr}.pdf", f"Training {nr}")
            s = verbinde([TEXTE / f"{t['maerchen']}_A4.pdf", a], aus / f"Training_{nr}_A4.pdf")
            bericht.append("%-34s %d S.  (Märchenanfang, Auftrag)" % (f"Training_{nr}_A4.pdf", s))
            mach(muster_html(nr, t), aus / f"Training_{nr}_Muster_A4.pdf", f"Training {nr} · Kiosk")
        br.close()
    for x in tmp.iterdir():
        x.unlink()
    tmp.rmdir()
    print("\n".join(bericht))
    if fehler:
        print("FEHLER:", *fehler, sep="\n  ")
        return 1
    print("Prüfung: alle Seiten ≥ 14 pt (Erwartungshorizont ≥ 12 pt).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
