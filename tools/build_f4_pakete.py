#!/usr/bin/env python3
"""Fassung 4 · Material der Kollegin im HBG-Design und vier vollständige Materialpakete.

    python3 tools/build_f4_pakete.py            Kollegin-Material setzen und Pakete bauen (vorher build_f4.py alles)

Quelle der Inhalte: extern/kollegin.json (nicht im Repo, enthält fremde Texte).
Ausgabe: ausgabe/f4/kollegin/ und ausgabe/f4/pakete/Paket_1–4 (beides nicht im Repo).
Paket 1 Lesematerial Sprache · Paket 2 Etappe 1 · Paket 3 Etappe 2 · Paket 4 Klassenarbeiten.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pymupdf as fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_f4 as f4  # noqa: E402
from build_material import GN_CSS, doc, esc, md, verbinde  # noqa: E402

f2 = f4.f2
sym, kopf, F2_CSS = f2.sym, f2.kopf, f2.F2_CSS
KOL = json.loads((f4.ROOT / "extern" / "kollegin.json").read_text("utf-8"))
AUS = f4.AUS
KAUS = AUS / "kollegin"
PAUS = AUS / "pakete"
LINIE = "<div class=linie></div>"


def mdb(t: str) -> str:
    """md() mit erlaubtem Zeilenumbruch <br>."""
    return md(t).replace("&lt;br&gt;", "<br>")
KOMPAKT = ".kasten:last-child,div:last-child{margin-bottom:0}table.st td,table.st th{padding:.9mm 1.8mm;line-height:1.22}.auf2{padding:2mm 3mm}.auf2 h3{margin-bottom:.5mm}.hilft{margin-bottom:2mm}.kopf2{margin-bottom:2mm}"


text_pdf = f4.text_pdf


# ------------------------------------------------------------ Paket 1: Lesen in Sprache
def lese_deck_html() -> str:
    wahl = "".join("<div class=anfang style='margin:0 0 1.2mm;padding:1.2mm 3mm'><b>☐ &nbsp;%s &nbsp; %s</b>%s</div>"
                   % (L["sterne"], esc(L["titel"]), " – %s" % esc(L["untertitel"]) if L.get("untertitel") else "") for L in KOL["lese"])
    auftrag = "".join("<li style='margin:1mm 0'>%s</li>" % esc(s) for s in KOL["lese_auftrag"])
    return doc(F2_CSS + KOMPAKT, kopf("Sprache · Lesen", "Märchen lesen", "lesen")
               + "<div class=hilft>Freitags in Sprache liest du Märchen – im Tandem oder allein, in deinem Tempo. "
               "Such dir ein Märchen aus. Mit diesem Märchen arbeitest du später auch in Deutsch.</div>"
               + "<div style='font-size:16pt;font-weight:700;margin:3mm 0 1.5mm'>Wähle dein Märchen</div>" + wahl
               + "<div class=anfang style='margin:0 0 1.2mm;padding:1.2mm 3mm'><b>☐ &nbsp;ein Buch aus der Lesekiste:</b> ______________________________</div>"
               + "<p style='font-size:13.5pt'>★ kurz und gut zu verstehen · ★★ länger · ★★★ lang, viele Figuren</p>"
               + "<div style='font-size:16pt;font-weight:700;margin:3mm 0 1.5mm'>%s So lest ihr</div><ol style='margin-left:8mm;font-size:15pt'>%s</ol>" % (sym("zwei", 7), auftrag)
               + "<div class=hilft style='margin-top:3mm'>Wörter mit einer kleinen Zahl werden unten auf der Seite erklärt. Die Zahlen am Rand zählen die Zeilen. "
               "So findest du Antworten schnell wieder: <b>(Z. 5)</b>.</div>"
               + "<div style='font-size:16pt;margin-top:3mm'><b>Mein Märchen für Deutsch:</b> ______________________________</div>")


def lese_aufgaben_html(L: dict) -> str:
    teile = [kopf("Sprache · Leseübung %d · %s" % (L["n"], L["sterne"]), "Aufgaben zu „%s“" % L["titel"], "lesen"),
             "<div style='font-size:14.5pt;margin-bottom:1mm'>☐ im Tandem lesen &nbsp; ☐ noch einmal leise lesen &nbsp; ☐ nacherzählen &nbsp; ☐ Fragen beantworten</div>",
             "<div style='font-size:14pt;margin-bottom:2.5mm'><b>(Z.)</b> heißt: Schreib die Zeile dazu, zum Beispiel <b>(Z. 5)</b>.</div>"]
    for i, q in enumerate(L["fragen"], 1):
        felder = "".join("<div style='display:flex;gap:2mm;margin-top:2mm;font-size:15pt'><span style='white-space:nowrap'>%s</span>"
                         "<span style='flex:1;border-bottom:1pt solid #111'></span></div>" % esc(f) for f in q.get("felder", []))
        teile.append("<div style='margin:0 0 2.5mm'><div style='font-size:15pt'><b>%d.</b> %s%s</div>%s%s</div>" % (
            i, esc(q["text"]), " <b>(Z.)</b>" if q.get("zeile") else "", felder, LINIE * q.get("linien", 1)))
    zs = "".join("<div style='font-size:15pt;margin-top:1mm'>%s</div>%s%s" % (
        esc(z["text"]), LINIE * z.get("linien", 0),
        "<div style='border:1.2pt solid #111;border-radius:2mm;height:%dmm;margin-top:2mm'></div>" % z["kasten"] if z.get("kasten") else "")
        for z in L.get("zusatz", []))
    if zs:
        teile.append("%s<div class='kasten frei'><span class=etikett>%s FREIWILLIG</span>%s</div>" % (
            "<div style='break-before:page'></div>" if L.get("zusatz_seite") else "", sym("plus", 6), zs))
    return doc(F2_CSS + KOMPAKT, "".join(teile))


def verben_html() -> tuple[str, str]:
    v = KOL["verben"]
    arten = "".join("<div class=auf2 style='flex:1'><h3 style='font-size:16pt'>%s</h3><p style='font-size:14pt'>%s</p><p style='font-size:15pt;margin-top:1.5mm'><b>%s</b></p>%s</div>"
                    % (esc(t), md(e), esc(bsp), "".join("<div style='font-size:15pt'>%s</div>" % md(f) for f in formen)) for t, e, bsp, formen in v["arten"])
    s1 = doc(F2_CSS + KOMPAKT, kopf("Märchenverben", "Märchenverben im Präteritum", "plan") + "<div class=hilft>%s</div>" % md(v["einfuehrung"])
             + "<div style='display:flex;gap:2.5mm'>%s</div>" % arten + "<div class=hilft style='margin-top:2mm'><b>Tipp:</b> %s</div>" % esc(v["tipp"]))
    kopfz = "".join("<th>%s</th>" % x for x in ["Verb", "ich", "du", "er / sie / es", "wir", "ihr", "sie"])
    seiten = []
    for t in v["tabellen"]:
        rows = "".join("<tr>%s</tr>" % "".join("<td%s>%s</td>" % (" style='font-weight:700'" if i == 0 else "", esc(x)) for i, x in enumerate(z)) for z in t["verben"])
        seiten.append(kopf("Märchenverben", t["titel"], "plan") + ("<div class=hilft>%s</div>" % esc(t["hinweis"]) if t["hinweis"] else "")
                      + "<table class=st style='font-size:14pt;table-layout:fixed'><tr>%s</tr>%s</table>" % (kopfz, rows))
    # gemischte Verben und sein/haben/werden passen auf eine Seite
    seiten[-2] = seiten[-2] + "<div style='height:4mm'></div>" + seiten[-1].replace("<div class=kopf2>", "<div class=kopf2 style='border:none'>", 1)
    seiten.pop()
    quer = F2_CSS + KOMPAKT + "@page{size:A4 landscape}th{font-size:14pt;text-align:left}"
    return s1, doc(quer, "<div style='break-before:page'></div>".join(seiten))


def hilfe_seite_html(s: dict) -> str:
    teile = [kopf("Märchen-Hilfe · Seite %d" % s["nr"], s["titel"], "buch")]
    if s.get("intro"):
        teile.append("<div class=hilft>%s</div>" % md(s["intro"]))
    for bl in s["bloecke"]:
        if bl["art"] == "inhalt":
            teile.append("<table class=st style='font-size:14pt'>%s</table>" % "".join(
                "<tr><td style='width:12mm;text-align:center;font-weight:700;font-size:17pt'>%s</td><td><b>%s</b> – %s</td></tr>" % (n, esc(t), esc(u)) for n, t, u in bl["zeilen"]))
        elif bl["art"] == "gruppe":
            teile.append("<div class=auf2 style='margin-bottom:2mm'><h3 style='font-size:15.5pt'>%s</h3><div style='font-size:14.5pt'>%s</div></div>" % (esc(bl["titel"]), mdb(bl["text"])))
        elif bl["art"] == "tabelle":
            kz = "".join("<th>%s</th>" % esc(k) for k in bl["kopf"])
            rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % md(c) for c in z) for z in bl["zeilen"])
            teile.append("<table class=st style='font-size:14pt;margin-bottom:2mm'><tr>%s</tr>%s</table>" % (kz, rows))
        elif bl["art"] == "spalten":
            sp = "".join("<div style='flex:1'><div style='font-weight:700;font-size:15pt;border-bottom:1.2pt solid #111;margin-bottom:1mm'>%s</div>%s</div>"
                         % (esc(c[0]), "".join("<div style='font-size:14pt;line-height:1.35'>%s</div>" % md(x) for x in c[1:])) for c in bl["spalten"])
            teile.append("<div style='display:flex;gap:5mm;margin-bottom:3mm'>%s</div>" % sp)
    return doc(F2_CSS + KOMPAKT + "th{text-align:left;font-size:14pt}", "".join(teile))


# ------------------------------------------------------------ Paket 2 und 3: Merkblätter, Quiz, Rap, Schreibplan, Lückentext
def merkmale_html() -> str:
    box = lambda m: ("<div class=auf2 style='margin:0'><h3 style='font-size:15pt;display:flex;gap:2mm;align-items:center'>%s %s</h3>%s</div>"  # noqa: E731
                     % (sym(m["symbol"], 6.5), esc(m["bereich"]), "".join("<div style='font-size:13pt;line-height:1.25;margin-top:.8mm'><b>%s:</b> %s</div>" % (esc(a), esc(b_)) for a, b_ in m["punkte"])))
    return doc(F2_CSS + KOMPAKT, kopf("Etappe 1 · Merkblatt", "Märchenmerkmale", "lupe")
               + "<div style='display:grid;grid-template-columns:1fr 1fr;gap:2mm'>%s</div>" % "".join(box(m) for m in KOL["merkmale"]))


def quiz_html() -> str:
    rows = []
    for m in KOL["merkmale"]:
        n = len(m["punkte"])
        for i in range(n):
            rows.append("<tr>%s<td style='height:14mm;vertical-align:top'><span style='font-size:12pt'>Merkmal:</span></td>"
                        "<td style='vertical-align:top'><span style='font-size:12pt'>Beispiel aus meinem Märchen (Z.):</span></td></tr>"
                        % ("<td rowspan=%d style='width:30mm;vertical-align:top'><b>%s</b></td>" % (n, esc(m["bereich"])) if i == 0 else ""))
    return doc(F2_CSS, kopf("Etappe 1 · Quiz", "Quiz Märchenmerkmale", "stern")
               + "<div style='font-size:15pt;margin-bottom:2mm'>Name: ______________ &nbsp; Mein Märchen: ______________________</div>"
               + "<div class=hilft>Finde in deinem Märchen zu jedem Bereich ein Merkmal und ein Beispiel. Das Merkblatt hilft dir. Schreibe die Zeile dazu.</div>"
               + "<table class=st style='table-layout:fixed;font-size:13pt'>%s</table>" % "".join(rows))


def bogen_html() -> str:
    rows = "".join("<tr><td style='text-align:center;font-size:20pt;font-weight:700'>%s</td><td><b>%s</b> · <i>%s</i></td>"
                   "<td>%s</td><td>%s</td><td>%s</td></tr>" % (b_, esc(s), esc(w), esc(f), esc(m), esc(r)) for b_, s, w, f, m, r in KOL["bogen"])
    return doc(F2_CSS + KOMPAKT, kopf("Etappe 2 · Merkblatt", "Märchen-Spannungsbogen", "bogen") + f2.bogen_svg()
               + "<div class=hilft style='margin-top:-1mm'><b>In einem Satz:</b> %s &nbsp; ↗ Die Spannung steigt bis zum Höhepunkt, dann fällt sie ↘</div>" % esc(KOL["bogen_satz"])
               + "<table class=st style='font-size:13pt;table-layout:fixed'><tr><th style='width:10mm'></th><th style='width:33mm'>Schritt</th><th>Frage</th><th>im Märchen</th><th>Figuren und Dinge</th></tr>%s</table>" % rows
               )


def rap_html() -> str:
    r = KOL["rap"]
    refrain = lambda z: ("<div class=anfang style='margin:0 0 2mm;grid-column:1/3'><b>Refrain%s</b><div style='display:flex;gap:6mm;font-size:14.5pt'>"  # noqa: E731
                         "<div>%s</div><div>%s</div></div></div>" % (z, "<br>".join(esc(x) for x in r["refrain"][:2]), "<br>".join(esc(x) for x in r["refrain"][2:])))
    st = [refrain("")]
    for i, s_ in enumerate(r["strophen"]):
        st.append("<div style='border:1.4pt solid #111;border-radius:2mm;padding:1.8mm 3mm;break-inside:avoid'>"
                  "<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:2mm'><b style='font-size:14.5pt'>%s</b>"
                  "<span style='font-size:20pt;font-weight:700;white-space:nowrap'>%s</span></div>"
                  "<div style='font-size:12.5pt;font-style:italic;border-bottom:1pt dashed #111;margin-bottom:1mm'>%s</div>"
                  "<div style='font-size:14pt;line-height:1.28'>%s</div></div>"
                  % (esc(s_["titel"]), esc(s_["bogen"]), esc(s_["marke"]), "<br>".join(esc(z) for z in s_["zeilen"])))
        if i == 3:
            st.append(refrain(" (klatsch, klatsch)"))
    return doc(F2_CSS + KOMPAKT, kopf("Etappe 2 · Märchenrap", "Märchenrap und Spannungsbogen", "bogen")
               + "<div class=hilft>Sprecht den Rap. Achtet auf die Buchstaben: So ist ein Märchen aufgebaut.</div>"
               + "<div style='display:grid;grid-template-columns:1fr 1fr;gap:2mm'>%s</div>" % "".join(st))


def schreibplan_html() -> str:
    rows = "".join("<tr><td style='width:13mm;text-align:center;font-size:24pt;font-weight:700'>%s</td><td style='width:64mm'><b>%s</b> · <i>%s</i><br>%s<br>"
                   "<span style='font-size:12.5pt'>%s · %s</span></td><td style='height:31mm'></td></tr>" % (b_, esc(s), esc(w), esc(f), esc(m), esc(r))
                   for b_, s, w, f, m, r in KOL["bogen"])
    return doc(F2_CSS, kopf("Etappe 2 · Schreibplan ★★", "Mein Märchen-Schreibplan", "plan")
               + "<div style='font-size:15pt;margin-bottom:2mm'>Name: ______________ &nbsp; Mein Märchen: ______________________</div>"
               + "<div class=hilft>Trage dein Märchen in Stichwörtern ein. Das Merkblatt Spannungsbogen hilft dir.</div>"
               + "<table class=st style='font-size:14pt;table-layout:fixed'>%s</table>" % rows)


def lueckentext_html(meta: str) -> str:
    rows = "".join("<div style='display:flex;gap:3mm;margin-top:2mm;break-inside:avoid'><div style='width:13mm;text-align:center'><div style='font-size:22pt;font-weight:700'>%s</div>"
                   "<div style='font-size:11.5pt'>%s</div></div><div style='flex:1'>%s</div></div>"
                   % (b_, esc(w), "".join("<div style='font-size:15pt;margin-top:1mm'>%s …</div>%s" % (esc(s), LINIE * 2) for s in starts))
                   for b_, _, w, starts in KOL["lueckentext"])
    ws = "".join("<div style='margin-top:1.5mm'><b>%s:</b> %s</div>" % (esc(t), esc(x)) for t, x in KOL["wortspeicher"])
    return doc(F2_CSS, kopf(meta, "Märchen-Lückentext", "plan")
               + "<div class=hilft>Schreibe das Märchen weiter. Fülle die Lücken: Schreibe passende Wörter und Sätze auf die Linien. Der Wortspeicher hilft dir.</div>"
               + "<div style='font-size:15pt'><b>Überschrift:</b> ______________________________</div>" + rows
               + "<div class=anfang style='margin-top:4mm;break-inside:avoid'><b>Wortspeicher</b><div style='font-size:14pt'>%s</div></div>" % ws)


def check_html() -> str:
    bl = "".join("<div class=auf2 style='margin-bottom:2.5mm'><h3 style='font-size:16pt'>%s</h3>%s</div>" % (
        esc(c["bereich"]), "".join("<div style='font-size:15pt;margin:1.5mm 0;display:flex;gap:3mm'><span style='font-size:18pt;line-height:1'>☐</span><span>%s</span></div>" % md(p[0])
                                   for p in c["punkte"])) for c in KOL["check"])
    return doc(F2_CSS, kopf("Klassenarbeit · Prüfen", "Märchen-Check", "haken")
               + "<div style='font-size:15pt;margin-bottom:2mm'>Name: ______________________</div>"
               + "<div class=hilft>Hake jeden Punkt ab, wenn du ihn geprüft hast. Verbessere mit einem anderen Stift. <b>Gib diese Seite mit deinem Märchen ab.</b></div>" + bl)


# ------------------------------------------------------------ Bauen
def bau_kollegin(b: f2.Bau) -> dict[str, Path]:
    KAUS.mkdir(parents=True, exist_ok=True)
    tmp = KAUS / "_teile"
    tmp.mkdir(exist_ok=True)
    p = {}
    p["lese_deck"] = b.mach(lese_deck_html(), KAUS / "Lesen_Deckblatt_A4.pdf", "Märchen lesen", 13.5, 1)
    for L in KOL["lese"]:
        t = dict(L, quelle=L["quelle"] + (" · %s" % L["untertitel"] if L.get("untertitel") else ""))
        tx = text_pdf(b, t, "Sprache · Leseübung %d · %s" % (L["n"], L["sterne"]), tmp / f"lese_{L['n']}_text.pdf", L.get("info"))
        # Zeichenkasten so wählen, dass die Aufgaben auf eine Seite passen (keine Restseite)
        LL = copy.deepcopy(L)
        for _ in range(5):
            au = b.mach(lese_aufgaben_html(LL), tmp / f"lese_{L['n']}_auf.pdf", "Leseübung %d · Aufgaben" % L["n"], 14, 2)
            if len(fitz.open(au)) == 1 or LL.get("zusatz_seite"):
                break
            b.bericht.pop()
            if not any(z.get("kasten", 0) > 14 for z in LL.get("zusatz", [])):
                # passt nicht auf eine Seite: Zusatz bekommt eine eigene Seite mit großem Zeichenkasten
                LL["zusatz_seite"] = True
                for z in LL["zusatz"]:
                    if z.get("kasten"):
                        z["kasten"] = 190
                continue
            for z in LL["zusatz"]:
                if z.get("kasten"):
                    z["kasten"] -= 6
        p[f"lese_{L['n']}"] = KAUS / f"Leseuebung_{L['n']}_{L['id']}_A4.pdf"
        s = verbinde([tx, au], p[f"lese_{L['n']}"])
        b.bericht.append("%-40s %d S." % (p[f"lese_{L['n']}"].relative_to(AUS), s))
    s1, tab = verben_html()
    a = b.mach(s1, tmp / "verben_1.pdf", "Märchenverben", 14, 1)
    c = b.mach(tab, tmp / "verben_2.pdf", "Märchenverben", 14, 4)
    if len(fitz.open(c)) > 4:
        b.fehler.append("Verbtabellen: mehr als 4 Seiten")
    p["verben"] = KAUS / "Maerchenverben_Praeteritum_A4.pdf"
    verbinde([a, c], p["verben"])
    seiten = [b.mach(hilfe_seite_html(s), tmp / f"hilfe_{s['nr']:02d}.pdf", "Märchen-Hilfe", 14, 1) for s in KOL["hilfe"]]
    p["hilfe"] = KAUS / "Maerchen_Hilfe_Heft_A4.pdf"
    verbinde(seiten, p["hilfe"])
    b.bericht.append("%-40s %d S. (je Seite genau 1 Seite geprüft)" % (p["hilfe"].relative_to(AUS), len(seiten)))
    p["merkmale"] = b.mach(merkmale_html(), KAUS / "Merkblatt_Maerchenmerkmale_A4.pdf", "Merkblatt Märchenmerkmale", 13, 1)
    p["quiz"] = b.mach(quiz_html(), KAUS / "Quiz_Maerchenmerkmale_A4.pdf", "Quiz Märchenmerkmale", 12, 1)
    p["bogen"] = b.mach(bogen_html(), KAUS / "Merkblatt_Spannungsbogen_A4.pdf", "Merkblatt Spannungsbogen", 13, 1)
    p["rap"] = b.mach(rap_html(), KAUS / "Maerchenrap_A4.pdf", "Märchenrap", 12.5, 2)
    p["schreibplan"] = b.mach(schreibplan_html(), KAUS / "Schreibplan_A4.pdf", "Schreibplan", 12.5, 2)
    p["lueckentext_e2"] = b.mach(lueckentext_html("Etappe 2 · Schreibplan ★"), KAUS / "Lueckentext_Etappe2_A4.pdf", "Märchen-Lückentext", 11.5, 2)
    p["lueckentext_ka"] = b.mach(lueckentext_html("Klassenarbeit F · Hilfe"), KAUS / "Lueckentext_Klassenarbeit_A4.pdf", "Märchen-Lückentext", 11.5, 2)
    p["check"] = b.mach(check_html(), KAUS / "Maerchen_Check_A4.pdf", "Märchen-Check", 14, 1)
    for x in tmp.iterdir():
        x.unlink()
    tmp.rmdir()
    return p


A5 = "A4 → A5, beidseitig"
PAKETE = [
    ("1", "Lesematerial Sprache", "freitags ab 04.12.", [
        ("Kinder", "lese_deck", A5, "je Kind 1", "Wahl des Märchens, So lest ihr"),
        *[("Lesen", f"lese_{n}", "A4, beidseitig", "je etwa ⅓ der Kinder", "Leseübung %d %s: Text mit Zeilen und Fußnoten, dann Aufgaben" % (n, s))
          for n, s in [(1, "★"), (2, "★"), (3, "★★"), (4, "★★"), (5, "★★★")]],
        ("Kinder", "verben", A5, "je Kind 1", "Verbliste; bleibt bis zur Klassenarbeit in der Mappe"),
        ("Kinder", "hilfe", "A4 → A5 als Heft (Broschüre)", "je Kind 1", "Märchen-Hilfe, Seiten 1–12; gilt bis zur Klassenarbeit")]),
    ("2", "Etappe 1 · Märchenmerkmale", "ab 09.12.", [
        ("Kinder", "Lernweg_F4_A4.pdf", "A4, einseitig", "je Kind 1", "zu Beginn; bleibt in der Mappe"),
        ("Kinder", "merkmale", A5, "je Kind 1", "Merkblatt"),
        ("Kinder", "quiz", A5, "je Kind 1", "mit dem eigenen Lese-Märchen"),
        ("Nachweis", "etappe1/GN1_A_A4.pdf", "A4, beidseitig", "nur als Ersatz", "GN1 läuft am Laptop (apps/gn1-digital)"),
        ("Nachweis", "etappe1/GN1_B_A4.pdf", "A4, beidseitig", "nur als Ersatz", ""),
        ("Förderung", "etappe1/foerder/Foerderpaket_1_A4.pdf", A5, "je F-Kind 1", "Lösungsstreifen umknicken"),
        ("Förderung", "etappe1/foerder/GN1F_A_A4.pdf", "A4, beidseitig", "je F-Kind 1", ""),
        ("Förderung", "etappe1/foerder/GN1F_B_A4.pdf", "A4, beidseitig", "nach Bedarf", ""),
        ("Lehrkraft", "etappe1/GN1_Erwartungshorizont_A4.pdf", "A4", "1", ""),
        ("Lehrkraft", "inputs/Skript_Input_1_A4.pdf", "A4", "1", "Input 1 Märchenmerkmale")]),
    ("3", "Etappe 2 · Spannungsbogen und spannend erzählen", "ab 15.12.", [
        ("Kinder", "rap", A5, "je Kind 1", "Einstieg: gemeinsam sprechen"),
        ("Kinder", "bogen", A5, "je Kind 1", "Merkblatt"),
        ("Kinder", "lueckentext_e2", A5, "★: nach Bedarf", "Schreibplan für das eigene Märchen als Lückentext"),
        ("Kinder", "schreibplan", A5, "★★: je Kind 1", "Schreibplan für das eigene Märchen"),
        ("Kinder", "etappe2/Etappe2_Bilder_im_Kopf_A4.pdf", A5 + ", geheftet", "je Tandem 1", "Jorinde und Joringel, zu zweit, Arbeitsseite"),
        ("Nachweis", "etappe2/GN2_A_A4.pdf", "A4, beidseitig", "je Kind 1", "erst ausgeben, wenn Etappe 2 geschafft ist"),
        ("Nachweis", "etappe2/GN2_B_A4.pdf", "A4, beidseitig", "etwa ⅓", "Wiederholung nach dem Üben"),
        ("Förderung", "etappe2/foerder/Foerderpaket_2_A4.pdf", A5, "je F-Kind 1", ""),
        ("Lehrkraft", "etappe2/GN2_Erwartungshorizont_A4.pdf", "A4", "1", ""),
        ("Lehrkraft", "inputs/Skript_Input_2_A4.pdf", "A4", "1", "Input 2 Spannungsbogen"),
        ("Lehrkraft", "inputs/Skript_Input_3_A4.pdf", "A4", "1", "Input 3 Bilder im Kopf")]),
    ("4", "Klassenarbeiten · Ein Märchen zu Ende schreiben", "ab GN2, Abgabe bis 13.01.", [
        ("Kinder", "klassenarbeit/KA_0_Auftrag_A4.pdf", "A4, beidseitig", "je Kind 1", "vorn in die Klassenarbeitsmappe"),
        *[("Anfänge", f"klassenarbeit/KA_{i}_{a['id']}_A4.pdf", "A4, beidseitig", "nach Wahl", "%s %s" % (f4.STERNE[a["stufe"]], a["titel"]))
          for i, a in enumerate(f4.KA["anfaenge"], 1)],
        *[("Anfänge F", f"klassenarbeit/KA_{i}_{a['id']}_F_A4.pdf", "A4, beidseitig", "nach Bedarf", "%s mit Schreibrahmen" % a["titel"])
          for i, a in enumerate(f4.KA["anfaenge"], 1)],
        ("Hilfe", "lueckentext_ka", "A4, beidseitig", "nach Bedarf", "Förderschwerpunkt Lernen, LRS, geringe Deutschkenntnisse; auf dem Bewertungsbogen ankreuzen"),
        ("Kinder", "check", "A4 oder A5", "je Kind 1", "wird mit dem Rohentwurf abgegeben"),
        ("Lehrkraft", "klassenarbeit/KA_Bewertungsbogen_A4.pdf", "A4", "je Kind 1", ""),
        ("Lehrkraft", "klassenarbeit/KA_Erwartungshorizonte_A4.pdf", "A4", "1", "je Anfang eine Seite"),
        ("Lehrkraft", "inputs/Skript_Input_4_A4.pdf", "A4", "1", "Input 4 Ein Ende planen"),
        ("Lehrkraft", "inputs/Skript_Input_5_A4.pdf", "A4", "1", "Input 5 Prüfen (Schreibkonferenz, nach der Abgabe)"),
        ("Lehrkraft", "Zeitplan_F4_Lehrkraft_A4.pdf", "A4", "1", "")]),
]
DIGITAL = {"2": "apps/gn1-digital/index.html (Gelingensnachweis 1 am Laptop, Variante A oder B) · inputs/Input_1.html am Beamer · Videos „Was sind Märchen?“ und „Gebrüder Grimm“",
           "3": "inputs/Input_2.html und Input_3.html am Beamer",
           "4": "inputs/Input_4.html (vor dem Schreiben) und Input_5.html (Schreibkonferenz) am Beamer · liniertes Papier und eine Mappe je Kind; Mappen am Ende jeder Stunde einsammeln"}


def paket_anleitung_html(nr: str, titel: str, wann: str, inv: list[tuple], start: int) -> str:
    rows, seite = [], start
    for o, d, f, a, h, sz in inv:
        rows.append("<tr><td style='text-align:center'><b>%s</b></td><td>%s</td><td style='word-break:break-all'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            "%d–%d" % (seite, seite + sz - 1) if sz > 1 else str(seite), esc(o), esc(Path(d).name), esc(f), esc(a), esc(h)))
        seite += sz
    return doc(GN_CSS + "body{font-size:11.5pt}table{font-size:11pt}td,th{padding:1.2mm 1.8mm}", (
        "<div class=meta>Lehrkraft · Fassung 4 · Materialpaket %s · %s</div><h1>%s</h1>"
        "<p>Alles in diesem PDF ist fertig zum Drucken. Die Seitenangaben beziehen sich auf dieses PDF. „A4 → A5“ heißt: verkleinert, 2 Seiten pro Blatt. "
        "Alles ist für Graustufen gesetzt.</p>"
        "<table style='table-layout:fixed'><tr><th style='width:16mm'>Seiten</th><th style='width:20mm'>Teil</th><th style='width:50mm'>Datei</th><th style='width:30mm'>Format</th>"
        "<th style='width:22mm'>Anzahl</th><th>Hinweis</th></tr>%s</table>%s") % (
        nr, esc(wann), esc(titel), "".join(rows),
        "<h2 style='font-size:15pt;margin:3mm 0 1.5mm'>Digital und Raum</h2><p>%s</p>" % esc(DIGITAL[nr]) if nr in DIGITAL else ""))


def bau_pakete(b: f2.Bau, kol: dict[str, Path]):
    PAUS.mkdir(parents=True, exist_ok=True)
    for nr, titel, wann, teile in PAKETE:
        inv = []
        for o, d, f, a, h in teile:
            p = kol[d] if d in kol else AUS / d
            if not p.exists():
                b.fehler.append("Paket %s: fehlt %s" % (nr, d))
                continue
            inv.append((o, str(p.relative_to(AUS)), f, a, h, len(fitz.open(p))))
        anl = PAUS / f"_anleitung_{nr}.pdf"
        n = 0
        for _ in range(3):
            b.mach(paket_anleitung_html(nr, titel, wann, inv, n + 1), anl, "Materialpaket %s" % nr, 10.5)
            neu = len(fitz.open(anl))
            if neu == n:
                break
            n = neu
            b.bericht.pop()
        name = "Paket_%s_%s.pdf" % (nr, re.sub(r"[^A-Za-z0-9]+", "_", titel.split(" · ")[0].replace("ä", "ae").replace("ü", "ue")).strip("_"))
        ziel = PAUS / name
        s = verbinde([anl] + [AUS / x[1] for x in inv], ziel)
        anl.unlink()
        b.bericht.append("%-40s %d S. (Anleitung %d S. + %d Teile), %.1f MB" % ("pakete/" + name, s, n, len(inv), ziel.stat().st_size / 1e6))


def main() -> int:
    b = f2.Bau()
    kol = bau_kollegin(b)
    f4.bau_arbeit(b)
    bau_pakete(b, kol)
    f4.pruefe_seiten(b)
    return b.ende()


if __name__ == "__main__":
    sys.exit(main())
