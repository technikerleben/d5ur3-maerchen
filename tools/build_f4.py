#!/usr/bin/env python3
"""Fassung 4 (28.11.2026): Etappe 1 Märchenmerkmale + GN1, Etappe 2 Spannungsbogen und spannend erzählen + GN2,
danach Klassenarbeit „Ein Märchen zu Ende schreiben“ (Rohentwurf im Unterricht, eigenes Tempo, Abgabe bis 13.01.),
anschließend Schreibkonferenz und Überarbeitung ohne Note. Lernmaterial ist überwiegend das der Kollegin (extern/).

    python3 tools/build_f4.py etappe 1|2     GN (Papier), Erwartungshorizont, Förderpaket; Etappe 2 dazu „Bilder im Kopf“
    python3 tools/build_f4.py gn1            GN1 digital → apps/gn1-digital/index.html (wird durchgespielt)
    python3 tools/build_f4.py arbeit         Klassenarbeit: Auftrag, 5 Anfänge (normal/F), Erwartungshorizonte, Bewertungsbogen
    python3 tools/build_f4.py input [n]      Inputs 1–5
    python3 tools/build_f4.py raum           Lernweg F4, Zeitplan
    python3 tools/build_f4.py druck          alte Gesamt-Druckanleitung (ersetzt durch die vier Pakete in build_f4_pakete.py)
    python3 tools/build_f4.py alles          alles außer druck; danach build_f4_pakete.py für Material der Kollegin und Pakete

Inhalte: inhalt/f4/ · Ausgabe: ausgabe/f4/ · Bausteine: build_f2.py, build_f3.py · Material der Kollegin: extern/ (nicht im Repo).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf as fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_f3 as f3  # noqa: E402  (stellt beim Import auf Fassung 3; wird unten auf Fassung 4 umgestellt)
from build_material import GN_CSS, TEXTE, doc, esc, md, verbinde  # noqa: E402
from satz import ROOT, kleinste_schrift, render_seiten  # noqa: E402
import build_texte  # noqa: E402

f2 = f3.f2
IN = ROOT / "inhalt" / "f4"
AUS = ROOT / "ausgabe" / "f4"
L = lambda p: json.loads(p.read_text("utf-8"))  # noqa: E731

f2.IN = f3.IN = IN
f2.AUS = f3.AUS = AUS
f2.STRAT = f3.STRAT = {k["id"]: k for k in L(IN / "strategien.json")["karten"]}
f2.RAUM = f3.RAUM = L(IN / "raum.json")
KA = L(IN / "klassenarbeit.json")
STERNE = {1: "★", 2: "★★", 3: "★★★"}
sym, kopf, F2_CSS, TEXTDB = f2.sym, f2.kopf, f2.F2_CSS, f2.TEXTDB

_rueck = f2.gn_rueckmeldung_html
f2.gn_rueckmeldung_html = lambda e, nw, v: (_rueck(e, nw, v).replace("weiter zu Etappe 3", "weiter zur Klassenarbeit")
                                             .replace("weiter zu Etappe 2", "weiter zu Etappe 2"))

TERMINE = [
    ("Fr 04.12.", "Sprache", "Offenes Lesen: Leseübungen 1–5 (★–★★★) im Tandem und Lesekiste; Lernzeit für den späten Zootiere-Termin am 08.12."),
    ("Mi 09.12.", "Deutsch", "Etappe 1: Videos, Input 1, Merkblatt Märchenmerkmale, Quiz mit dem eigenen Lese-Märchen"),
    ("Fr 11.12.", "Sprache", "Lesen; Märchenverben im Präteritum"),
    ("Di 15.12.", "Deutsch", "GN1 am Laptop · Etappe 2: Märchenrap, Input 2, Merkblatt Spannungsbogen, Schreibplan für das eigene Märchen"),
    ("Mi 16.12.", "Deutsch", "Input 3 · Bilder im Kopf zu zweit, Märchen-Hilfe S. 3–5 und 10 · GN2 für alle, die so weit sind"),
    ("Fr 18.12.", "Sprache", "Lesen; Märchen-Hilfe (Grammatik: Nomen, Fälle, wo/wohin)"),
    ("Di 22.12.", "Deutsch", "GN2 für die übrigen · Input 4 · ab GN2 beginnt die Klassenarbeit (Anfang wählen, planen, schreiben)"),
    ("Fr 08.01.", "Sprache", "Lesen; Verben und wörtliche Rede (Märchen-Hilfe S. 8–10)"),
    ("Di 12.01.", "Deutsch", "Klassenarbeit: Schreiben – spätestens jetzt schreiben alle, auch ohne GN2"),
    ("Mi 13.01.", "Deutsch", "Klassenarbeit: Schreiben, Prüfen mit dem Märchen-Check, Abgabe des Rohentwurfs (spätestens)"),
    ("ab 19.01.", "Deutsch", "ohne Note: Input 5, Schreibkonferenz zu dritt, Überarbeiten in einer Kopie des Rohentwurfs; Wahlzeit: P1 Märchenbuch, P2 Vorlesen, P3 Umformen"),
    ("bis 27.01.", "Lehrkraft", "Rohentwürfe bewertet (Bewertungsbogen), Noten eingetragen"),
]


# ------------------------------------------------------------ Etappen 1 und 2: Nachweis und Förderung (Lernmaterial: Kollegin)
def bau_etappe(b: f2.Bau, n: int):
    e = L(IN / f"etappe{n}.json")
    aus = AUS / f"etappe{n}"
    tmp = aus / "_teile"
    tmp.mkdir(parents=True, exist_ok=True)
    if n == 2:
        g = b.mach(f2.gemeinsam_html(e), tmp / "zweit.pdf", "Etappe 2 · zu zweit", 14, 3)
        txt = umbenennen(TEXTE / f"{e['text']}_A4.pdf", tmp / "text.pdf", "Etappe 2 · Bilder im Kopf")
        s = verbinde([txt, g], aus / "Etappe2_Bilder_im_Kopf_A4.pdf")
        b.bericht.append("%-40s %d S.  (Text, zu zweit, Arbeitsseite)" % ("etappe2/Etappe2_Bilder_im_Kopf_A4.pdf", s))
    nw = e["nachweis"]
    for v, var in nw["varianten"].items():
        a = b.mach(f2.gn_aufgaben_html(e, nw, v), tmp / f"gn_{v}.pdf", f"GN{n} {v}")
        r = b.mach(f2.gn_rueckmeldung_html(e, nw, v), tmp / f"gn_{v}_r.pdf", f"GN{n} {v} · Rückmeldung")
        txt = [umbenennen(TEXTE / f"{var['maerchen']}_A4.pdf", tmp / f"text_{v}.pdf", f"Gelingensnachweis {n} · Variante {v}")] if var.get("maerchen") else []
        s = verbinde(txt + [a, r], aus / f"GN{n}_{v}_A4.pdf")
        b.bericht.append("%-40s %d S." % (f"etappe{n}/GN{n}_{v}_A4.pdf", s))
    b.mach(f2.gn_erwartung_html(e, nw), aus / f"GN{n}_Erwartungshorizont_A4.pdf", f"GN{n} · Lehrkraft", 12)
    f = e["foerder"]
    mk = b.mach(f2.f_merkkarte_html(e), tmp / "f_merk.pdf", f"Merkkarte {n}F")
    fb = [b.mach(f2.f_blatt_html(e, x, "Etappe %dF · Blatt %s" % (n, x["nr"])), tmp / f"f_{x['nr']}.pdf", f"Blatt {x['nr']}") for x in f["blaetter"]]
    (aus / "foerder").mkdir(exist_ok=True)
    s = verbinde([mk] + ([TEXTE / f"{f['material']}_A4.pdf"] if f.get("material") else []) + fb, aus / "foerder" / f"Foerderpaket_{n}_A4.pdf")
    b.bericht.append("%-40s %d S." % (f"etappe{n}/foerder/Foerderpaket_{n}_A4.pdf", s))
    for v in (("A", "B") if f.get("nachweis") else ()):
        auf, rueck = f2.f_gn_html(e, v)
        a = b.mach(auf, tmp / f"fgn_{v}.pdf", f"GN{n}F {v}")
        r = b.mach(rueck, tmp / f"fgn_{v}_r.pdf", f"GN{n}F {v} · Rückmeldung")
        s = verbinde([a, r], aus / "foerder" / f"GN{n}F_{v}_A4.pdf")
        b.bericht.append("%-40s %d S." % (f"etappe{n}/foerder/GN{n}F_{v}_A4.pdf", s))
    for x in tmp.iterdir():
        x.unlink()
    tmp.rmdir()


# ------------------------------------------------------------ Texte mit Zeilennummern (Satz wie alle Märchentexte)
KOL_JSON = ROOT / "extern" / "kollegin.json"
KOL_TEXTE = json.loads(KOL_JSON.read_text("utf-8"))["anfaenge"] if KOL_JSON.exists() else {}


def text_pdf(b: f2.Bau, t: dict, label: str, ziel: Path, info: str | None = None, zid: str | None = None) -> Path:
    tt = {"rolle": label, "titel": t["titel"], "quelle": t["quelle"], "text": t["text"], "fussnoten": t.get("fussnoten", []),
          "vollstaendig": t.get("vollstaendig", True)}
    inhalt, fns = build_texte.text_html(tt)
    if info:
        i = inhalt.find("<div class=par")
        inhalt = inhalt[:i] + "<div style='border:1.4pt solid #111;border-radius:2mm;padding:2mm 3mm;margin:0 0 3mm;font-size:14pt'><b>Gut zu wissen:</b> %s</div>" % esc(info) + inhalt[i:]
    pg = b.br.new_page()
    for enger in build_texte.ENGER:
        info_ = render_seiten(pg, inhalt, build_texte.CSS + enger, fns, ziel, fuss_rechts=t["titel"])
        rest = info_["zeilen_je_seite"][-1]
        if info_["seiten"] == 1 or (rest and rest[1] - rest[0] + 1 >= 4):
            break
    zeilentext = pg.evaluate("""() => [...document.querySelectorAll('.ln[data-zeile]')].map(l => {
        const c = l.cloneNode(true); c.querySelectorAll('.nr, sup').forEach(x => x.remove());
        return c.textContent.replace(/\\s+/g, ' ').trim(); })""")
    pg.close()
    if zid:  # Zeilen merken (für Zeilenangaben im Kontroll-Kiosk); liegt bei den Texten der Kollegin, nicht im Repo
        zj = AUS / "kollegin" / "zeilen.json"
        zj.parent.mkdir(parents=True, exist_ok=True)
        alle = json.loads(zj.read_text("utf-8")) if zj.exists() else {}
        alle[zid] = {"zeilentext": zeilentext, "seiten": info_["seiten"]}
        zj.write_text(json.dumps(alle, ensure_ascii=False, indent=1), "utf-8")
    mn = kleinste_schrift(ziel, ausnahmen=(11.0,))
    if mn < 14:
        b.fehler.append("%s Schrift %.1f" % (ziel.name, mn))
    b.bericht.append("%-40s %d S.  min %.1f pt" % (ziel.relative_to(AUS), info_["seiten"], mn))
    return ziel



# ------------------------------------------------------------ Klassenarbeit
CSS_KA = F2_CSS + "td.k{width:12mm;text-align:center;font-size:17pt}"


def auftrag_html() -> str:
    so = "".join("<li style='margin:1mm 0'>%s</li>" % md(s.replace("%ABGABE%", KA["abgabe"])) for s in KA["so"])
    auftrag = "".join("<tr><td class=k><b>%d</b></td><td>%s</td><td class=k>☐</td></tr>" % (i, md(s)) for i, s in enumerate(KA["auftrag"], 1))
    seite1 = (kopf("Klassenarbeit · Deutsch · Märchen", KA["titel"], "stern")
              + "<div style='font-size:15pt;margin-bottom:2mm'>Name: ________________________ &nbsp; Klasse: ________</div>"
              + "<div style='font-size:15pt;margin-bottom:3mm'>Mein Anfang: ______________________ &nbsp; ☐ ★ &nbsp; ☐ ★★ &nbsp; ☐ ★★★</div>"
              + "<div class=hilft><b>Deine Situation</b><br>%s</div>" % esc(KA["situation"])
              + "<div style='font-size:16pt;font-weight:700;margin:3mm 0 1mm'>So arbeitest du</div><ul style='margin-left:7mm;font-size:14.5pt'>%s</ul>" % so
              + "<div style='font-size:16pt;font-weight:700;margin:3mm 0 1mm'>Dein Auftrag</div><table class='st eng' style='font-size:14pt'>%s</table>" % auftrag)
    zellen = ["<td style='width:50%%'><b>%s:</b> %s</td>" % (esc(k), esc(t)) for k, t in KA["bewertet"]]
    bew = "".join("<tr>%s</tr>" % "".join(zellen[i:i + 2]) for i in range(0, len(zellen), 2))
    wahl = "".join(
        "<div class=anfang style='margin:0 0 1.2mm;padding:1.2mm 3mm;font-size:13.5pt'><b>%s &nbsp; %s</b> – %s <i style='font-size:12.5pt'>(%s)</i></div>"
        % (STERNE[a["stufe"]], esc(a["titel"]), esc(a["teaser"]), esc(a["warum"])) for a in KA["anfaenge"])
    seite2 = ("<div style='break-before:page'></div>" + kopf("Klassenarbeit · Seite 2", "Wähle deinen Anfang", "stern")
              + "<p style='font-size:13.5pt;margin-bottom:1.5mm'>★ gut zu verstehen · ★★ mehr eigene Ideen · ★★★ ältere Sprache. "
              "Mit jedem Anfang kannst du alle Punkte erreichen. Sprich deine Wahl mit der Lehrkraft ab.</p>" + wahl
              + "<div style='font-size:15pt;font-weight:700;margin:2mm 0 1mm'>Darauf achten wir bei der Bewertung</div><table class='st eng' style='font-size:12.5pt;table-layout:fixed'>%s</table>" % bew
              + "<div class=hilft style='margin-top:2mm;font-size:13pt'>%s</div>" % md(KA["rohentwurf"]))
    return doc(CSS_KA, seite1 + seite2)


def aufgaben_html(a: dict, f: bool) -> str:
    merk = "".join("<div style='font-size:14.5pt;margin:1mm 0'>☐ %s</div>" % md(m) for m in KA["merkmale"])
    if f:
        a1 = a["aufgabe1_f"]
        auf1 = "<p>%s</p>%s" % (md(a1["text"]), "".join("<div style='font-size:14.5pt;margin:1mm 0'>☐ %s</div>" % esc(o) for o in a1["optionen"]))
    else:
        auf1 = ("<p>Markiere im Text je ein Beispiel und schreibe es auf.</p><table class=st style='table-layout:fixed;font-size:14pt'>%s</table>"
                % "".join("<tr><td style='width:58mm;height:13mm'><b>%s</b></td><td></td></tr>" % esc(m) for m, _ in a["aufgabe1"]))
    return doc(F2_CSS, kopf("Klassenarbeit%s · %s %s" % (" F" if f else "", STERNE[a["stufe"]], a["titel"]), "Aufgabe 1 und 2", "stern")
               + "<div class=auf2><h3>Aufgabe 1 · Finde Märchenmerkmale im Anfang</h3>%s</div>" % auf1
               + "<div class=auf2><h3>Aufgabe 2 · Plane deine Märchenmerkmale</h3><p>Kreuze <b>mindestens 4</b> an. Diese baust du in deinen Text ein.</p>"
               "<div style='columns:2;column-gap:6mm'>%s</div></div>" % merk)


SCHRITTE = [("D", "Versuche", "dann", "Was tat die Figur? Oft dreimal.", "Wer hilft?"),
            ("D", "Höhepunkt", "dann", "Wo wurde es gefährlich?", "Wer ist Gegenspieler:in?"),
            ("A", "Lösung", "also", "Wie wurde das Problem gelöst?", "Wer oder was löst das Problem?"),
            ("A", "Schluss", "also", "Wie endete es? Schlusssatz", "Wer wird wie belohnt? Wer wird wie bestraft?")]


def schreibplan_html(a: dict) -> str:
    rows = "".join("<tr><td style='width:16mm;text-align:center;font-size:26pt;font-weight:700'>%s</td><td style='width:62mm'><b>%s</b> · <i>%s</i><br>%s<br>%s</td>"
                   "<td style='height:46mm'></td></tr>" % (bu, esc(t), w, esc(f1), esc(f2_)) for bu, t, w, f1, f2_ in SCHRITTE)
    return doc(F2_CSS, kopf("Klassenarbeit · %s %s" % (STERNE[a["stufe"]], a["titel"]), "Schreibplan: Plane dein Ende", "plan")
               + "<div class=hilft>Du darfst den Schreibplan nutzen, du musst aber nicht. Notiere nur Stichwörter. "
               "Der Anfang hat J – W – A schon erzählt. Du schreibst D – D – A – A.</div>"
               "<table class=st style='table-layout:fixed;font-size:14pt'>%s</table>" % rows)


def rahmen_html(a: dict) -> str:
    rahmen = "".join("<div style='display:flex;gap:3mm;margin-top:1.2mm'><div style='width:12mm;font-size:20pt;font-weight:700;text-align:center'>%s</div>"
                     "<div style='flex:1'><div style='font-size:15pt'>%s%s</div>%s</div></div>" % (
                         bu, "<i>%s:</i> " % w if w else "", esc(s) + " …", "<div class=linie></div>" * n) for bu, w, s, n in a["rahmen_f"])
    return doc(F2_CSS, kopf("Klassenarbeit F · %s %s" % (STERNE[a["stufe"]], a["titel"]), "Schreibrahmen: Schreibe das Märchen zu Ende", "plan")
               + "<div class=hilft>Schreibe auf die Linien weiter. Die Satzanfänge helfen dir. Der Lückentext mit Wortspeicher und die Märchenverben auch.</div>"
               "<div style='font-size:15pt'><b>Überschrift:</b> ______________________________</div>" + rahmen)


def erwartung_html(a: dict) -> str:
    return ("<div class=meta>Lehrkraft · Klassenarbeit · %s</div><h1>%s</h1>" % (STERNE[a["stufe"]], esc(a["titel"]))
            + "<p style='font-size:12.5pt;margin-bottom:2mm'><b>Stufe:</b> %s · <b>Wo der Anfang aufhört:</b> %s</p>" % (esc(a["warum"]), esc(a["anknuepfung"]))
            + "<h2 style='font-size:15pt;margin:2mm 0 1.5mm'>Aufgabe 1</h2><table><tr><th>Merkmal</th><th>Beispiel</th></tr>%s</table>"
            % "".join("<tr><td style='width:45mm'>%s</td><td>%s</td></tr>" % (esc(m), md(x)) for m, x in a["aufgabe1"])
            + "<p style='font-size:12.5pt'>F-Fassung: richtig sind %s.</p>" % ", ".join("„%s“" % x for x in a["aufgabe1_f"]["loesung"])
            + "<h2 style='font-size:15pt;margin:2mm 0 1.5mm'>Das Ende (Kriterien K1–K6)</h2><table><tr><th>Kriterium</th><th>Worauf achten bei diesem Anfang</th></tr>%s</table>"
            % "".join("<tr><td style='width:36mm'><b>%s</b></td><td>%s</td></tr>" % (esc(k), esc(t)) for k, t in a["erwartung"])
            + ("<p style='font-size:12.5pt;margin-top:2mm'><b>Zum Vergleich, nicht erwartet – das Original:</b> %s</p>" % esc(a["original"]) if a.get("original") else ""))


def bogen_html() -> str:
    bg = KA["bogen"]
    kopfz = "".join("<th style='width:15mm;font-size:9.5pt;padding:1mm'>%s</th>" % esc(s) for s in bg["stufen"])
    rows = "".join("<tr><td><b>%s</b></td><td><b>%s</b> <span style='font-size:10pt'>%s</span></td>%s<td></td></tr>"
                   % (k, esc(n), esc(t), "".join("<td style='text-align:center'>☐ %d</td>" % p for p in pts)) for k, n, t, pts in bg["kriterien"])
    noten = " · ".join("%s ab %d" % (n, p) for n, p in bg["noten"][:-1]) + " · darunter ungenügend"
    linie = "<div style='border-bottom:1px solid #999;height:8mm'></div>"
    return doc(GN_CSS + "body{font-size:11pt}table{font-size:11pt}td,th{padding:1mm 1.4mm}h1{margin-bottom:1mm}", (
        "<div class=meta>Klassenarbeit · Deutsch · Märchen</div><h1>Bewertungsbogen</h1>"
        "<table style='margin-bottom:2mm'><tr><td style='width:50%%'>Name:</td><td>Abgabe am:</td></tr>"
        "<tr><td>Anfang: ______________ ☐★ ☐★★ ☐★★★</td>"
        "<td>☐ mit Schreibrahmen/Lückentext <span style='font-size:9.5pt'>(Förderschwerpunkt Lernen, LRS, geringe Deutschkenntnisse)</span></td></tr></table>"
        "<table style='table-layout:fixed'><tr><th style='width:8mm'></th><th>Kriterium</th>%s<th style='width:15mm;font-size:9.5pt'>Punkte</th></tr>%s"
        "<tr><td></td><td><b>Zusatz</b> <span style='font-size:10pt'>%s</span></td><td colspan=5></td><td></td></tr>"
        "<tr><td></td><td colspan=6 style='text-align:right'><b>Summe (höchstens 100)</b></td><td></td></tr></table>"
        "<p style='margin:2mm 0'><b>Note:</b> ____________________ &nbsp; <span style='font-size:10.5pt'>Notengrenzen in Punkten: %s</span></p>"
        "<p style='margin-top:3mm'><b>Das gelingt dir schon:</b></p>%s%s"
        "<p style='margin-top:3mm'><b>Daran arbeitest du bei der Überarbeitung (ohne Note):</b></p>%s%s"
        "<p style='margin-top:6mm'>Datum, Unterschrift Lehrkraft: ______________________ &nbsp; Unterschrift Erziehungsberechtigte: ______________________</p>")
        % (kopfz, rows, esc(bg["zusatz"]), esc(noten), linie, linie, linie, linie))


def umbenennen(quelle: Path, ziel: Path, label: str) -> Path:
    """Kopie eines Text-PDFs mit neuer Kopfzeile (z. B. „Klassenarbeit · Märchenanfang“); Text und Zeilen bleiben unverändert."""
    from fontTools.ttLib import TTFont
    ttf = ziel.parent / "_andika700.ttf"
    if not ttf.exists():
        f = TTFont(str(f2.ROOT / "assets" / "fonts" / "andika-latin-700-normal.woff2") if (f2.ROOT / "assets" / "fonts").exists()
                   else str(next(f2.ROOT.rglob("andika-latin-700-normal.woff2"))))
        f.flavor = None
        f.save(str(ttf))
    d = fitz.open(quelle)
    pg = d[0]
    sp = next(s for b in pg.get_text("dict")["blocks"] for li in b.get("lines", []) for s in li["spans"] if s["font"].endswith("Bold") and s["size"] < 15)
    pg.add_redact_annot(fitz.Rect(sp["bbox"]), fill=(1, 1, 1))
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    pg.insert_font(fontname="andb", fontfile=str(ttf))
    pg.insert_text(fitz.Point(sp["origin"]), label.upper(), fontname="andb", fontsize=sp["size"], color=(0x44 / 255,) * 3)
    d.save(ziel)
    return ziel


def extern_seiten(b: f2.Bau, stw: str, seiten: list[int], ziel: Path) -> Path:
    pdf = f2.extern_pdf(stw)
    if not pdf:
        b.bericht.append("  (Vorlage %s fehlt in extern/ – Platzhalter eingelegt)" % stw)
        return b.mach(f2.platzhalter_html(stw), ziel, "Vorlage Kollegin", 14)
    q, d = fitz.open(pdf), fitz.open()
    for s in seiten:
        d.insert_pdf(q, from_page=s - 1, to_page=s - 1)
    d.save(ziel)
    return ziel


def bau_arbeit(b: f2.Bau):
    aus = AUS / "klassenarbeit"
    tmp = aus / "_teile"
    tmp.mkdir(parents=True, exist_ok=True)
    b.mach(auftrag_html(), aus / "KA_0_Auftrag_A4.pdf", "Klassenarbeit · Auftrag", 12.5, 2)
    erw = []
    for i, a in enumerate(KA["anfaenge"], 1):
        if a.get("extern") and a["id"] in KOL_TEXTE:
            # Anfang der Kollegin im HBG-Satz (Text liegt in extern/kollegin.json)
            txt = text_pdf(b, dict(KOL_TEXTE[a["id"]], vollstaendig=False), "Klassenarbeit · Märchenanfang", tmp / f"text_{a['id']}.pdf")
            anf = [txt, b.mach(aufgaben_html(a, False), tmp / f"auf_{a['id']}.pdf", "Klassenarbeit · Aufgaben", 14, 1)]
            anf_f = [txt, b.mach(aufgaben_html(a, True), tmp / f"auff_{a['id']}.pdf", "Klassenarbeit F · Aufgaben", 14, 1)]
        elif a.get("extern"):
            anf = [extern_seiten(b, a["extern"], a["extern_seiten"], tmp / f"ext_{a['id']}.pdf")]
            anf_f = anf
        else:
            txt = umbenennen(TEXTE / f"{a['text']}_A4.pdf", tmp / f"text_{a['id']}.pdf", "Klassenarbeit · Märchenanfang")
            anf = [txt, b.mach(aufgaben_html(a, False), tmp / f"auf_{a['id']}.pdf", "Klassenarbeit · Aufgaben", 14, 1)]
            anf_f = [anf[0], b.mach(aufgaben_html(a, True), tmp / f"auff_{a['id']}.pdf", "Klassenarbeit F · Aufgaben", 14, 1)]
        plan = b.mach(schreibplan_html(a), tmp / f"plan_{a['id']}.pdf", "Klassenarbeit · Schreibplan", 14, 1)
        rahmen = b.mach(rahmen_html(a), tmp / f"rahmen_{a['id']}.pdf", "Klassenarbeit F · Schreibrahmen", 14, 1)
        name = f"KA_{i}_{a['id']}"
        s = verbinde(anf + [plan], aus / f"{name}_A4.pdf")
        sf = verbinde(anf_f + [plan, rahmen], aus / f"{name}_F_A4.pdf")
        b.bericht.append("%-40s %d S. · F: %d S.  (%s)" % (f"klassenarbeit/{name}_A4.pdf", s, sf, STERNE[a["stufe"]]))
        erw.append(erwartung_html(a))
    b.mach(doc(GN_CSS + "body{font-size:11.5pt}table{font-size:11.5pt}td,th{padding:1.1mm 1.8mm}h1{margin-bottom:1mm}",
               "<div style='break-before:page'></div>".join(erw)), aus / "KA_Erwartungshorizonte_A4.pdf", "Erwartungshorizonte", 11.5, len(erw))
    b.mach(bogen_html(), aus / "KA_Bewertungsbogen_A4.pdf", "Bewertungsbogen", 9.4, 1)
    for x in tmp.iterdir():
        x.unlink()
    tmp.rmdir()


# ------------------------------------------------------------ Lernweg und Zeitplan
def lernweg_html() -> str:
    o = lambda t: "<div class=p>○ %s</div>" % t  # noqa: E731
    gn = lambda t: "<div class=p><b>%s %s</b> &nbsp; ____ / 5</div>" % (sym("haken", 5.5), t)  # noqa: E731
    blk = lambda n, t, sub, inhalt: ("<div class=blk><div class=nr>%d</div><div style='flex:1'><div class=bt>%s <span class=sub>%s</span></div>%s</div></div>"  # noqa: E731
                                     % (n, esc(t), esc(sub), inhalt))
    css = GN_CSS + (".blk{display:flex;gap:3mm;border:1.4px solid #333;border-radius:3mm;padding:1.3mm 3mm;margin-bottom:1.6mm}"
                    ".nr{font-size:20pt;font-weight:700;width:9mm;text-align:center}.bt{font-size:13.5pt;font-weight:700;margin-bottom:.3mm}"
                    ".sub{font-size:11pt;font-weight:400}.p{font-size:12pt;margin:.3mm 0;line-height:1.3}.zw{columns:2;column-gap:6mm}body{font-size:12.5pt}")
    teile = [
        blk(1, "Märchen lesen", "in Sprache, freitags – im Tandem oder allein",
            "<div class=zw>%s</div>" % "".join(o(x) for x in ["Die Sterntaler ★", "Die 12 Monate ★", "Des Kaisers neue Kleider ★★", "Hänsel und Gretel ★★",
                                                               "Die Bremer Stadtmusikanten ★★★", "Buch aus der Lesekiste: ____________"])
            + "<div class=p><b>Mein Märchen für Deutsch:</b> ______________________</div>"),
        blk(2, "Märchenmerkmale", "Etappe 1",
            o("Videos „Was sind Märchen?“ und „Gebrüder Grimm“") + o("Merkblatt Märchenmerkmale lesen") + o("Quiz mit Beispielen aus <b>meinem</b> Märchen")
            + gn("Gelingensnachweis 1 am Laptop")),
        blk(3, "Märchenaufbau: der Spannungsbogen", "Etappe 2",
            o("Märchenrap &nbsp; ○ Merkblatt Spannungsbogen lesen") + o("Schreibplan für mein Märchen: ★ als Lückentext &nbsp; ○ ★★ frei")),
        blk(4, "Spannend erzählen", "Etappe 2",
            o("Bilder im Kopf (zu zweit, „Jorinde und Joringel“)") + o("Märchen-Hilfe: S. 3 Satzanfänge · S. 4 Wortfelder · S. 5 Adjektive · S. 10 wörtliche Rede")
            + o("Märchenverben im Präteritum") + gn("Gelingensnachweis 2")),
        blk(5, "Klassenarbeit: ein Märchen zu Ende schreiben", "nur in der Schule · Abgabe spätestens %s" % KA["abgabe"],
            "<div class=p><b>Mein Anfang:</b> ______________________ &nbsp; ☐ ★ &nbsp; ☐ ★★ &nbsp; ☐ ★★★</div>"
            + "<div class=zw>%s</div>" % "".join(o(x) for x in ["Anfang lesen und markieren", "Aufgabe 1 und 2", "Schreibplan (freiwillig)", "Text schreiben",
                                                               "Märchen-Check", "abgegeben am ________"])),
        blk(6, "Nach der Abgabe", "ohne Note",
            "<div class=zw>%s</div>" % "".join(o(x) for x in ["Schreibkonferenz", "Überarbeitungsplan", "Kopie überarbeiten (grüner Stift)", "Wahlhilfe"])
            + "<div class=p><b>Wahlzeit:</b> ○&nbsp;P1 Märchenbuch &nbsp; ○&nbsp;P2 Vorlesen &nbsp; ○&nbsp;P3 Umformen</div>"),
    ]
    return doc(css, "<div class=meta>Lernweg · Deutsch · Märchen</div><h1>Lernweg – Märchen</h1>"
               "<p style='margin-bottom:2mm'>Name: ____________________ &nbsp; Klasse: ______ &nbsp; Hake ab, was du geschafft hast.</p>" + "".join(teile))


def zeitplan_html() -> str:
    rows = "".join("<tr><td style='white-space:nowrap'><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (esc(d), esc(f), esc(t)) for d, f, t in TERMINE)
    return doc(GN_CSS + "body{font-size:12pt}table{font-size:12pt}", (
        "<div class=meta>Lehrkraft · Fassung 4 · Stand 28.11.2026</div><h1>Zeitplan Märchen</h1>"
        "<p style='margin-bottom:2mm'><b>Prinzip:</b> Etappe 1 und 2 enden mit einem Gelingensnachweis. Danach schreiben die Kinder als <b>Klassenarbeit</b> "
        "einen Märchenanfang zu Ende: nur im Unterricht unter Aufsicht, in ihrem Tempo, Mappen werden jede Stunde eingesammelt, "
        "Abgabe des Rohentwurfs spätestens %s. Bewertet wird der Rohentwurf. Danach wird ohne Note überarbeitet.</p>"
        "<table><tr><th style='width:22mm'>Datum</th><th style='width:20mm'>Fach</th><th>Inhalt</th></tr>%s</table>"
        "<p style='margin-top:2mm'>Bei viel Krankheit und dadurch zu wenig Schreibzeit wird eine Sonderlösung gefunden.</p>") % (KA["abgabe"], rows))


def bau_raum(b: f2.Bau):
    b.mach(lernweg_html(), AUS / "Lernweg_F4_A4.pdf", "Lernweg", 11, 1)
    b.mach(zeitplan_html(), AUS / "Zeitplan_F4_Lehrkraft_A4.pdf", "Zeitplan", 11, 1)


# ------------------------------------------------------------ Druck
EXTERN_DRUCK = [
    ("Sprache", "AB-Leseuebung 1–5 (★–★★★)", "je Übung etwa 1/3 der Kinder; zum Auswählen auslegen"),
    ("Etappe 1", "Merkblatt Märchenmerkmale, Quiz Märchenmerkmale", "Quiz je Kind (2 auf einer Seite: halbieren); Merkblatt je Kind oder Lerntheke"),
    ("Etappe 2", "Märchenrap, Merkblatt Spannungsbogen, Märchen-Schreibplan", "Schreibplan je Kind; zusätzlich Lückentext (★)"),
    ("Etappe 2 + Arbeit", "Märchen-Hilfe (Heft, A5), Märchenverben im Präteritum", "je Kind oder je Tisch; während der Klassenarbeit erlaubt"),
    ("Arbeit", "Vertiefung 1 und 2: Seite 2 steckt in KA_1 und KA_2", "nicht extra drucken"),
    ("Arbeit", "Märchen-Lückentext mit Wortspeicher", "nur für Kinder mit Förderschwerpunkt Lernen, LRS, geringen Deutschkenntnissen"),
    ("Arbeit", "Märchen-Check (eigenes Märchen)", "je Kind 1 (2 auf einer Seite: halbieren); wird mit dem Rohentwurf abgegeben"),
    ("Arbeit", "liniertes Papier, Mappe je Kind", "Mappen am Ende jeder Stunde einsammeln"),
]


def druck_liste() -> list[tuple]:
    r = [("Kinder", "Lernweg_F4_A4.pdf", "A4, einseitig", "je Kind 1", "zu Beginn; bleibt in der Mappe"),
         ("Etappe 1", "etappe1/GN1_A_A4.pdf", "A4, beidseitig", "nur als Ersatz", "GN1 läuft am Laptop (apps/gn1-digital)"),
         ("Etappe 1", "etappe1/GN1_B_A4.pdf", "A4, beidseitig", "nur als Ersatz", ""),
         ("Etappe 1", "etappe1/foerder/Foerderpaket_1_A4.pdf", "A4 → A5, beidseitig", "je F-Kind 1", "Lösungsstreifen umknicken"),
         ("Etappe 1", "etappe1/foerder/GN1F_A_A4.pdf", "A4, beidseitig", "je F-Kind 1", ""),
         ("Etappe 2", "etappe2/Etappe2_Bilder_im_Kopf_A4.pdf", "A4 → A5, beidseitig, geheftet", "je Tandem 1", "Text „Jorinde und Joringel“ + zu zweit + Arbeitsseite"),
         ("Etappe 2", "etappe2/GN2_A_A4.pdf", "A4, beidseitig", "je Kind 1", "erst ausgeben, wenn Etappe 2 geschafft ist"),
         ("Etappe 2", "etappe2/GN2_B_A4.pdf", "A4, beidseitig", "etwa ⅓", "Wiederholung nach dem Üben"),
         ("Etappe 2", "etappe2/foerder/Foerderpaket_2_A4.pdf", "A4 → A5, beidseitig", "je F-Kind 1", "")]
    r.append(("Arbeit", "klassenarbeit/KA_0_Auftrag_A4.pdf", "A4, beidseitig", "je Kind 1", "steckt vorn in der Klassenarbeitsmappe"))
    for i, a in enumerate(KA["anfaenge"], 1):
        r.append(("Arbeit", f"klassenarbeit/KA_{i}_{a['id']}_A4.pdf", "A4, beidseitig", "nach Wahl", "%s %s" % (STERNE[a["stufe"]], a["titel"])))
        r.append(("Arbeit", f"klassenarbeit/KA_{i}_{a['id']}_F_A4.pdf", "A4, beidseitig", "nach Bedarf", "mit Schreibrahmen"))
    r += [("Lehrkraft", "klassenarbeit/KA_Bewertungsbogen_A4.pdf", "A4", "je Kind 1", ""),
          ("Lehrkraft", "klassenarbeit/KA_Erwartungshorizonte_A4.pdf", "A4", "1", ""),
          ("Lehrkraft", "etappe1/GN1_Erwartungshorizont_A4.pdf", "A4", "1", ""),
          ("Lehrkraft", "etappe2/GN2_Erwartungshorizont_A4.pdf", "A4", "1", ""),
          ("Lehrkraft", "Zeitplan_F4_Lehrkraft_A4.pdf", "A4", "1", "")]
    r += [("Lehrkraft", f"inputs/Skript_Input_{i}_A4.pdf", "A4", "1", "Input %d" % i) for i in range(1, 6)]
    return r


def druck_html(inv: list[tuple], start: int) -> str:
    rows, seite = [], start
    for o, d, f, a, h, sz in inv:
        rows.append("<tr><td style='text-align:center'><b>%s</b></td><td>%s</td><td style='word-break:break-all'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            "%d–%d" % (seite, seite + sz - 1) if sz > 1 else str(seite), esc(o), esc(Path(d).name), esc(f), esc(a), esc(h)))
        seite += sz
    ext = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (esc(a), esc(b_), esc(c)) for a, b_, c in EXTERN_DRUCK)
    return doc(GN_CSS + "body{font-size:11.5pt}table{font-size:11pt}td,th{padding:1.2mm 1.8mm}", (
        "<div class=meta>Lehrkraft · Fassung 4</div><h1>Druckanleitung Märchen</h1>"
        "<p>Seitenangaben beziehen sich auf das Gesamt-PDF. Pakete mit „A4 → A5“ verkleinert drucken (2 Seiten pro Blatt), alles andere in A4. Alles ist für Graustufen gemacht.</p>"
        "<table style='table-layout:fixed'><tr><th style='width:16mm'>Seiten</th><th style='width:20mm'>Teil</th><th style='width:52mm'>Datei</th><th style='width:30mm'>Format</th>"
        "<th style='width:20mm'>Anzahl</th><th>Hinweis</th></tr>%s</table>"
        "<h2 style='font-size:15pt;margin:3mm 0 1.5mm'>Digital</h2><p>apps/gn1-digital/index.html: Gelingensnachweis 1 am Laptop · inputs/Input_1–5.html am Beamer</p>"
        "<h2 style='font-size:15pt;margin:3mm 0 1.5mm'>Material der Kollegin (von ihren Originalen drucken)</h2>"
        "<table><tr><th style='width:28mm'>wofür</th><th>Material</th><th>Hinweis</th></tr>%s</table>") % ("".join(rows), ext))


def bau_druck(b: f2.Bau):
    inv, fehlt = [], []
    for o, d, f, a, h in druck_liste():
        p = AUS / d
        if not p.exists():
            fehlt.append(d)
            continue
        inv.append((o, d, f, a, h, len(fitz.open(p))))
    if fehlt:
        b.fehler.append("Druck: fehlt " + ", ".join(fehlt))
        return
    anl = AUS / "Druckanleitung_F4_A4.pdf"
    n = 0
    for _ in range(3):
        b.mach(druck_html(inv, n + 1), anl, "Druckanleitung", 10.5)
        neu = len(fitz.open(anl))
        if neu == n:
            break
        n = neu
        b.bericht.pop()
    ges = AUS / "Gesamtpaket_F4.pdf"
    s = verbinde([anl] + [AUS / d for _, d, *_ in inv], ges)
    if s != n + sum(x[5] for x in inv):
        b.fehler.append("Gesamt-PDF: Seitenzahl stimmt nicht")
    b.bericht.append("%-40s %d S. (Anleitung %d S. + %d Teile), %.1f MB" % (ges.name, s, n, len(inv), ges.stat().st_size / 1e6))


# ------------------------------------------------------------ Setzprüfung
def pruefe_seiten(b: f2.Bau):
    """Keine Seite darf nur einen Rest enthalten (z. B. ein Wort oder eine Zeile nach einem Umbruch)."""
    import re
    n = 0
    for pdf in sorted(AUS.rglob("*.pdf")):
        if pdf.name.startswith(("Gesamtpaket", "Paket_")) or "Reinschrift" in pdf.name or "_teile" in pdf.parts or "pakete" in pdf.parts:
            continue
        d = fitz.open(pdf)
        for i, pg in enumerate(d):
            if len(d) == 1:
                continue
            body = re.sub(r"Deutsch · Jahrgang 5 · Märchen.*", "", pg.get_text(), flags=re.S).strip()
            if len(body) < 120 and not pg.get_images():
                b.fehler.append("Setzfehler: %s Seite %d hat nur einen Rest (%r)" % (pdf.relative_to(AUS), i + 1, body[:40]))
        n += 1
    b.bericht.append("%-40s %d PDFs ohne Restseiten" % ("Setzprüfung", n))


# ------------------------------------------------------------ main
def main(argv: list[str]) -> int:
    was = argv[0] if argv else "alles"
    arg = argv[1] if len(argv) > 1 else None
    b = f2.Bau()
    if was in ("etappe", "alles"):
        for n in ([int(arg)] if arg else [1, 2]):
            bau_etappe(b, n)
    if was in ("gn1", "alles"):
        f3.pruefe_gn1(b, f3.gn1_digital())
    if was in ("arbeit", "alles"):
        bau_arbeit(b)
    if was in ("input", "alles"):
        for n in ([int(arg)] if arg else [1, 2, 3, 4, 5]):
            f3.bau_input(b, n)
    if was in ("raum", "alles"):
        bau_raum(b)
    if was == "druck":
        bau_druck(b)
    pruefe_seiten(b)
    return b.ende()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
