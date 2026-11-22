#!/usr/bin/env python3
"""Fassung 2 (Umbau 11/2026): Etappenpakete, Wocheninputs, Strategiekarten, Lesestrang, Raummaterial.

    python3 tools/build_f2.py etappe 1      Etappenpaket, GN A/B, Erwartungshorizont, Förderpaket
    python3 tools/build_f2.py input 1       Wocheninput W1 (HTML) und Lehrkraft-Skript
    python3 tools/build_f2.py lesestrang 1  Lesebogen W1
    python3 tools/build_f2.py lerntheke     Strategiekarten (A5 quer)
    python3 tools/build_f2.py raum          Plakat „Wo stehe ich?“, Zonenschilder, Satzstarter, Lernweg
    python3 tools/build_f2.py druck [N]     Gesamt-PDF je Etappe: Druckanleitung (mit Seitenangaben) + alle neuen Druckteile
    python3 tools/build_f2.py alles         alles, was es schon gibt

Ausgabe: ausgabe/f2/…  · Material der Kollegin liegt (nicht im Repo) in extern/ und wird nur eingelegt.
Grundsätze: Input zeigt lautes Denken (kein Merkblatt-Abbild); Strategien haben Symbole, die an Aufgaben,
Karten und im Input gleich sind; Schülerseiten ≥ 14 pt.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_material import (BLATT_CSS, F_JS, FOERDER_CSS, GN_CSS, TEXTE, doc, drucke, esc, f_blatt_html,  # noqa: E402
                            f_gn_html, f_merkkarte_html, gn_aufgaben_html, gn_erwartung_html,
                            gn_rueckmeldung_html, md, verbinde)
from satz import ROOT, font_css, zeile  # noqa: E402

IN = ROOT / "inhalt" / "f2"
AUS = ROOT / "ausgabe" / "f2"
EXTERN = ROOT / "extern"
TEXTDB = {t["id"]: t for t in json.loads((ROOT / "inhalt" / "texte.json").read_text("utf-8"))["texte"]}
STRAT = {k["id"]: k for k in json.loads((IN / "strategien.json").read_text("utf-8"))["karten"]}
RAUM = json.loads((IN / "raum.json").read_text("utf-8"))

# ------------------------------------------------------------ Symbole (Strichzeichnung, druckt in Graustufen)
_P = {
    "stern": "<path d='M12 2.5l2.9 6.2 6.6.8-4.9 4.6 1.3 6.6L12 17.4l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z'/>",
    "fernglas": "<circle cx='6.5' cy='15.5' r='4.5'/><circle cx='17.5' cy='15.5' r='4.5'/><path d='M11 15.5h2M4 11l2-6h3l1 6M20 11l-2-6h-3l-1 6'/>",
    "buch": "<path d='M2 5.5c3.5-1.5 7-1.5 10 1 3-2.5 6.5-2.5 10-1V20c-3.5-1.5-7-1.5-10 1-3-2.5-6.5-2.5-10-1z'/><path d='M12 6.5V21'/>",
    "lupe": "<circle cx='10' cy='10' r='6.5'/><path d='M15 15l6.5 6.5'/>",
    "eins": "<circle cx='12' cy='7' r='3.6'/><path d='M4.5 21c0-4.5 3.4-7.5 7.5-7.5s7.5 3 7.5 7.5'/>",
    "zwei": "<circle cx='8' cy='8' r='3.2'/><circle cx='16.5' cy='8' r='3.2'/><path d='M1.5 20.5c0-4 2.9-6.5 6.5-6.5 1.6 0 3 .5 4.2 1.4M10 20.5c.3-3.8 3-6.5 6.5-6.5s6.2 2.7 6.5 6.5'/>",
    "lesen": "<path d='M2 6c3.5-1.5 7-1.5 10 1 3-2.5 6.5-2.5 10-1v13c-3.5-1.5-7-1.5-10 1-3-2.5-6.5-2.5-10-1z'/><path d='M12 7v13M5 9.5h4M5 12.5h4M15 9.5h4M15 12.5h4'/>",
    "haken": "<circle cx='12' cy='12' r='9.5'/><path d='M7.5 12.3l3 3 6-6.3'/>",
    "plus": "<circle cx='12' cy='12' r='9.5' stroke-dasharray='2.6 2'/><path d='M12 7.5v9M7.5 12h9'/>",
    "bogen": "<path d='M2.5 20C6 6 18 6 21.5 20'/><circle cx='12' cy='9.5' r='1.6'/><path d='M2.5 20h19'/>",
    "auge": "<path d='M1.5 12C5 6 19 6 22.5 12 19 18 5 18 1.5 12z'/><circle cx='12' cy='12' r='3.4'/>",
    "plan": "<rect x='4.5' y='3.5' width='15' height='18' rx='1.5'/><path d='M9 3.5h6v3H9zM8 11h8M8 14.5h8M8 18h5'/>",
    "uhr": "<circle cx='12' cy='12' r='9.5'/><path d='M12 6.5V12l4 2.5'/>",
    "figur": "<circle cx='9' cy='8' r='3.6'/><path d='M2 21c0-4.3 3-7.2 7-7.2s7 2.9 7 7.2'/><path d='M14.5 2.5h7.5v6h-4l-2 2v-2h-1.5z'/>",
    "klammer": "<path d='M9 2.5h6l-1 9h-4zM10 11.5l-1.5 10h7l-1.5-10'/>",
}


def sym(name: str, mm: float = 9) -> str:
    return ("<svg class=sym viewBox='0 0 24 24' width='%smm' height='%smm' fill='none' stroke='#111' stroke-width='1.7' "
            "stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>%s</svg>" % (mm, mm, _P[name]))


def strat_hinweis(ids: list[str]) -> str:
    return "<div class=hilft><b>Das hilft dir (Lerntheke):</b> %s</div>" % " · ".join(
        "%s %s" % (sym(STRAT[i]["symbol"], 7), esc(STRAT[i]["titel"])) for i in ids)


F2_CSS = BLATT_CSS + """
.sym{vertical-align:-1.6mm;flex:none}
.kopf2{display:flex;justify-content:space-between;align-items:flex-start;gap:4mm;border-bottom:2pt solid #111;padding-bottom:2mm;margin-bottom:3mm}
.kopf2 .meta{display:flex;align-items:center;gap:2mm}
.hilft{font-size:14pt;border:1.5pt solid #111;border-radius:2.5mm;padding:1.5mm 3mm;margin-bottom:3mm}
.auf2{border:2pt solid #111;border-radius:3mm;padding:2.5mm 4mm;margin-bottom:3.5mm;break-inside:avoid}
.auf2 h2{font-size:17pt;display:flex;justify-content:space-between;align-items:center;gap:3mm;margin-bottom:1.5mm}
.auf2 h2 small{font-size:14pt;font-weight:400;display:flex;align-items:center;gap:1.5mm}
.merke{font-size:15pt;border-left:4pt solid #111;padding:1mm 3mm;margin:1mm 0 2mm;background:#f0f0f0}
.satzbox{font-size:17pt;line-height:2.1;border:1.2pt solid #777;border-radius:2mm;padding:1mm 3mm;margin-top:2mm}
.anfang{border:1.5pt solid #111;border-radius:2.5mm;padding:2mm 3.5mm;margin:2mm 0;font-size:15pt;line-height:1.45}
.anfang .fnz{font-size:14pt;border-top:1pt solid #777;margin-top:1.5mm;padding-top:1mm}
.linie{height:11mm;border-bottom:1pt solid #555}
.schritte{list-style:none;padding:0}.schritte li{display:flex;gap:3mm;align-items:flex-start;margin-bottom:2.5mm}
.schritte .n{font-weight:700;min-width:7mm}
.tipp{font-size:14pt;font-style:italic;margin-top:1mm}
.starter{font-size:14pt;border:1.5pt dashed #111;border-radius:2.5mm;padding:1.5mm 3mm;margin-bottom:3mm}
.starter b{display:block}
.unterschrift{display:flex;gap:8mm;font-size:14pt;margin-top:5mm}.unterschrift span{flex:1;border-top:1pt solid #111;padding-top:1mm}
table.st{width:100%;border-collapse:collapse;font-size:15pt}table.st td{border:1.5pt solid #111;padding:2.5mm 3mm;vertical-align:middle}
table.st td.i{width:14mm;text-align:center}
table.st.eng td{padding:1.2mm 2.5mm;font-size:14.5pt;line-height:1.25}table.st td.k{width:12mm;text-align:center;font-size:20pt}
"""


def kopf(meta: str, titel: str, icon: str | None, brauchst: str | None = None) -> str:
    return "<div class=kopf2><div><div class=meta>%s%s</div><h1>%s</h1>%s</div></div>" % (
        sym(icon, 8) if icon else "", esc(meta), esc(titel), "<div class=brauchst><b>Das brauchst du:</b> %s</div>" % esc(brauchst) if brauchst else "")


def anfang_box(tid: str) -> str:
    t = TEXTDB[tid]
    fn = " · ".join("<i>%s:</i> %s" % (esc(f["stelle"]), esc(f["erklaerung"])) for f in t.get("fussnoten", []))
    txt = " ".join(p.get("absatz") or " ".join(p["vers"]) for p in t["text"])
    return "<div class=anfang><b>%s</b><div>%s</div>%s</div>" % (esc(t["titel"]), esc(txt), "<div class=fnz>%s</div>" % fn if fn else "")


# ------------------------------------------------------------ Etappenpaket
def deckblatt_html(e: dict) -> str:
    t = TEXTDB[e["text"]]["titel"]
    zeilen = [
        ("lesen", "„%s“ lesen – im Lesetandem oder mit einem Partner" % t, False),
        ("zwei", "Zu zweit: %s" % e["gemeinsam"]["titel"], False),
        ("eins", "Allein: %s" % e["einzel"]["titel"], False),
        ("plus", "Freiwillig: Vertiefung auf dem Einzelblatt", True),
        ("haken", "Gelingensnachweis: Hol ihn bei der Lehrkraft. Ab 4 von 5 geht es weiter. &nbsp; Ergebnis: ____ / 5", False),
    ]
    rows = "".join("<tr><td class=i>%s</td><td>%s%s</td><td class=k>☐</td></tr>" % (
        sym(i, 10), "<i>%s</i>" % s if frei else s, "", ) for i, s, frei in zeilen)
    strat = sorted({*e["gemeinsam"].get("strategien", []), *[a["strategie"] for a in e["einzel"]["aufgaben"] if a.get("strategie")]},
                   key=list(STRAT).index)
    return doc(F2_CSS, (
        "<div class=kopf2><div><div class=meta>Etappe %d · dein Paket</div><h1>%s</h1></div></div>"
        "<div class=hilft style='font-size:16pt'><b>Dein Ziel:</b> %s<br><b>Richtwert:</b> %s</div>"
        "<div style='font-size:15pt;margin-bottom:2mm'><b>In deinem Paket:</b> dieses Deckblatt · „%s“ · Blatt „Zu zweit“%s · Blatt „Allein“</div>"
        "<table class=st>%s</table>"
        "<div class=hilft style='margin-top:4mm'><b>Diese Strategien helfen dir.</b> Die Karten liegen auf der Lerntheke:<br>%s</div>"
        "<div class=hilft>%s <b>Wo stehe ich?</b> Häng deine Klammer am Plakat weiter, wenn du einen Schritt geschafft hast. "
        "Wer an derselben Stelle hängt, kann dein Partner sein.</div>")
        % (e["etappe"], esc(e["titel"]), esc(e["ziel"]), esc(e["woche"]), esc(t),
           (" · Quiz Märchenmerkmale" if e.get("extern") else "") + (" mit Legeplan und Satzstreifen" if e["gemeinsam"].get("legeplan") else "") + (" mit Arbeitsseite" if e["gemeinsam"].get("arbeitsseite") else ""), rows,
           " · ".join("%s %s" % (sym(STRAT[s]["symbol"], 7), esc(STRAT[s]["titel"])) for s in strat), sym("klammer", 7)))


BOGEN_SCHRITTE = [("J", "jemand", "Einleitung: Wer? Wann? Wo?"), ("W", "wollte", "Wunsch: Was wollte jemand?"),
                  ("A", "aber", "Problem: Was kam dazwischen?"), ("D", "dann", "Versuche: Was tat die Figur?"),
                  ("D", "dann", "Höhepunkt: Wo wurde es gefährlich?"), ("A", "also", "Lösung: Wie wurde es gut?"),
                  ("A", "also", "Schluss: Wie endete es?")]


def bogen_svg() -> str:
    pkt = [(12, 36), (36, 28), (60, 20), (86, 12), (116, 6), (142, 16), (164, 30)]
    kreise = "".join("<circle cx='%d' cy='%d' r='5.2' fill='#fff' stroke='#111' stroke-width='.7'/><text x='%d' y='%.1f' text-anchor='middle' "
                     "font-size='6.2' font-weight='700' font-family='Andika'>%s</text>" % (x, y, x, y + 2.2, b) for (x, y), (b, _, _) in zip(pkt, BOGEN_SCHRITTE))
    return ("<svg viewBox='0 0 176 44' width='150mm' height='37.5mm' style='display:block;margin:0 auto 2mm'>"
            "<path d='M4 40 C40 30 80 4 116 6 C140 7 158 22 172 36' fill='none' stroke='#111' stroke-width='.9'/>%s"
            "<text x='116' y='17.5' text-anchor='middle' font-size='6.2' font-family='Andika'>Höhepunkt</text></svg>" % kreise)


def legeplan_html(e: dict) -> str:
    g = e["gemeinsam"]
    rows = "".join("<tr><td style='width:13mm;text-align:center;font-size:22pt;font-weight:700'>%s</td><td style='width:78mm'><b>%s …</b> %s</td>"
                   "<td style='height:15mm'></td></tr>" % (b, w, esc(f)) for b, w, f in BOGEN_SCHRITTE)
    return ("<div style='break-before:page'></div>" + kopf("Etappe %d · zu zweit · Legeplan" % e["etappe"], "Der Spannungsbogen", "bogen")
            + bogen_svg() + "<table class=st style='font-size:14pt'><tr><td></td><td><b>Signalwort und Frage</b></td><td><b>Hier klebt euer Streifen</b></td></tr>%s</table>" % rows
            + "<div style='font-size:15pt;margin-top:3mm'><b>Das Männchen ist …, weil …</b></div><div class=linie></div><div class=linie></div>"
            + ("<div class=unterschrift><span>Wir haben zusammen gearbeitet:</span><span>und</span></div>" if g.get("unterschrift") else ""))


def streifen_html(e: dict) -> str:
    st = "".join("<div style='border:1.4pt dashed #111;border-radius:1.5mm;padding:2.2mm 3mm;margin-bottom:2.6mm;width:124mm;font-size:14pt;line-height:1.3'>%s</div>"
                 % esc(t) for _, t in e["gemeinsam"]["streifen"])
    return ("<div style='break-before:page'></div>" + kopf("Etappe %d · zu zweit · zum Ausschneiden" % e["etappe"], "Satzstreifen", "zwei")
            + "<div class=hilft>✂ Schneidet die Streifen aus. Lest jeden Streifen laut und einigt euch, wohin er gehört.</div>%s" % st)


def arbeitsseite_html(e: dict) -> str:
    a = e["gemeinsam"]["arbeitsseite"]
    teile = ["<div style='break-before:page'></div>", kopf("Etappe %d · zu zweit · Arbeitsseite" % e["etappe"], a["titel"], "zwei")]
    for b in a.get("boxen", []):
        teile.append("<div class=anfang><b>%s</b><div>%s</div></div>" % (esc(b["titel"]), esc(b["text"])))
    if a.get("tabelle"):
        t = a["tabelle"]
        kopfz = "".join("<td><b>%s</b></td>" % esc(s) for s in t["spalten"])
        bsp = "".join("<td><i>%s</i></td>" % esc(s) for s in t.get("beispiel", []))
        leer = ("<tr>%s</tr>" % ("<td style='height:12mm'></td>" * len(t["spalten"]))) * t["zeilen"]
        teile.append("<table class=st style='table-layout:fixed;font-size:14pt'><tr>%s</tr>%s%s</table>" % (kopfz, "<tr>%s</tr>" % bsp if bsp else "", leer))
    if a.get("schreiben"):
        s = a["schreiben"]
        teile.append("<div class=anfang style='margin-top:3mm'><b>%s</b><div>%s</div></div><div style='font-size:15pt'><b>%s</b></div>%s"
                     % (esc(s["titel"]), esc(s["text"]), esc(s["auftrag"]), "<div class=linie></div>" * s["linien"]))
    if e["gemeinsam"].get("unterschrift"):
        teile.append("<div class=unterschrift><span>Wir haben zusammen gearbeitet:</span><span>und</span></div>")
    return "".join(teile)


def gemeinsam_html(e: dict) -> str:
    g = e["gemeinsam"]
    li = "".join("<li><span class=n>%d.</span><span>%s</span></li>" % (n, md(s)) for n, s in enumerate(g["schritte"], 1))
    st = "".join("<div>%s</div>" % esc(s) for _, s in RAUM["satzstarter"][:4])
    return doc(F2_CSS, (
        kopf("Etappe %d · zu zweit" % e["etappe"], g["titel"], "zwei", g["brauchst"]) + strat_hinweis(g.get("strategien", []))
        + "<div class='kasten pflicht'><span class=etikett>SO GEHT IHR VOR</span><ol class=schritte>%s</ol>%s</div>" % (
            li, "<div class=tipp>Tipp: %s</div>" % md(g["tipp"]) if g.get("tipp") else "")
        + "<div class=starter><b>So denkt ihr laut:</b>%s</div>" % st
        + ("<div class=unterschrift><span>Wir haben zusammen gearbeitet:</span><span>und</span></div>" if g.get("unterschrift") and not g.get("legeplan") and not g.get("arbeitsseite") else "")
        + (arbeitsseite_html(e) if g.get("arbeitsseite") else "")
        + (legeplan_html(e) if g.get("legeplan") else "") + (streifen_html(e) if g.get("streifen") else "")))


def einzel_html(e: dict) -> str:
    ez = e["einzel"]
    teile = [kopf("Etappe %d · allein" % e["etappe"], ez["titel"], "eins")]
    for n, a in enumerate(ez["aufgaben"], 1):
        hilft = "<small>hilft: %s %s</small>" % (sym(STRAT[a["strategie"]]["symbol"], 6.5), esc(STRAT[a["strategie"]]["titel"])) if a.get("strategie") else ""
        teile.append("<div class=auf2><h2><span>%d · %s</span>%s</h2>%s%s%s<div>%s</div>%s</div>" % (
            n, esc(a["titel"]), hilft,
            "<div class=merke>%s</div>" % md(a["merke"]) if a.get("merke") else "",
            anfang_box(a["anfang"]) if a.get("anfang") else "",
            "<div class=anfang><b>%s</b><div>%s</div></div>" % (esc(a["geschichte"]["titel"]), esc(a["geschichte"]["text"])) if a.get("geschichte") else "",
            md(a["text"]),
            ("<div class=satzbox>%s</div>" % esc(a["satzbox"]) if a.get("satzbox") else "") + "<div class=linie></div>" * a.get("linien", 0)))
    if ez.get("vertiefung"):
        teile.append("<div class='kasten frei'><span class=etikett>%s FREIWILLIG</span><div>%s</div></div>" % (sym("plus", 6), md(ez["vertiefung"])))
    return doc(F2_CSS, "".join(teile))


def platzhalter_html(name: str) -> str:
    return doc(F2_CSS, "<div class=hilft style='margin-top:60mm;font-size:20pt;text-align:center'>Hier einlegen:<br><b>%s</b><br>"
               "(Vorlage der Kollegin, liegt nicht im Repo)</div>" % esc(name))


def extern_pdf(stichwort: str) -> Path | None:
    treffer = sorted(EXTERN.glob(f"*{stichwort}*.pdf"))
    return treffer[0] if treffer else None


# ------------------------------------------------------------ Strategiekarten, Input, Lesebogen, Raum
KARTE_CSS = F2_CSS + "@page{size:A5 landscape;margin:9mm 11mm 15mm 11mm}body{font-size:16pt}h1{font-size:25pt}"


def karte_html(k: dict) -> str:
    li = "".join("<li><span class=n>%d.</span><span>%s</span></li>" % (n, md(s)) for n, s in enumerate(k["schritte"], 1))
    return doc(KARTE_CSS, (
        "<div style='display:flex;gap:5mm;align-items:center;border-bottom:2pt solid #111;padding-bottom:2mm;margin-bottom:2.5mm'>%s"
        "<div><div class=meta>Strategiekarte</div><h1 style='margin:0'>%s</h1></div></div>"
        "<div style='font-size:15pt;margin-bottom:2mm'><b>Wann?</b> %s</div><ol class=schritte>%s</ol>"
        "<div class=starter><b>So klingt lautes Denken:</b>%s</div>%s")
        % (sym(k["symbol"], 18), esc(k["titel"]), esc(k["wann"]), li, esc(k["laut"]),
           "<div class=tipp>Tipp: %s</div>" % esc(k["tipp"]) if k.get("tipp") else ""))


INPUT_CSS = """
:root{--blau:#3E5668;--blau2:#2C3D4C;--orange:#D97A4A;--orange2:#9E4E22;--gruen:#7DBB6F;--gruen2:#4D8B3F;--bg:#F5F4F1;--text:#1E2A35}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Andika',sans-serif}
.folie{position:absolute;inset:0;padding:4vh 5vw;display:none;flex-direction:column;gap:2.5vh}
.folie.an{display:flex}
.kopf{display:flex;align-items:center;gap:1.4vw;color:var(--blau2)}
.kopf .sym{width:6vh;height:6vh}.kopf .sym *{stroke:var(--blau2)}
.kopf small{display:block;font-size:2.2vh;letter-spacing:.08em;text-transform:uppercase;color:var(--orange2)}
h1{font-size:5.4vh;line-height:1.1}
.schr{list-style:none;display:grid;gap:1.6vh;font-size:3.4vh}
.schr li{background:#fff;border-left:1vh solid var(--blau);border-radius:1vh;padding:1.4vh 2vw}
.schr b{color:var(--orange2)}
.text{font-size:3.6vh;line-height:1.6;background:#fff;border-radius:1.4vh;padding:2.4vh 2.4vw;box-shadow:0 .4vh 1.4vh rgba(0,0,0,.08)}
mark{background:transparent;color:inherit;border-radius:.5vh;transition:background .3s}
mark.an{background:#F4C9AE}mark.war{text-decoration:underline .35vh var(--orange);text-underline-offset:.5vh}
.blasen{display:grid;gap:1.4vh;align-self:start}
.blase{font-size:3.2vh;line-height:1.35;background:#fff;border:.35vh solid var(--orange);border-radius:3vh;padding:1.4vh 2vw;opacity:0;transform:translateY(1vh);transition:all .3s;position:relative}
.blase:not(.an){display:none}.blase.an{opacity:1;transform:none}.blase.alt{display:none}
.zaehler{font-size:2.4vh;color:#667}
.blase::before{content:"💭";margin-right:.6em}
.karte{background:#fff;border-radius:1.4vh;padding:2vh 2vw;font-size:3.2vh;border-left:1vh solid var(--gruen2)}
.zwei{display:grid;grid-template-columns:1.25fr 1fr;gap:2.4vw;flex:1;min-height:0}
.fuss{position:absolute;bottom:2vh;right:3vw;font-size:2vh;color:#667}
.hilfe{position:absolute;bottom:2vh;left:3vw;font-size:2vh;color:#667}
"""

INPUT_JS = """
const F=[...document.querySelectorAll('.folie')];let f=0,s=0;
const B=()=>[...F[f].querySelectorAll('[data-s]')];
function zeig(){F.forEach((x,i)=>x.classList.toggle('an',i===f));
 B().forEach(b=>{const n=+b.dataset.s;b.classList.toggle('an',n<=s);b.classList.toggle('alt',n<s&&b.classList.contains('blase'))});
 document.querySelectorAll('mark').forEach(m=>{const n=+m.dataset.m,hier=F[f].contains(m);m.classList.toggle('an',hier&&n===s);m.classList.toggle('war',hier&&n<s)});
 document.querySelector('.fuss').textContent=(f+1)+' / '+F.length;}
function vor(){const max=Math.max(0,...B().map(b=>+b.dataset.s));if(s<max){s++;}else if(f<F.length-1){f++;s=0;}zeig()}
function zur(){if(s>0){s--;}else if(f>0){f--;s=Math.max(0,...B().map(b=>+b.dataset.s));}zeig()}
document.addEventListener('keydown',e=>{if(['ArrowRight',' ','PageDown','Enter'].includes(e.key)){e.preventDefault();vor()}
 if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();zur()}
 if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}});
document.addEventListener('click',e=>{e.clientX<innerWidth*0.2?zur():vor()});zeig();
"""


def input_html(w: dict) -> str:
    k = STRAT[w["strategie"]]
    txt = esc(w["text"])
    for n, d in enumerate(w["denken"], 1):
        st = esc(d["stelle"])
        if st not in txt:
            raise SystemExit("Input W%d: Stelle nicht im Text: %s" % (w["woche"], d["stelle"]))
        txt = txt.replace(st, "<mark data-m='%d'>%s</mark>" % (n, st), 1)
    kp = lambda t: "<div class=kopf>%s<div><small>Woche %d · Input</small><h1>%s</h1></div></div>" % (sym(k["symbol"], 12), w["woche"], esc(t))
    f1 = "<section class=folie>%s<div style='font-size:3vh'>Ich zeige euch, was in meinem Kopf passiert. <b>Ich denke laut.</b></div><ol class=schr>%s</ol></section>" % (
        kp(k["titel"]), "".join("<li data-s='%d'><b>%d.</b> %s</li>" % (n, n, md(s)) for n, s in enumerate(k["schritte"], 1)))
    f2 = "<section class=folie>%s<div class=zwei><div><div style='font-size:2.4vh;color:#667;margin-bottom:1vh'>%s</div><div class=text>%s</div></div><div class=blasen>%s</div></div></section>" % (
        kp("Ich denke laut"), esc(w["text_titel"]), txt, "".join("<div class=blase data-s='%d'>%s</div>" % (n, esc(d["gedanke"])) for n, d in enumerate(w["denken"], 1)))
    f3 = "<section class=folie>%s<ol class=schr>%s</ol><div class=karte data-s='%d'><b>So klingt lautes Denken:</b> %s</div></section>" % (
        kp("Jetzt ihr"), "".join("<li data-s='%d'>%s</li>" % (n, md(s)) for n, s in enumerate(w["jetzt"], 1)), len(w["jetzt"]) + 1, esc(k["laut"]))
    f4 = "<section class=folie>%s<ol class=schr>%s</ol></section>" % (kp("Hier findest du Hilfe"), "".join("<li>%s</li>" % md(s) for s in w["hilfe"]))
    return ("<!doctype html><html lang=de><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Input W%d · %s</title><style>%s%s</style></head><body>%s%s%s%s<div class=hilfe>Klick oder → weiter · ← zurück · F Vollbild</div><div class=fuss></div>"
            "<script>%s</script></body></html>") % (w["woche"], esc(w["titel"]), font_css(), INPUT_CSS, f1, f2, f3, f4, INPUT_JS)


def skript_html(w: dict) -> str:
    k = STRAT[w["strategie"]]
    rows = "".join("<tr><td>%d</td><td><b>„%s“</b></td><td>%s</td><td>%s</td></tr>" % (n, esc(d["stelle"]), esc(d["gedanke"]), esc(d["sagen"]))
                   for n, d in enumerate(w["denken"], 1))
    return doc(GN_CSS, (
        "<div class=meta>Lehrkraft · Wocheninput W%d · %s</div><h1>Skript: %s</h1>"
        "<p style='font-size:14pt;margin-bottom:3mm'><b>Ziel:</b> Das Vorgehen zeigen, nicht das Merkblatt erklären. Höchstens 10 Minuten. "
        "Folie 1 Strategie (Klick für Klick) · Folie 2 lautes Denken am Übungstext · Folie 3 Auftrag · Folie 4 Hilfe.</p>"
        "<p style='font-size:14pt;margin-bottom:2mm'><b>Übungstext:</b> %s</p>"
        "<table><tr><th>Klick</th><th>Stelle</th><th>laut denken</th><th>Hinweis</th></tr>%s</table>"
        "<ul style='font-size:14pt;margin:3mm 0 0 6mm'>%s</ul>")
        % (w["woche"], esc(w["dauer"]), esc(k["titel"]), esc(w["text"]), rows, "".join("<li>%s</li>" % esc(s) for s in w["skript"])))


def lesebogen_html(lw: dict) -> str:
    t = TEXTDB[lw["text"]]
    rows = "".join("<tr><td class=i>%s</td><td style='width:27mm;white-space:nowrap'><b>Stopp %d</b><br>nach %s</td><td>%s</td><td class=k>☐</td></tr>" % (
        sym(s["symbol"], 7.5), n, zeile(lw["text"], s["nach"]), esc(s["frage"])) for n, s in enumerate(lw["stopps"], 1))
    return doc(F2_CSS, (
        kopf("Lesestrang · Woche %d · Lesetandem" % lw["woche"], t["titel"], "lesen")
        + strat_hinweis(lw["strategien"])
        + "<div class='kasten pflicht'><span class=etikett>SO LEST IHR</span>%s</div>" % "".join("<div>%s</div>" % md(a) for a in lw["ablauf"])
        + "<table class='st eng'>%s</table>" % rows
        + "<div class=hilft style='margin-top:3mm'><b>Zum Schluss:</b> %s</div>" % esc(lw["abschluss"])
        + "<div class=unterschrift><span>Lesetandem:</span><span>und</span></div>"))


PLAKAT_CSS = F2_CSS + """
@page{size:A3 landscape;margin:12mm 14mm 18mm 14mm}
body{font-size:20pt}h1{font-size:44pt}
.raster{display:grid;grid-template-columns:repeat(6,1fr);gap:4mm;margin-top:5mm;height:215mm}
.spalte{border:2.5pt solid #111;border-radius:4mm;padding:3mm;display:flex;flex-direction:column;gap:3mm}
.spalte h2{font-size:22pt;line-height:1.1}.spalte .w{font-size:15pt;color:#333}
.feld{flex:1;border:1.8pt solid #111;border-radius:3mm;min-height:30mm;padding:2mm 3mm;display:flex;gap:2mm;align-items:flex-start;font-size:17pt;font-weight:700}
.feld.frei{border-style:dashed}
"""


def plakat_html() -> str:
    sp = ["<div class=spalte><h2>Start</h2><div class=w>Lernweg holen, Klammer beschriften</div><div class=feld>%s Startklar</div></div>" % sym("klammer", 9)]
    for e in RAUM["etappen"]:
        felder = "".join("<div class=feld>%s %s</div>" % (sym(i, 9), t) for i, t in (("zwei", "zu zweit"), ("eins", "allein"), ("haken", "Nachweis")))
        if e["n"] == 4:
            felder = "".join("<div class=feld>%s %s</div>" % (sym(i, 9), t) for i, t in (("zwei", "zu zweit planen"), ("eins", "allein schreiben"), ("haken", "Probearbeit")))
        sp.append("<div class=spalte><h2>Etappe %d</h2><div class=w>%s · %s</div>%s</div>" % (e["n"], esc(e["titel"]), esc(e["woche"]), felder))
    sp.append("<div class=spalte style='grid-column:6'><h2>Wahlzeit</h2><div class=w>Woche 6</div><div class='feld frei'>%s Training</div>"
              "<div class='feld frei'>%s Märchenbuch · Vorlesen</div></div>" % (sym("uhr", 9), sym("buch", 9)))
    # 1 Start + 4 Etappen = 5 Spalten; Wahlzeit = 6.
    return doc(PLAKAT_CSS, (
        "<div style='display:flex;justify-content:space-between;align-items:flex-end'><h1>Wo stehe ich?</h1>"
        "<div style='font-size:18pt;max-width:55%%'>%s Häng deine Klammer an den Schritt, an dem du gerade arbeitest.<br>"
        "%s Partner gesucht? Wer an derselben Stelle hängt, arbeitet mit dir.</div></div><div class=raster>%s</div>")
        % (sym("klammer", 9), sym("zwei", 9), "".join(sp)))


ZONE_CSS = F2_CSS + "@page{size:A4 landscape;margin:15mm 18mm 20mm 18mm}body{font-size:26pt}"


def zone_html(z: dict) -> str:
    return doc(ZONE_CSS, "<div style='display:flex;gap:12mm;align-items:center;margin-top:18mm'>%s<div><div style='font-size:72pt;font-weight:700;line-height:1'>%s</div>"
               "<div style='margin-top:6mm'>%s</div><div style='font-size:20pt;margin-top:6mm;color:#333'>%s</div></div></div>"
               % (sym(z["symbol"], 70), esc(z["name"]), esc(z["text"]), esc(z["was"])))


def satzstarter_html() -> str:
    rows = "".join("<tr><td style='width:42mm'><b>%s</b></td><td>%s</td></tr>" % (esc(a), esc(b)) for a, b in RAUM["satzstarter"])
    return doc(KARTE_CSS, "<div style='display:flex;gap:4mm;align-items:center;border-bottom:2pt solid #111;padding-bottom:2mm;margin-bottom:3mm'>%s"
               "<div><div class=meta>Karte</div><h1 style='margin:0'>Laut denken – zu zweit</h1></div></div><table class=st>%s</table>" % (sym("zwei", 14), rows))


LERNWEG_CSS = F2_CSS + """
body{font-size:14pt;line-height:1.3}h1{font-size:22pt}
table.lw{width:100%;border-collapse:collapse}table.lw td,table.lw th{border:1.2pt solid #111;padding:1.5mm 2mm;vertical-align:middle;text-align:left}
table.lw th{background:#eee}.c{text-align:center;white-space:nowrap}.m{text-align:center;width:16.6%}
.it{display:inline-block;white-space:nowrap;margin-right:3mm}
"""


def lernweg_html() -> str:
    rows = []
    for e in RAUM["etappen"]:
        if e["n"] == 4:
            sch = " ".join("<span class=it>%s %s ☐</span>" % (sym(i, 6), t) for i, t in (("zwei", "zu zweit planen"), ("eins", "allein schreiben"), ("zwei", "zu zweit prüfen")))
            nw = "%s Probearbeit ☐" % sym("haken", 6)
        else:
            sch = " ".join("<span class=it>%s %s ☐</span>" % (sym(i, 6), t) for i, t in (("lesen", "lesen"), ("zwei", "zu zweit"), ("eins", "allein"), ("plus", "frei")))
            nw = "%s A ☐ B ☐<br>____ / 5" % sym("haken", 6)
        rows.append("<tr><td><b>Etappe %d</b><br>%s</td><td>%s</td><td class=c>%s</td><td class=c>%s</td></tr>" % (e["n"], esc(e["titel"]), sch, nw, esc(e["woche"])))
    rows.append("<tr><td><b>Wahlzeit</b></td><td>%s</td><td></td><td class=c>Woche 6</td></tr>" % " ".join("<span class=it>%s ☐</span>" % t for t in ("Feedback lesen", "Training 1", "Training 2", "Märchenbuch", "Vorlesen")))
    rows.append("<tr><td><b>Arbeit 3</b></td><td>Mein Termin: ☐ Termin 1 &nbsp; ☐ Termin 2</td><td></td><td class=c>Woche 6</td></tr>")
    les = "".join("<td class=m><b>%s</b> ☐<br>%s</td>" % (w, esc(t)) for w, t in RAUM["lesestrang"])
    return doc(LERNWEG_CSS, (
        "<div class=kopf2><div><div class=meta>Lernweg · Deutsch · Märchen</div><h1>Mein Weg durch die Märchen</h1></div></div>"
        "<div class=unterschrift style='margin-top:0;margin-bottom:3mm'><span>Name:</span><span>Klasse:</span></div>"
        "<div style='margin-bottom:2mm'><b>Mein Ziel:</b> %s</div>"
        "<table class=lw><tr><th style='width:40mm'>Etappe</th><th>Schritte im Paket</th><th style='width:33mm'>Nachweis</th><th style='width:25mm'>Richtwert</th></tr>%s</table>"
        "<h2 style='font-size:16pt;margin:4mm 0 1.5mm'>%s Lesestrang (Sprache, im Lesetandem)</h2><table class=lw><tr>%s</tr></table>"
        "<div style='margin-top:2mm;font-size:14pt'>%s lesen · %s zu zweit · %s allein · %s freiwillig · %s Nachweis allein (ab 4 von 5 weiter)</div>")
        % (esc(RAUM["ziel"]), "".join(rows), sym("lesen", 6), les, sym("lesen", 6), sym("zwei", 6), sym("eins", 6), sym("plus", 6), sym("haken", 6)))


# ------------------------------------------------------------ Bau
class Bau:
    def __init__(self):
        self.p = sync_playwright().start()
        self.br = self.p.chromium.launch()
        self.pg = self.br.new_page()
        self.bericht, self.fehler = [], []

    def mach(self, h: str, pdf: Path, fuss: str, minpt: float = 14, max_s: int | None = None) -> Path:
        mn = drucke(self.pg, h, pdf, fuss)
        s = len(fitz.open(pdf))
        warn = ""
        if mn < minpt:
            warn += "  << unter %g pt" % minpt
            self.fehler.append(pdf.name + " Schrift")
        if max_s and s > max_s:
            warn += "  << mehr als %d S." % max_s
            self.fehler.append("%s hat %d Seiten (max. %d)" % (pdf.name, s, max_s))
        self.bericht.append("%-40s %d S.  min %.1f pt%s" % (pdf.relative_to(AUS), s, mn, warn))
        return pdf

    def ende(self) -> int:
        self.br.close()
        self.p.stop()
        print("\n".join(self.bericht))
        if self.fehler:
            print("FEHLER:", *self.fehler, sep="\n  ")
            return 1
        print("Prüfung bestanden.")
        return 0


def bau_etappe(b: Bau, n: int):
    e = json.loads((IN / f"etappe{n}.json").read_text("utf-8"))
    aus = AUS / f"etappe{n}"
    tmp = aus / "_teile"
    tmp.mkdir(parents=True, exist_ok=True)
    for s in [*e["gemeinsam"].get("strategien", []), *[a.get("strategie") for a in e["einzel"]["aufgaben"] if a.get("strategie")]]:
        if s not in STRAT:
            b.fehler.append("Strategie ohne Karte: " + s)
    d = b.mach(deckblatt_html(e), tmp / "deck.pdf", f"Etappe {n} · Paket", 14, 1)
    g = b.mach(gemeinsam_html(e), aus / f"E{n}_zu_zweit_A4.pdf", f"Etappe {n} · zu zweit", 14,
               1 + bool(e["gemeinsam"].get("legeplan")) + bool(e["gemeinsam"].get("streifen")) + 2 * bool(e["gemeinsam"].get("arbeitsseite")))
    ein = b.mach(einzel_html(e), aus / f"E{n}_allein_A4.pdf", f"Etappe {n} · allein", 14, 2)
    ext = []
    for stw in e.get("extern", []):
        pdf = extern_pdf(stw)
        if not pdf:
            pdf = b.mach(platzhalter_html(stw), tmp / f"platz_{stw}.pdf", "Vorlage Kollegin", 14)
            b.bericht.append("  (Vorlage %s fehlt in extern/ – Platzhalter eingelegt)" % stw)
        ext.append(pdf)
    s = verbinde([d, TEXTE / f"{e['text']}_A4.pdf", g, *ext, ein], aus / f"Etappenpaket_{n}_A4.pdf")
    b.bericht.append("%-40s %d S.  (Deckblatt, Text, zu zweit, Vorlage, allein)" % (f"etappe{n}/Etappenpaket_{n}_A4.pdf", s))
    nw = e["nachweis"]
    for v, var in nw["varianten"].items():
        a = b.mach(gn_aufgaben_html(e, nw, v), tmp / f"gn_{v}.pdf", f"GN{n} {v}")
        r = b.mach(gn_rueckmeldung_html(e, nw, v), tmp / f"gn_{v}_r.pdf", f"GN{n} {v} · Rückmeldung")
        s = verbinde(([TEXTE / f"{var['maerchen']}_A4.pdf"] if var.get("maerchen") else []) + [a, r], aus / f"GN{n}_{v}_A4.pdf")
        b.bericht.append("%-40s %d S." % (f"etappe{n}/GN{n}_{v}_A4.pdf", s))
    b.mach(gn_erwartung_html(e, nw), aus / f"GN{n}_Erwartungshorizont_A4.pdf", f"GN{n} · Lehrkraft", 12)
    f = e["foerder"]
    mk = b.mach(f_merkkarte_html(e), tmp / "f_merk.pdf", f"Merkkarte {n}F")
    fb = [b.mach(f_blatt_html(e, x, "Etappe %dF · Blatt %s" % (n, x["nr"])), tmp / f"f_{x['nr']}.pdf", f"Blatt {x['nr']}") for x in f["blaetter"]]
    (aus / "foerder").mkdir(exist_ok=True)
    s = verbinde([mk] + ([TEXTE / f"{f['material']}_A4.pdf"] if f.get("material") else []) + fb, aus / "foerder" / f"Foerderpaket_{n}_A4.pdf")
    b.bericht.append("%-40s %d S." % (f"etappe{n}/foerder/Foerderpaket_{n}_A4.pdf", s))
    for v in ("A", "B"):
        auf, rueck = f_gn_html(e, v)
        a = b.mach(auf, tmp / f"fgn_{v}.pdf", f"GN{n}F {v}")
        r = b.mach(rueck, tmp / f"fgn_{v}_r.pdf", f"GN{n}F {v} · Rückmeldung")
        s = verbinde([a, r], aus / "foerder" / f"GN{n}F_{v}_A4.pdf")
        b.bericht.append("%-40s %d S." % (f"etappe{n}/foerder/GN{n}F_{v}_A4.pdf", s))
    for x in tmp.iterdir():
        x.unlink()
    tmp.rmdir()


def bau_input(b: Bau, n: int):
    w = json.loads((IN / "inputs" / f"w{n}.json").read_text("utf-8"))
    ziel = AUS / "inputs" / f"Input_W{n}.html"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(input_html(w), encoding="utf-8")
    # Prüfung: jede Folie und jeder Klickschritt passt auf 1280×800 und 1024×768
    for vw, vh in ((1280, 800), (1024, 768)):
        pg = b.br.new_page(viewport={"width": vw, "height": vh})
        pg.goto(ziel.resolve().as_uri())
        pg.evaluate("document.fonts.ready")
        for _ in range(40):
            ueber = pg.evaluate("(()=>{const f=document.querySelector('.folie.an');return f.scrollHeight>f.clientHeight+2||f.scrollWidth>f.clientWidth+2})()")
            if ueber:
                b.fehler.append("Input W%d: Überlauf bei %dx%d auf Folie %s" % (n, vw, vh, pg.evaluate("f+1")))
                break
            pg.keyboard.press("ArrowRight")
        pg.close()
    b.bericht.append("%-40s Folien geprüft (1280×800, 1024×768)" % f"inputs/Input_W{n}.html")
    b.mach(skript_html(w), AUS / "inputs" / f"Skript_W{n}_A4.pdf", f"Skript W{n}", 12, 2)


def bau_lesestrang(b: Bau, n: int):
    lw = next(x for x in json.loads((IN / "lesestrang.json").read_text("utf-8"))["wochen"] if x["woche"] == n)
    b.mach(lesebogen_html(lw), AUS / "lesestrang" / f"Lesebogen_W{n}_A4.pdf", f"Lesebogen W{n}", 14, 1)


def bau_lerntheke(b: Bau):
    teile = [b.mach(karte_html(k), AUS / "lerntheke" / f"Strategie_{k['id']}_A5.pdf", "Strategiekarte", 14, 1) for k in STRAT.values()]
    verbinde(teile, AUS / "lerntheke" / "Strategiekarten_alle_A5.pdf")


def bau_raum(b: Bau):
    b.mach(plakat_html(), AUS / "raum" / "Plakat_Wo_stehe_ich_A3.pdf", "Plakat", 14, 1)
    zs = [b.mach(zone_html(z), AUS / "raum" / f"_zone_{z['name']}.pdf", "Zone", 14, 1) for z in RAUM["zonen"]]
    verbinde(zs, AUS / "raum" / "Zonenschilder_A4quer.pdf")
    for z in zs:
        z.unlink()
    b.mach(satzstarter_html(), AUS / "raum" / "Karte_Laut_denken_A5.pdf", "Karte", 14, 1)
    b.mach(lernweg_html(), AUS / "raum" / "Lernweg_F2_A4.pdf", "Lernweg", 12, 1)


# ------------------------------------------------------------ Druckpaket mit Druckanleitung
# Druckteile je Etappe: (Ordner, Datei relativ zu ausgabe/f2, Format, Anzahl, Hinweis)
A5H = "A4 → A5 verkleinert, beidseitig, geheftet"


def druck_liste(n: int) -> list[tuple]:
    e = json.loads((IN / f"etappe{n}.json").read_text("utf-8"))
    t = TEXTDB[e["text"]]["titel"]
    reihen = []
    if n == 1:
        reihen.append(("1_Kinder", "raum/Lernweg_F2_A4.pdf", "A4, einseitig", "je Kind 1", "zu Beginn der Reihe; bleibt in der Mappe"))
    inhalt = "Deckblatt, „%s“, zu zweit%s, allein" % (t, " (mit Legeplan und Satzstreifen)" if e["gemeinsam"].get("legeplan") else
                                                      " (mit Arbeitsseite)" if e["gemeinsam"].get("arbeitsseite") else "")
    hinweis = "Reihenfolge: " + inhalt + "."
    if e.get("extern"):
        hinweis += " Das Quiz der Kollegin hat zwei Exemplare auf einer Seite: halbieren, je Kind eine Hälfte."
    if e["gemeinsam"].get("streifen"):
        hinweis += " Schere und Kleber bereitlegen."
    reihen += [
        ("1_Kinder", f"etappe{n}/Etappenpaket_{n}_A4.pdf", A5H, "je Kind 1", hinweis),
        ("2_Nachweise", f"etappe{n}/GN{n}_A_A4.pdf", "A4, beidseitig", "je Kind 1", "erst ausgeben, wenn das Kind die Schritte im Paket geschafft hat"),
        ("2_Nachweise", f"etappe{n}/GN{n}_B_A4.pdf", "A4, beidseitig", "etwa ⅓ der Kinder", "Wiederholung nach dem Üben"),
        ("3_Foerder", f"etappe{n}/foerder/Foerderpaket_{n}_A4.pdf", "A4 → A5 verkleinert, beidseitig", "je F-Kind 1", "Lösungsstreifen unten am Blatt umknicken"),
        ("3_Foerder", f"etappe{n}/foerder/GN{n}F_A_A4.pdf", "A4, beidseitig", "je F-Kind 1", ""),
        ("3_Foerder", f"etappe{n}/foerder/GN{n}F_B_A4.pdf", "A4, beidseitig", "nach Bedarf", ""),
        ("4_Lesestrang", f"lesestrang/Lesebogen_W{n}_A4.pdf", "A4, einseitig", "je Lesetandem 1", "Sprach-Doppelstunde in Woche %d; „%s“ liegt im Etappenpaket" % (n, t)),
    ]
    reihen += [("5_Lerntheke", f"lerntheke/Strategie_{k['id']}_A5.pdf", "A5 quer, einseitig, laminieren", "2–3 je Raum",
                "neue Strategiekarte: „%s“" % k["titel"]) for k in STRAT.values() if k.get("etappe", 1) == n]
    if n == 1:
        reihen += [("6_Raum", "raum/Plakat_Wo_stehe_ich_A3.pdf", "A3 quer (oder 2 × A4 zusammenkleben)", "je Raum 1", "Wäscheklammern mit Namen; Klassenübersicht und Partnersuche zugleich"),
                   ("6_Raum", "raum/Zonenschilder_A4quer.pdf", "A4 quer, einseitig, laminieren", "je Raum 1 Satz", "Stillraum · Denkraum · Flur"),
                   ("6_Raum", "raum/Karte_Laut_denken_A5.pdf", "A5 quer, laminieren", "je Tisch 1", "")]
    reihen += [("7_Lehrkraft", f"etappe{n}/GN{n}_Erwartungshorizont_A4.pdf", "A4", "1", ""),
               ("7_Lehrkraft", f"inputs/Skript_W{n}_A4.pdf", "A4", "1", "Input W%d (höchstens 10 Minuten) in der ersten Deutsch-Doppelstunde der Woche" % n)]
    return reihen


DRUCK_EXTERN = {1: ["Merkblatt Märchenmerkmale (Kollegin) – Lerntheke, A5"],
                2: ["Merkblatt Märchen-Spannungsbogen und Spannungsbogen universell (Kollegin) – Lerntheke",
                    "Verbliste (Kollegin) – Lerntheke; folgt noch"],
                3: ["Märchen-Lückentext (Kollegin): Wortspeicher als Lerntheken-Karte, A5",
                    "Rechtschreib-Check (Kollegin) – Lerntheke, für die wörtliche Rede; folgt noch"]}


def druckanleitung_html(inv: list[tuple], n: int, start: int = 1) -> str:
    rows, seite = [], start
    for o, d, f, a, h, sz in inv:
        rows.append("<tr><td style='text-align:center'><b>%s</b></td><td style='word-break:break-all'>%s<br><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            "%d–%d" % (seite, seite + sz - 1) if sz > 1 else str(seite), esc(o), esc(Path(d).name), esc(f), esc(a), esc(h)))
        seite += sz
    raum = ("<li>Plakat aufhängen, Klammern mit Namen beschriften (Klammer startet bei „Start“).</li>"
            "<li>Zonenschilder an Stillraum, Denkraum und Flur; Karte „Laut denken“ auf die Tische.</li>") if n == 1 else ""
    extern = "".join("<li>%s</li>" % esc(x) for x in DRUCK_EXTERN.get(n, [])) or "<li>–</li>"
    h2 = "<h2 style='font-size:16pt;margin:4mm 0 1.5mm'>%s</h2>"
    return doc(GN_CSS + "body{font-size:12.5pt}table{font-size:12.5pt}td,th{padding:1.4mm 2mm}", "".join([
        "<div class=meta>Lehrkraft · Fassung 2 · Etappe %d</div><h1>Druckanleitung</h1>" % n,
        "<div class=hinweis><b>So druckst du:</b> Etappenpakete und Förderpakete sind A4 gesetzt und werden <b>auf A5 verkleinert</b> gedruckt "
        "(2 Seiten pro Blatt, beidseitig, Heftung). Drucke dafür nur die angegebenen <b>Seiten im PDF</b>. Nachweise, Lesebogen und Lehrkraft-Seiten "
        "in <b>A4-Originalgröße</b>. Karten und Schilder laminieren. Alles ist für Graustufen gemacht.</div>",
        "<table style='table-layout:fixed'><tr><th style='width:20mm'>Seiten im PDF</th><th style='width:48mm'>Teil</th><th style='width:34mm'>Format</th>"
        "<th style='width:24mm'>Anzahl</th><th>Hinweis</th></tr>%s</table>" % "".join(rows),
        h2 % "Digital", "<p><b>Input_W%d.html</b>: Beamer (im Browser öffnen, F = Vollbild, Klick = nächster Gedanke)</p>" % n,
        h2 % "Vom Material der Kollegin (nicht im Paket, von ihren Originalen drucken)", "<ul style='margin-left:6mm'>%s</ul>" % extern,
        h2 % "Vorbereitung im Raum", "<ul style='margin-left:6mm'>%s<li>Lerntheke: neue Strategiekarten und Merkblätter der Kollegin dazulegen.</li>"
        "<li>Gelingensnachweise GN%d A/B bei der Lehrkraft bereithalten, nicht ins Paket.</li></ul>" % (raum, n)]))


def bau_druck(b: Bau, n: int):
    inv, fehlt = [], []
    for o, d, f, a, h in druck_liste(n):
        p = AUS / d
        if not p.exists():
            fehlt.append(d)
            continue
        inv.append((o, d, f, a, h, len(fitz.open(p))))
    if fehlt:
        b.fehler.append("Druckpaket %d: fehlt %s" % (n, ", ".join(fehlt)))
        return
    anl = AUS / f"Druckanleitung_F2_Etappe{n}_A4.pdf"
    n_anl = 0
    for _ in range(3):  # Seitenangaben hängen von der Länge der Anleitung ab
        b.mach(druckanleitung_html(inv, n, n_anl + 1), anl, "Druckanleitung", 12)
        neu = len(fitz.open(anl))
        if neu == n_anl:
            break
        n_anl = neu
        b.bericht.pop()
    gesamt = AUS / f"Gesamtpaket_F2_Etappe{n}.pdf"
    seiten = verbinde([anl] + [AUS / d for _, d, *_ in inv], gesamt)
    soll = n_anl + sum(x[5] for x in inv)
    if seiten != soll:
        b.fehler.append("Gesamt-PDF %d: %d Seiten statt %d" % (n, seiten, soll))
    b.bericht.append("%-40s %d S. (Anleitung %d S. + %d Teile), %.1f MB" % (gesamt.name, seiten, n_anl, len(inv), gesamt.stat().st_size / 1e6))


def main(argv: list[str]) -> int:
    was = argv[0] if argv else "alles"
    b = Bau()
    if was in ("etappe", "alles"):
        for n in ([int(argv[1])] if was == "etappe" else [p.stem[-1] for p in sorted(IN.glob("etappe*.json"))]):
            bau_etappe(b, int(n))
    if was in ("input", "alles"):
        for n in ([int(argv[1])] if was == "input" else [int(p.stem[1:]) for p in sorted((IN / "inputs").glob("w*.json"))]):
            bau_input(b, n)
    if was in ("lesestrang", "alles"):
        wochen = [x["woche"] for x in json.loads((IN / "lesestrang.json").read_text("utf-8"))["wochen"]]
        for n in ([int(argv[1])] if was == "lesestrang" else wochen):
            bau_lesestrang(b, n)
    if was in ("lerntheke", "alles"):
        bau_lerntheke(b)
    if was in ("raum", "alles"):
        bau_raum(b)
    if was in ("druck", "alles"):
        for n in ([int(argv[1])] if was == "druck" and len(argv) > 1 else [int(p.stem[-1]) for p in sorted(IN.glob("etappe*.json"))]):
            bau_druck(b, n)
    return b.ende()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
