#!/usr/bin/env python3
"""Fassung 4 · Nach der Abgabe (ohne Note): Schreibkonferenz, Überarbeitungsplan, Wahlhilfe, Projekte P1–P3, Reinschrift.

    python3 tools/build_f4_nachabgabe.py

Inhalte: inhalt/f4/nach_der_abgabe.json. Ausgabe: ausgabe/f4/nach_der_abgabe/ (im Repo, keine fremden Texte).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_f4 as f4  # noqa: E402
from build_material import GN_CSS, doc, esc, md, verbinde  # noqa: E402
from build_wahlzeit import reinschrift_html  # noqa: E402

f2 = f4.f2
sym, kopf, F2_CSS = f2.sym, f2.kopf, f2.F2_CSS
N = json.loads((f4.ROOT / "inhalt" / "f4" / "nach_der_abgabe.json").read_text("utf-8"))
SK = N["schreibkonferenz"]
AUS = f4.AUS / "nach_der_abgabe"
LINIE = "<div class=linie style='height:9mm'></div>"
CSS = F2_CSS + ".kasten:last-child,div:last-child{margin-bottom:0}"


def ablauf_html() -> str:
    rollen = "".join("<tr><td class=i>%s</td><td style='width:42mm'><b>%s</b></td><td>%s</td></tr>" % (sym(i, 9), esc(r), md(t)) for r, i, t in SK["rollen"])
    schritte = "".join("<li><span class=n>%d</span><span><b>%s:</b> %s</span></li>" % (n, esc(a), md(b)) for n, (a, b) in enumerate(SK["schritte"], 1))
    starter = "".join("<div style='margin:.6mm 0'><b style='display:inline'>%s:</b> %s</div>" % (esc(a), esc(b)) for a, b in SK["starter"])
    return doc(CSS + "table.st td{padding:1.4mm 2.5mm;font-size:14pt;line-height:1.25}.schritte li{margin-bottom:.8mm;font-size:14pt;line-height:1.25}.auf2{padding:2mm 3.5mm;margin-bottom:2.5mm}.hilft{margin-bottom:2mm}.merke{font-size:14pt;margin:0}", (
        kopf("Nach der Abgabe · ohne Note · zu dritt", "Schreibkonferenz", "zwei")
        + "<div class=hilft>Ihr helft euch gegenseitig, eure Märchen noch besser zu machen. Jedes Kind ist einmal Autorenkind. "
          "Dann wechseln die Rollen – <b>drei Runden</b>, etwa 15 Minuten pro Text.</div>"
        + "<table class=st style='margin-bottom:3mm'>%s</table>" % rollen
        + "<div class=auf2><h2>So geht eine Runde</h2><ol class=schritte>%s</ol></div>" % schritte
        + "<div class=starter><b>Satzanfänge</b>%s</div>" % starter
        + "<div class=merke>%s</div>" % "<br>".join("● " + md(r) for r in SK["regeln"])))


def karte_teil(titel: str, icon: str, items) -> str:
    """items: Texte oder [K, Text]; das Kriterium steht nur in den Daten, nicht auf der Karte (Platz)."""
    texte = [i[1] if isinstance(i, list) else i for i in items]
    rows = "".join("<tr><td>%s</td><td class=k>☐</td><td class=k>☐</td></tr>" % md(t) for t in texte)
    kopfz = "<tr><td></td><td class=k style='font-size:14pt'><b>gelingt</b></td><td class=k style='font-size:14pt'><b>noch nicht</b></td></tr>"
    return ("<div class=auf2><h2><span>%s %s</span><small>Name: ________________</small></h2>"
            "<table class='st eng'>%s%s</table>"
            "<div style='font-size:14pt;margin-top:1.5mm'><b>Das gefällt mir:</b></div>%s"
            "<div style='font-size:14pt;margin-top:1mm'><b>Mein Tipp</b> (mit Stelle):</div>%s</div>") % (
        sym(icon, 7), esc(titel), kopfz, rows, LINIE, LINIE)


def karte_html(leicht: bool) -> str:
    css = CSS + "table.st.eng td{padding:1mm 2mm;font-size:14pt}table.st td.k{width:27mm;font-size:17pt;padding:.4mm;white-space:nowrap}.auf2{padding:2mm 3.5mm;margin-bottom:2.5mm}.auf2 h2{margin-bottom:1mm}"
    if leicht:
        teile = (karte_teil("Zuhörkind 1 · Inhalt", "fernglas", SK["karte_leicht_inhalt"])
                 + karte_teil("Zuhörkind 2 · Sprache", "auge", SK["karte_leicht_sprache"])
                 + "<div class=hilft><b>Satzanfänge:</b> Mir gefällt, dass … · Du könntest …</div>")
    else:
        teile = (karte_teil("Zuhörkind 1 · Inhalt", "fernglas", SK["karte_inhalt"])
                 + karte_teil("Zuhörkind 2 · Sprache", "auge", SK["karte_sprache"]))
    return doc(css, kopf("Schreibkonferenz · %s" % ("Feedbackkarte leicht" if leicht else "Feedbackkarte"), "Feedback für ein Märchen", "haken")
               + "<div style='font-size:14pt;margin-bottom:2mm'>Text von: ____________________ &nbsp; Anfang: ____________________</div>" + teile)


def plan_html() -> str:
    schritte = "".join("<li><span class=n>%d</span><span><b>%s:</b> %s</span></li>" % (n, esc(a), md(b)) for n, (a, b) in enumerate(SK["plan_schritte"], 1))
    tab = "".join("<tr><td style='height:15mm'></td><td style='width:30mm'></td><td style='width:15mm' class=k>☐</td></tr>" for _ in range(3))
    hilfen = "".join("<tr><td style='width:12mm'><b>%s</b></td><td style='width:42mm'>%s</td><td>%s</td></tr>" % (k, esc(n), esc(h)) for k, n, h in SK["hilfen"])
    return doc(CSS + "table.st td{padding:1.3mm 2.5mm;font-size:14pt;line-height:1.25}table.st td.k{font-size:18pt;text-align:center}.schritte li{margin-bottom:1.4mm}", (
        kopf("Nach der Abgabe · ohne Note", "Mein Überarbeitungsplan", "plan",
             "Kopie deines Rohentwurfs · Feedbackkarte · grüner Stift · Märchen-Check")
        + "<ol class=schritte style='font-size:14.5pt'>%s</ol>" % schritte
        + "<table class=st style='margin:2mm 0 3mm'><tr><td><b>Mein Tipp: Das verbessere ich</b></td><td><b>Stelle</b></td><td class=k style='font-size:14pt'><b>fertig</b></td></tr>%s</table>" % tab
        + "<div class=auf2><h2>Das hilft dir</h2><table class='st eng'>%s</table></div>" % hilfen))


def wahlhilfe_html() -> str:
    rows = "".join("<tr><td style='width:44mm'><b>%s</b> %s</td><td class=k>☐</td><td>%s</td></tr>" % (k, esc(t), md(u)) for k, t, u in N["wahlhilfe"])
    return doc(CSS + "table.st td{padding:1.6mm 2.5mm;font-size:14pt;line-height:1.28;vertical-align:top}table.st td.k{width:14mm;font-size:18pt;text-align:center}", (
        kopf("Nach der Abgabe · Wahlzeit", "Was übe ich jetzt?", "lupe", N["wahlhilfe_brauchst"])
        + "<div class=hilft><b>Zuerst:</b> %s</div>" % md(N["wahlhilfe_zuerst"])
        + "<table class=st><tr><td><b>Kriterium</b></td><td class=k style='font-size:14pt'><b>offen</b></td><td><b>So übst du</b></td></tr>%s</table>" % rows
        + "<div class=hilft style='margin-top:3mm'><b>Danach:</b> %s</div>" % md(N["wahlhilfe_danach"])))


def projekt_html(p: dict) -> str:
    li = "".join("<li><span class=n>%d</span><span><b>%s:</b> %s</span></li>" % (n, esc(a), md(b)) for n, (a, b) in enumerate(p["schritte"], 1))
    return doc(CSS + ".schritte li{margin-bottom:1.8mm}", (
        kopf("Wahlzeit · Projekt %s · freiwillig" % p["nr"], p["titel"], p["icon"], p["brauchst"])
        + "<div style='font-size:15pt;margin-bottom:3mm'>%s</div>" % md(p["einleitung"])
        + "<div class=auf2><h2>So gehst du vor</h2><ol class=schritte>%s</ol></div>" % li
        + "<div class=auf2><h2>Gelingt, wenn</h2>%s</div>" % "".join("<div style='margin:1mm 0'>☐ %s</div>" % md(g) for g in p["gelingt"])
        + ("<div class=hilft><b>Noch mehr:</b> %s</div>" % md(p["erweiterung"]) if p.get("erweiterung") else "")))


def lehrkraft_html() -> str:
    rows = "".join("<tr><td style='width:28mm'><b>%s</b></td><td>%s</td></tr>" % (esc(a), md(b)) for a, b in SK["lehrkraft"])
    druck = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(map(esc, d)) for d in SK["druck"])
    return doc(GN_CSS + "body{font-size:12pt}table{font-size:12pt;width:100%;border-collapse:collapse}td{border:1pt solid #111;padding:1.4mm 2mm;vertical-align:top}", (
        "<div class=meta>Lehrkraft · Fassung 4</div><h1>Nach der Abgabe: Schreibkonferenz und Wahlzeit</h1>"
        "<table style='margin-bottom:4mm'>%s</table><h2 style='font-size:14pt;margin-bottom:1.5mm'>Drucken (A4 gesetzt, auf A5 verkleinert; Reinschrift A4)</h2>"
        "<table>%s</table>") % (rows, druck))


def main() -> int:
    AUS.mkdir(parents=True, exist_ok=True)
    b = f2.Bau()
    teile = [
        b.mach(lehrkraft_html(), AUS / "NA_0_Lehrkraft_A4.pdf", "Lehrkraft", 12, 1),
        b.mach(ablauf_html(), AUS / "NA_1_Schreibkonferenz_Ablauf_A4.pdf", "Schreibkonferenz", 14, 1),
        b.mach(karte_html(False), AUS / "NA_2_Feedbackkarte_A4.pdf", "Schreibkonferenz", 14, 1),
        b.mach(karte_html(True), AUS / "NA_3_Feedbackkarte_leicht_A4.pdf", "Schreibkonferenz", 14, 1),
        b.mach(plan_html(), AUS / "NA_4_Ueberarbeitungsplan_A4.pdf", "Überarbeiten", 14, 1),
        b.mach(wahlhilfe_html(), AUS / "NA_5_Wahlhilfe_A4.pdf", "Wahlzeit", 14, 1),
    ]
    pr = [b.mach(projekt_html(p), AUS / ("NA_6_" + p["datei"]), "Projekt " + p["nr"], 14, 1) for p in N["projekte"]]
    rein = b.mach(reinschrift_html(), AUS / "NA_7_Reinschrift_Maerchenbuch_A4.pdf", "Märchenbuch", 14, 2)
    s = verbinde(teile + pr + [rein], AUS / "Paket_5_Nach_der_Abgabe.pdf")
    b.bericht.append("%-40s %d S." % ("nach_der_abgabe/Paket_5_Nach_der_Abgabe.pdf", s))
    f4.pruefe_seiten(b)
    return b.ende()


if __name__ == "__main__":
    sys.exit(main())
