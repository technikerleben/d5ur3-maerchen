#!/usr/bin/env python3
"""Lernweg (+F), Wahlhilfe nach dem Feedback, Projekte P1–P3 und Reinschriftvorlage Märchenbuch.

    python3 tools/build_wahlzeit.py

Ausgabe ausgabe/wahlzeit/:
  Lernweg_Maerchen_A4.pdf, Lernweg_Maerchen_F_A4.pdf   eine Seite, A4 Originalgröße
  Wahlhilfe_A4.pdf                                     offene Kriterien → Übungsweg
  Projekt_P1_Maerchenbuch_A4.pdf, Projekt_P2_Vorlesen_A4.pdf, Projekt_P3_Umformen_A4.pdf
  Projekte_P1-P3_A4.pdf                                alle drei (A4 gesetzt, auf A5 verkleinert drucken)
  Reinschrift_Maerchenbuch_A4.pdf                      Vorlage zum Scannen, A4 Originalgröße
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_material import BLATT_CSS, KARTEN, doc, drucke, esc, md, verbinde  # noqa: E402
from satz import ROOT, bild_uri  # noqa: E402

W = json.loads((ROOT / "inhalt" / "wahlzeit.json").read_text("utf-8"))
ET = [json.loads((ROOT / "inhalt" / f"etappe{n}.json").read_text("utf-8")) for n in range(1, 6)]

LERNWEG_CSS = """
body{font-size:13pt;line-height:1.3}
h1{font-size:22pt;margin-bottom:1mm}
.namen{display:flex;gap:8mm;font-size:13pt;margin:1mm 0 3mm}.namen span{flex:1;border-bottom:1pt solid #111}
table{width:100%;border-collapse:collapse}td,th{border:1pt solid #111;padding:1.4mm 2mm;vertical-align:top;text-align:left}
th{background:#eee;font-size:12.5pt}.et{width:42mm}.et b{display:block;font-size:13pt}.et span{font-size:12pt}
.ck{white-space:nowrap;width:44mm}.it{white-space:nowrap;display:inline-block;margin-right:3.5mm}.ab td{background:#f4f4f4}
.legende{font-size:12pt;margin-top:2mm}
"""

PROJEKT_CSS = BLATT_CSS + """
.gelingt{border:2pt solid #111;border-radius:3mm;padding:2.5mm 4mm;margin-bottom:3.5mm}
.gelingt .etikett{border:1.5pt solid #111}
"""

REIN_CSS = """
@page{size:A4;margin:22mm 22mm 24mm 22mm}
body{font-size:15pt}
.feld{display:flex;gap:8mm;margin-bottom:5mm}.feld div{flex:1;border-bottom:1.6pt solid #000;padding-bottom:1mm;font-size:14pt}
.titel{border-bottom:2pt solid #000;height:16mm;margin-bottom:6mm;font-size:14pt}
.bild{border:2pt solid #000;height:70mm;margin-bottom:6mm;position:relative}
.bild span{position:absolute;left:3mm;top:2mm;font-size:14pt}
.l{height:12mm;border-bottom:1.4pt solid #000}
.seite{break-after:page}.seite:last-child{break-after:auto}
"""


def lernweg_html(f: bool) -> str:
    rows = []
    for e in ET:
        n = e["etappe"]
        if f:
            items = ["☐ Merkkarte %dF" % n] + ["☐ Blatt %s" % b["nr"] for b in e["foerder"]["blaetter"]]
            nw = "☐ Probearbeit F" if n == 5 else "☐ GN%dF · A ☐ B ☐" % n
        else:
            items = ["☐ Merkblatt %d" % n] + ["☐ Blatt %s ☐ frei" % b["nr"] for b in e["blaetter"]]
            nw = "☐ Probearbeit<br>____ / 5" if n == 5 else "☐ GN%d · A ☐ B ☐<br>____ / 5" % n
        rows.append("<tr><td class=et><b>Etappe %d</b><span>%s</span></td><td>%s</td><td class=ck>%s</td><td style='width:18mm'></td></tr>"
                    % (n, esc(e["titel"]), " ".join("<span class=it>%s</span>" % i for i in items), nw))
    ab = W["lernweg_f_abschluss"] if f else W["lernweg_abschluss"]
    rows += ["<tr class=ab><td class=et><b>%s</b></td><td colspan=2>%s</td><td></td></tr>" % (esc(a), md(b)) for a, b in ab]
    return doc(LERNWEG_CSS, (
        "<div class=kopfzeile><div><div class=meta>Lernweg%s · Deutsch · Märchen</div><h1>Mein Weg durch die Märchen</h1></div><img src='%s' alt=''></div>"
        "<div class=namen><span>Name:</span><span>Start:</span></div>"
        "<div style='font-size:13pt;margin-bottom:2mm'><b>Dein Ziel:</b> %s</div>"
        "<table><tr><th>Etappe</th><th>Das machst du</th><th>Nachweis</th><th>Datum</th></tr>%s</table>"
        "<div class=legende>%s</div>")
        % (" F" if f else "", bild_uri("maerchenbuch"), esc(W["ziel_f"] if f else W["ziel"]), "".join(rows), md(W["legende_f"] if f else W["legende"])))


def wahlhilfe_html() -> str:
    rows = "".join("<tr><td><b>%s</b> %s</td><td class=k style='font-size:16pt'>☐</td><td>%s</td></tr>" % (k, esc(t), md(u)) for k, t, u in W["wahlhilfe"])
    return doc(PROJEKT_CSS + "table{width:100%;border-collapse:collapse;font-size:14pt}td,th{border:1pt solid #111;padding:2mm;vertical-align:top;text-align:left}th{background:#eee}", (
        "<div class=kopfzeile><div><div class=meta>Wahlzeit</div><h1>Was übe ich jetzt?</h1>"
        "<div class=brauchst><b>Das brauchst du:</b> deinen Feedbackbogen der Probearbeit · Lernweg</div></div><img src='%s' alt=''></div>"
        "<div class='kasten pflicht'><span class=etikett>ZUERST</span><div>%s</div></div>"
        "<table><tr><th>Kriterium</th><th>offen</th><th>So übst du</th></tr>%s</table>"
        "<div class='kasten frei' style='margin-top:4mm'><span class=etikett>DANACH</span><div>%s</div></div>")
        % (bild_uri("lupe"), md(W["wahlhilfe_zuerst"]), rows, md(W["wahlhilfe_danach"])))


def projekt_html(p: dict) -> str:
    li = "".join("<li><b>%s:</b> %s</li>" % (esc(a), md(b)) for a, b in p["schritte"])
    teile = ["<div class=kopfzeile><div><div class=meta>Wahlzeit · Projekt %s · freiwillig</div><h1>%s</h1><div class=brauchst><b>Das brauchst du:</b> %s</div></div><img src='%s' alt=''></div>"
             % (p["nr"], esc(p["titel"]), esc(p["brauchst"]), bild_uri(p["bild"])),
             "<div style='margin-bottom:3mm'>%s</div>" % md(p["einleitung"]),
             "<div class='kasten pflicht'><span class=etikett>SO GEHST DU VOR</span><ol>%s</ol></div>" % li,
             "<div class=gelingt><span class=etikett>GELINGT, WENN</span><div>%s</div></div>" % "<br>".join("☐ " + md(g) for g in p["gelingt"])]
    if p.get("erweiterung"):
        teile.append("<div class='kasten frei'><span class=etikett>NOCH MEHR</span><div>%s</div></div>" % md(p["erweiterung"]))
    return doc(PROJEKT_CSS, "".join(teile))


def reinschrift_html() -> str:
    s1 = ("<div class=seite><div class=feld><div>Vorname oder Kürzel:</div><div style='flex:.6'>Klasse:</div></div>"
          "<div class=titel>Titel:</div><div class=bild><span>Mein Bild</span></div>%s</div>") % ("<div class=l></div>" * 9)
    s2 = "<div class=seite><div class=feld><div>Vorname oder Kürzel:</div><div style='flex:.4'>Seite:</div></div>%s</div>" % ("<div class=l></div>" * 17)
    return doc(REIN_CSS, s1 + s2)


def main() -> int:
    aus = ROOT / "ausgabe" / "wahlzeit"
    aus.mkdir(parents=True, exist_ok=True)
    bericht, fehler = [], []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page()

        def mach(h: str, pdf: Path, fuss: str, minpt: float = 14) -> Path:
            mn = drucke(pg, h, pdf, fuss)
            seiten = len(fitz.open(pdf))
            bericht.append("%-36s %d S.  min %.1f pt%s" % (pdf.name, seiten, mn, "" if mn >= minpt else "  << unter %g pt" % minpt))
            if mn < minpt:
                fehler.append(pdf.name)
            return pdf

        for f in (False, True):
            pdf = mach(lernweg_html(f), aus / ("Lernweg_Maerchen%s_A4.pdf" % ("_F" if f else "")), "Lernweg" + (" F" if f else ""), 12)
            if len(fitz.open(pdf)) != 1:
                fehler.append(pdf.name + " ist länger als eine Seite")
        mach(wahlhilfe_html(), aus / "Wahlhilfe_A4.pdf", "Wahlzeit")
        teile = [mach(projekt_html(p), aus / p["datei"], "Projekt " + p["nr"]) for p in W["projekte"]]
        s = verbinde(teile, aus / "Projekte_P1-P3_A4.pdf")
        bericht.append("%-36s %d S." % ("Projekte_P1-P3_A4.pdf", s))
        mach(reinschrift_html(), aus / "Reinschrift_Maerchenbuch_A4.pdf", "Märchenbuch")
        br.close()
    print("\n".join(bericht))
    if fehler:
        print("FEHLER:", *fehler, sep="\n  ")
        return 1
    print("Prüfung: Kinderseiten ≥ 14 pt, Lernweg ≥ 12 pt und eine Seite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
