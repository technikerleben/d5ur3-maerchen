#!/usr/bin/env python3
"""Fassung 3 (Neuplanung 24.11.2026): Teil 1 mit drei Etappen bis Arbeit 3, Teil 2 unbenotet, Sprache parallel.

    python3 tools/build_f3.py etappe 1      Etappenpaket, Nachweis, Förderpaket (Etappe 1–4)
    python3 tools/build_f3.py input 1       Input 1–5 (HTML) und Lehrkraft-Skript
    python3 tools/build_f3.py sprache [n]   Sprache-Termine 1–4: Lesebogen und Sprachblatt
    python3 tools/build_f3.py gn1           Gelingensnachweis 1 digital → apps/gn1-digital/index.html
    python3 tools/build_f3.py lerntheke     Strategiekarten und Märchen-Check
    python3 tools/build_f3.py raum          Plakat, Zonenschilder, Karte „Laut denken“, Lernweg
    python3 tools/build_f3.py druck [n]     Druckanleitung und Gesamt-PDF je Etappe (n = 1–4) und für Sprache (n = s)
    python3 tools/build_f3.py alles

Nutzt die Bausteine aus build_f2.py; Inhalte aus inhalt/f3/, Ausgabe nach ausgabe/f3/.
Fassung 2 (inhalt/f2, ausgabe/f2, build_f2.py) bleibt unverändert als Archiv (Git-Tag fassung-2).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pymupdf as fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_f2 as f2  # noqa: E402
from build_material import GN_CSS, TEXTE, doc, esc, md, verbinde  # noqa: E402
from satz import ROOT, font_css  # noqa: E402

IN = ROOT / "inhalt" / "f3"
AUS = ROOT / "ausgabe" / "f3"
L = lambda p: json.loads(p.read_text("utf-8"))  # noqa: E731

# Bausteine aus Fassung 2 auf die Inhalte der Fassung 3 umstellen
f2.IN, f2.AUS = IN, AUS
f2.STRAT = {k["id"]: k for k in L(IN / "strategien.json")["karten"]}
f2.RAUM = L(IN / "raum.json")
f2.CHECK = L(IN / "maerchen_check.json")
f2.PROBE = L(IN / "probearbeit.json")
f2.LESE = {w["woche"]: w for w in L(IN / "lesestrang.json")["wochen"]}
STRAT, RAUM, LESE = f2.STRAT, f2.RAUM, f2.LESE
SPRACHE = L(IN / "sprache.json")["termine"]
sym = f2.sym

_rueck_alt = f2.gn_rueckmeldung_html
f2.gn_rueckmeldung_html = lambda e, nw, v: _rueck_alt(e, nw, v).replace("weiter zu Etappe 5", "weiter mit Märchenbuch oder Vorlesen")
_check_alt = f2.check_html
f2.check_html = lambda: _check_alt().replace("Lerntheke · Etappe 4", "Lerntheke · Etappe 3")

TERMINE = [  # Plan Teil 1 (Entscheidungen 24.11.2026); für Lehrkraft-Seiten, nicht für Kinderblätter
    ("Fr 04.12.", "Sprache", "„Frau Holle“ im Lesetandem; danach Lernzeit (Vorbereitung später Zootiere-Termin 08.12. / Verben)"),
    ("Mi 09.12.", "Deutsch", "Input 1 · Etappe 1 Märchen erkennen"),
    ("Fr 11.12.", "Sprache", "„Rumpelstilzchen“ im Lesetandem · Verben im Präteritum"),
    ("Di 15.12.", "Deutsch", "Gelingensnachweis 1 (digital) · Input 2 · Etappe 2 Spannungsbogen"),
    ("Mi 16.12.", "Deutsch", "Input 3 · Etappe 3 ein Ende planen, schreiben, zu zweit prüfen"),
    ("Fr 18.12.", "Sprache", "„Die weiße Schlange“ (Anfang) im Lesetandem"),
    ("Di 22.12.", "Deutsch", "Probearbeit „Die goldene Gans“ (von Hand, unbenotet) · Korrektur in den Ferien"),
    ("Fr 08.01.", "Sprache", "„Jorinde und Joringel“: vorhersagen, Bilder im Kopf · Adjektive"),
    ("Di 12.01.", "Deutsch", "Feedback zur Probearbeit · Input 4 · gezielt üben, Training mit Zeitplan"),
    ("Mi 13.01.", "Deutsch", "Arbeit 3, früher Termin"),
    ("ab 19.01.", "Deutsch", "Teil 2 (unbenotet): Etappe 4 Bilder im Kopf, Märchenbuch, Vorlesen · parallel Vorbereitung später Termin"),
    ("Mi 20.01.", "Deutsch", "Arbeit 3, später Termin · Noten bis spätestens 27.01."),
]


# ------------------------------------------------------------ Inputs 1–5
def bau_input(b: f2.Bau, n: int):
    w = L(IN / "inputs" / f"i{n}.json")
    html = f2.input_html(w).replace("Woche %d · Input" % n, "Input %d" % n).replace("<title>Input W%d" % n, "<title>Input %d" % n)
    ziel = AUS / "inputs" / f"Input_{n}.html"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(html, encoding="utf-8")
    for vw, vh in ((1280, 800), (1024, 768)):
        pg = b.br.new_page(viewport={"width": vw, "height": vh})
        pg.goto(ziel.resolve().as_uri())
        pg.evaluate("document.fonts.ready")
        for _ in range(40):
            if pg.evaluate("(()=>{const f=document.querySelector('.folie.an');return f.scrollHeight>f.clientHeight+2||f.scrollWidth>f.clientWidth+2})()"):
                b.fehler.append("Input %d: Überlauf bei %dx%d auf Folie %s" % (n, vw, vh, pg.evaluate("f+1")))
                break
            pg.keyboard.press("ArrowRight")
        pg.close()
    b.bericht.append("%-40s Folien geprüft (1280×800, 1024×768)" % f"inputs/Input_{n}.html")
    sk = f2.skript_html(w).replace("Wocheninput W%d" % n, "Input %d" % n)
    b.mach(sk, AUS / "inputs" / f"Skript_Input_{n}_A4.pdf", f"Skript Input {n}", 12, 2)


# ------------------------------------------------------------ Sprache
def sprachblatt_html(t: dict) -> str:
    e = {"etappe": 0, "einzel": {"titel": t["titel"], "aufgaben": t["aufgaben"]}}
    return f2.einzel_html(e).replace("Etappe 0 · allein", "Sprache · Märchen %d" % t["n"])


def bau_sprache(b: f2.Bau, t: dict):
    aus = AUS / "sprache"
    lw = LESE[t["lesebogen"]]
    h = f2.lesebogen_html(lw).replace("Lesestrang · Woche %d · Lesetandem" % lw["woche"], "Sprache · Märchen %d · Lesetandem" % t["n"])
    b.mach(h, aus / f"Sprache_{t['n']}_Lesebogen_A4.pdf", f"Sprache {t['n']} · Lesebogen", 14, 1)
    if t["aufgaben"]:
        b.mach(sprachblatt_html(t), aus / f"Sprache_{t['n']}_Sprachblatt_A4.pdf", f"Sprache {t['n']} · Sprachblatt", 14, 2)


# ------------------------------------------------------------ GN1 digital
def gn1_digital() -> Path:
    d = L(IN / "gn1_digital.json")
    e1 = L(IN / "etappe1.json")
    ids = {x for v in d["varianten"].values() for x in (v["maerchen"], v["anfang"])}
    d["texte"] = {i: {k: f2.TEXTDB[i][k] for k in ("titel", "quelle", "text", "fussnoten") if k in f2.TEXTDB[i]} for i in ids}
    d["ziele"] = [{k: z[k] for k in ("id", "kind", "ueben")} for z in e1["nachweis"]["ziele"]]
    for v, var in d["varianten"].items():  # Abgleich mit den Indikatoren der Etappe
        if [a["ziel"] for a in var["aufgaben"]] != [z["id"] for z in d["ziele"]]:
            raise SystemExit("GN1 digital %s: Aufgaben passen nicht zu den Indikatoren" % v)
    vorlage = (ROOT / "tools" / "vorlagen" / "gn1_digital.html").read_text("utf-8")
    html = vorlage.replace("/*FONTS*/", font_css()).replace("/*DATEN*/null", json.dumps(d, ensure_ascii=False))
    ziel = ROOT / "apps" / "gn1-digital" / "index.html"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(html, encoding="utf-8")
    return ziel


def pruefe_gn1(b: f2.Bau, ziel: Path):
    """Spielt Variante A und B im Browser durch: einmal alles richtig (5/5), einmal nur falsch (0/5)."""
    d = L(IN / "gn1_digital.json")
    for v, var in d["varianten"].items():
        for richtig in (True, False):
            pg = b.br.new_page(viewport={"width": 1280, "height": 800})
            fehler = []
            pg.on("pageerror", lambda ex: fehler.append(str(ex)))
            pg.goto(ziel.resolve().as_uri())
            pg.evaluate("localStorage.clear()")
            pg.reload()
            pg.fill("#name", "Test")
            pg.click(f"[data-v={v}]")
            for a in var["aufgaben"]:
                if a["art"] == "zuordnen":
                    for i, s in enumerate(a["stellen"]):
                        w = s["richtig"][0] if richtig else next(o for o in a["optionen"] if o not in s["richtig"])
                        pg.click(f'[data-gruppe="s{i}"] .opt[data-w="{w}"]')
                elif a["art"] == "auswahl":
                    for i, f in enumerate(a["fragen"]):
                        w = f["richtig"] if richtig else next(o for o in f["optionen"] if o != f["richtig"])
                        pg.click(f'[data-gruppe="f{i}"] .opt[data-w="{w}"]')
                elif a["art"] == "ankreuzen":
                    for o in a["optionen"]:
                        if o["richtig"] == richtig:
                            pg.click(f'[data-gruppe="k"] .opt[data-w="{o["text"]}"]')
                elif a["art"] == "formeln":
                    pg.click(f'[data-gruppe="fo"] .opt[data-w="{a["formel"]["richtig"] if richtig else next(o for o in a["formel"]["optionen"] if o != a["formel"]["richtig"])}"]')
                    for w in a["woerter"]["liste"]:
                        if w["richtig"] == richtig:
                            pg.click(f'[data-gruppe="wo"] .opt[data-w="{w["text"]}"]')
                    if a.get("spruch"):
                        pg.click(f'[data-gruppe="sp"] .opt[data-w=\'{a["spruch"]["richtig"]}\']')
                elif a["art"] == "vorhersage":
                    pg.fill("#v1", "Ich vermute, dass etwas Zauberhaftes passiert, weil im Text steht, dass es klopfte.")
                    pg.fill("#v2", "Die Tochter öffnete die Tür. Draußen stand eine kleine Fee.")
                    pg.click("#pruefen")
                    for i in range(3):
                        pg.click(f'[data-gruppe="sp{i}"] .opt[data-w="{"ja" if richtig else "noch nicht"}"]')
                pg.click("#pruefen")
                pg.click("#next")
            txt = pg.inner_text("main")
            soll = "5 von 5" if richtig else "0 von 5"
            if soll not in txt or fehler:
                b.fehler.append("GN1 digital %s (%s): erwartet %s, JS-Fehler: %s" % (v, "richtig" if richtig else "falsch", soll, fehler))
            pg.close()
    b.bericht.append("%-40s Variante A/B je 5/5 und 0/5 durchgespielt" % "apps/gn1-digital/index.html")


# ------------------------------------------------------------ Raum: Plakat und Lernweg
def plakat_html() -> str:
    feld = lambda i, t, frei=False: "<div class='feld%s'>%s %s</div>" % (" frei" if frei else "", sym(i, 9), t)
    sp = ["<div class=spalte><h2>Start</h2><div class=w>Lernweg holen, Klammer beschriften</div>%s</div>" % feld("klammer", "Startklar")]
    for e in RAUM["etappen"][:3]:
        if e["n"] == 1:
            ff = feld("zwei", "zu zweit") + feld("eins", "allein") + feld("haken", "Nachweis am Laptop")
        elif e["n"] == 2:
            ff = feld("zwei", "zu zweit: Legeplan") + feld("eins", "allein: Schluss")
        else:
            ff = feld("zwei", "zu zweit planen") + feld("eins", "allein schreiben") + feld("zwei", "zu zweit prüfen") + feld("haken", "Probearbeit")
        sp.append("<div class=spalte><h2>Etappe %d</h2><div class=w>%s</div>%s</div>" % (e["n"], esc(e["titel"]), ff))
    sp.append("<div class=spalte><h2>Arbeit 3</h2><div class=w>Feedback lesen, üben</div>%s%s</div>" % (feld("uhr", "Training"), feld("stern", "Arbeit geschrieben")))
    sp.append("<div class=spalte><h2>Teil 2</h2><div class=w>nach der Arbeit</div>%s%s%s</div>" % (
        feld("auge", "Etappe 4 Bilder im Kopf", True), feld("buch", "Märchenbuch", True), feld("lesen", "Vorlesen", True)))
    return doc(f2.PLAKAT_CSS, (
        "<div style='display:flex;justify-content:space-between;align-items:flex-end'><h1>Wo stehe ich?</h1>"
        "<div style='font-size:18pt;max-width:55%%'>%s Häng deine Klammer an den Schritt, an dem du gerade arbeitest.<br>"
        "%s Partner gesucht? Arbeite mit einem anderen Kind, das gleich weit ist wie du.</div></div><div class=raster>%s</div>")
        % (sym("klammer", 9), sym("zwei", 9), "".join(sp)))


def lernweg_html() -> str:
    it = lambda i, t: "<span class=it>%s %s ☐</span>" % (sym(i, 6), t)
    E = {e["n"]: e for e in RAUM["etappen"]}
    rows = [
        "<tr><td><b>Etappe 1</b><br>%s</td><td>%s</td><td class=c>%s am Laptop<br>____ / 5</td><td class=c>%s</td></tr>" % (
            esc(E[1]["titel"]), it("zwei", "zu zweit") + it("eins", "allein") + it("plus", "frei"), sym("haken", 6), esc(E[1]["woche"])),
        "<tr><td><b>Etappe 2</b><br>%s</td><td>%s</td><td class=c>in der Probearbeit</td><td class=c>%s</td></tr>" % (
            esc(E[2]["titel"]), it("zwei", "zu zweit") + it("eins", "allein") + it("plus", "frei"), esc(E[2]["woche"])),
        "<tr><td><b>Etappe 3</b><br>%s</td><td>%s</td><td class=c>%s Probearbeit ☐</td><td class=c>%s</td></tr>" % (
            esc(E[3]["titel"]), it("zwei", "zu zweit planen") + it("eins", "allein schreiben") + it("zwei", "zu zweit prüfen"), sym("haken", 6), esc(E[3]["woche"])),
        "<tr><td><b>Vor der Arbeit</b></td><td>%s</td><td></td><td class=c>nach den Ferien</td></tr>" % (it("lesen", "Feedback lesen") + it("uhr", "Training")),
        "<tr><td><b>Arbeit 3</b></td><td>Mein Termin: ☐ früh &nbsp; ☐ spät</td><td></td><td class=c>Januar</td></tr>",
    ]
    teil2 = "<tr><td><b>Teil 2</b><br>ohne Note</td><td>%s</td><td class=c>%s A ☐ B ☐<br>____ / 5</td><td class=c>%s</td></tr>" % (
        it("auge", "Etappe 4 Bilder im Kopf") + it("buch", "Märchenbuch") + it("lesen", "Vorlesen"), sym("haken", 6), esc(E[4]["woche"]))
    spr = "".join("<td class=m><b>%d</b> ☐<br>%s</td>" % (t["n"], esc(f2.TEXTDB[LESE[t["lesebogen"]]["text"]]["titel"])) for t in SPRACHE)
    return doc(f2.LERNWEG_CSS, (
        "<div class=kopf2><div><div class=meta>Lernweg · Deutsch · Märchen</div><h1>Mein Weg durch die Märchen</h1></div></div>"
        "<div class=unterschrift style='margin-top:0;margin-bottom:3mm'><span>Name:</span><span>Klasse:</span></div>"
        "<div style='margin-bottom:2mm'><b>Mein Ziel:</b> %s</div>"
        "<h2 style='font-size:16pt;margin:2mm 0 1.5mm'>Teil 1 · bis zur Arbeit</h2>"
        "<table class=lw><tr><th style='width:40mm'>Etappe</th><th>Schritte im Paket</th><th style='width:33mm'>Nachweis</th><th style='width:27mm'>Richtwert</th></tr>%s</table>"
        "<h2 style='font-size:16pt;margin:4mm 0 1.5mm'>Teil 2 · nach der Arbeit</h2><table class=lw>%s</table>"
        "<h2 style='font-size:16pt;margin:4mm 0 1.5mm'>%s Im Fach Sprache lest ihr die Märchen vorher im Lesetandem</h2><table class=lw><tr>%s</tr></table>"
        "<div style='margin-top:2mm;font-size:14pt'>%s lesen · %s zu zweit · %s allein · %s freiwillig · %s Nachweis allein</div>")
        % (esc(RAUM["ziel"]), "".join(rows), teil2, sym("lesen", 6), spr, sym("lesen", 6), sym("zwei", 6), sym("eins", 6), sym("plus", 6), sym("haken", 6)))


def bau_raum(b: f2.Bau):
    b.mach(plakat_html(), AUS / "raum" / "Plakat_Wo_stehe_ich_A3.pdf", "Plakat", 14, 1)
    zs = [b.mach(f2.zone_html(z), AUS / "raum" / f"_zone_{z['name']}.pdf", "Zone", 14, 1) for z in RAUM["zonen"]]
    verbinde(zs, AUS / "raum" / "Zonenschilder_A4quer.pdf")
    for z in zs:
        z.unlink()
    b.mach(f2.satzstarter_html(), AUS / "raum" / "Karte_Laut_denken_A5.pdf", "Karte", 14, 1)
    b.mach(lernweg_html(), AUS / "raum" / "Lernweg_F3_A4.pdf", "Lernweg", 12, 1)
    b.mach(zeitplan_html(), AUS / "Zeitplan_F3_Lehrkraft_A4.pdf", "Zeitplan Lehrkraft", 12, 1)


def zeitplan_html() -> str:
    rows = "".join("<tr><td style='white-space:nowrap'><b>%s</b></td><td>%s</td><td>%s</td></tr>" % (esc(d), esc(f), esc(t)) for d, f, t in TERMINE)
    return doc(GN_CSS + "body{font-size:12.5pt}table{font-size:12.5pt}", (
        "<div class=meta>Lehrkraft · Fassung 3 · Stand 24.11.2026</div><h1>Zeitplan Märchen</h1>"
        "<p style='margin-bottom:3mm'><b>Prinzip:</b> Sprache liest die Märchen im Vorgriff (Lesetandem, Lesestrategien, Verben und Adjektive). "
        "Deutsch arbeitet danach an Inhalt, Merkmalen und Aufbau. Benotet wird nur Arbeit 3 (Zwischenstand); Teil 2 läuft ohne Note bis zum Halbjahresende.</p>"
        "<table><tr><th style='width:24mm'>Datum</th><th style='width:20mm'>Fach</th><th>Inhalt</th></tr>%s</table>"
        "<p style='margin-top:3mm'>Kinder, die früh geschrieben haben, beginnen nach dem 13.01. mit Teil 2; die übrigen bereiten sich auf den 20.01. vor.</p>") % rows)


# ------------------------------------------------------------ Druck
A5H = "A4 → A5 verkleinert, beidseitig, geheftet"
DRUCK_EXTERN = {
    1: ["Merkblatt Märchenmerkmale (Kollegin) – Lerntheke, A5"],
    2: ["Merkblatt Märchen-Spannungsbogen und Spannungsbogen universell (Kollegin) – Lerntheke"],
    3: ["Märchen-Schreibplan (Kollegin, 2 S.) – steckt im Etappenpaket; zusätzlich je Kind 1 zur Probearbeit und 1 zur Arbeit 3",
        "Märchen-Feedback Arbeit 3 (Kollegin) – je Kind 1 für die Probearbeit, 1 für die Arbeit",
        "Märchen-Lückentext (Kollegin) – steckt im Förderpaket 3; Wortspeicher als Lerntheken-Karte",
        "Arbeit 3, Termin 1 und 2 (Kollegin) – 13.01. und 20.01.",
        "Verbliste und Rechtschreib-Check (Kollegin) – Lerntheke; folgen noch",
        "Liniertes Papier für das Ende (Etappe 3, Probearbeit)"],
    4: ["Märchen-Lückentext (Kollegin): Wortspeicher als Lerntheken-Karte, A5", "Rechtschreib-Check (Kollegin) – Lerntheke; folgt noch"],
    "s": ["Verbliste (Kollegin) – für Märchen 2 (Präteritum); folgt noch"],
}
INPUTS = {1: [1], 2: [2], 3: [3, 4], 4: [5]}


def druck_liste(n) -> list[tuple]:
    if n == "s":
        r = []
        for t in SPRACHE:
            tid = LESE[t["lesebogen"]]["text"]
            r.append(("Sprache %d" % t["n"], f"sprache/Sprache_{t['n']}_Lesebogen_A4.pdf", "A4, einseitig", "je Lesetandem 1", "%s · %s" % (t["datum"], t["plan"])))
            r.append(("Sprache %d" % t["n"], f"../texte/{tid}_A4.pdf", A5H, "je Kind 1",
                      "Märchentext „%s“; die Kinder heben ihn auf – er steckt auch im Etappenpaket" % f2.TEXTDB[tid]["titel"] if t["n"] < 4 else "Märchentext; für Teil 2 aufheben"))
            if t["aufgaben"]:
                r.append(("Sprache %d" % t["n"], f"sprache/Sprache_{t['n']}_Sprachblatt_A4.pdf", A5H, "je Kind 1", t["titel"]))
        return r
    e = L(IN / f"etappe{n}.json")
    t = f2.TEXTDB[e["text"]]["titel"]
    r = []
    if n == 1:
        r.append(("1_Kinder", "raum/Lernweg_F3_A4.pdf", "A4, einseitig", "je Kind 1", "zu Beginn der Reihe; bleibt in der Mappe"))
    inhalt = "Deckblatt, „%s“, zu zweit%s, allein" % (t, " (mit Legeplan und Satzstreifen)" if e["gemeinsam"].get("legeplan") else
                                                      " (mit Arbeitsseite)" if e["gemeinsam"].get("arbeitsseite") else "")
    hinweis = "Reihenfolge: " + inhalt + "."
    if n == 1:
        hinweis += " Das Quiz der Kollegin hat zwei Exemplare auf einer Seite: halbieren, je Kind eine Hälfte."
    elif e.get("extern"):
        hinweis += " Der %s der Kollegin liegt zwischen „zu zweit“ und „allein“." % e.get("extern_name", "Vorlage")
    if e.get("anhang_check"):
        hinweis += " Hinten: Märchen-Check."
    if e["gemeinsam"].get("streifen"):
        hinweis += " Schere und Kleber bereitlegen."
    r.append(("1_Kinder", f"etappe{n}/Etappenpaket_{n}_A4.pdf", A5H, "je Kind 1", hinweis))
    art = e["nachweis"].get("art")
    if art == "probearbeit":
        r += [("2_Nachweise", f"etappe{n}/Probearbeit_A4.pdf", "A4, beidseitig", "je Kind 1",
               "am 22.12. für alle; dazu liniertes Papier, Schreibplan und Feedbackbogen der Kollegin"),
              ("3_Foerder", f"etappe{n}/Probearbeit_F_A4.pdf", "A4, beidseitig", "je F-Kind 1", "mit Schreibrahmen; Feedbackbogen der Kollegin")]
    elif e["nachweis"].get("varianten"):
        if n == 1:
            r.append(("2_Nachweise", f"etappe{n}/GN{n}_A_A4.pdf", "A4, beidseitig", "nur als Ersatz",
                      "GN1 läuft digital (apps/gn1-digital). Papier nur, wenn Laptops ausfallen."))
        else:
            r += [("2_Nachweise", f"etappe{n}/GN{n}_A_A4.pdf", "A4, beidseitig", "je Kind 1", "erst ausgeben, wenn das Kind die Schritte im Paket geschafft hat"),
                  ("2_Nachweise", f"etappe{n}/GN{n}_B_A4.pdf", "A4, beidseitig", "etwa ⅓ der Kinder", "Wiederholung nach dem Üben")]
    r.append(("3_Foerder", f"etappe{n}/foerder/Foerderpaket_{n}_A4.pdf", "A4 → A5 verkleinert, beidseitig", "je F-Kind 1",
              "Lösungsstreifen unten am Blatt umknicken" + ("; hinten der Lückentext der Kollegin" if e["foerder"].get("extern") else "")))
    if e["foerder"].get("nachweis"):
        r += [("3_Foerder", f"etappe{n}/foerder/GN{n}F_A_A4.pdf", "A4, beidseitig", "je F-Kind 1", ""),
              ("3_Foerder", f"etappe{n}/foerder/GN{n}F_B_A4.pdf", "A4, beidseitig", "nach Bedarf", "")]
    r += [("5_Lerntheke", f"lerntheke/Strategie_{k['id']}_A5.pdf", "A5 quer, einseitig, laminieren", "2–3 je Raum",
           "neue Strategiekarte: „%s“" % k["titel"]) for k in STRAT.values() if k.get("etappe", 1) == n]
    if n == 1:
        r += [("6_Raum", "raum/Plakat_Wo_stehe_ich_A3.pdf", "A3 quer (oder 2 × A4 zusammenkleben)", "je Raum 1", "Wäscheklammern mit Namen; Klassenübersicht und Partnersuche zugleich"),
              ("6_Raum", "raum/Zonenschilder_A4quer.pdf", "A4 quer, einseitig, laminieren", "je Raum 1 Satz", "Stillraum · Denkraum · Flur"),
              ("6_Raum", "raum/Karte_Laut_denken_A5.pdf", "A5 quer, laminieren", "je Tisch 1", ""),
              ("7_Lehrkraft", "Zeitplan_F3_Lehrkraft_A4.pdf", "A4", "1", "")]
    if e.get("anhang_check"):
        r.append(("5_Lerntheke", "lerntheke/Maerchen_Check_A4.pdf", "A4, laminieren", "2–3 je Raum", "steckt auch im Etappenpaket"))
    if art == "probearbeit":
        r.append(("7_Lehrkraft", f"etappe{n}/Probearbeit_Erwartungshorizont_A4.pdf", "A4", "1", ""))
    elif e["nachweis"].get("varianten"):
        r.append(("7_Lehrkraft", f"etappe{n}/GN{n}_Erwartungshorizont_A4.pdf", "A4", "1", ""))
    r += [("7_Lehrkraft", f"inputs/Skript_Input_{i}_A4.pdf", "A4", "1", "Input %d (höchstens 10 Minuten)" % i) for i in INPUTS[n]]
    return r


def druckanleitung_html(inv: list[tuple], n, start: int = 1) -> str:
    rows, seite = [], start
    for o, d, f, a, h, sz in inv:
        rows.append("<tr><td style='text-align:center'><b>%s</b></td><td style='word-break:break-all'>%s<br><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            "%d–%d" % (seite, seite + sz - 1) if sz > 1 else str(seite), esc(o), esc(Path(d).name), esc(f), esc(a), esc(h)))
        seite += sz
    titel = "Sprache (Märchen 1–4)" if n == "s" else "Etappe %d" % n
    digital = ("" if n == "s" else " · ".join("<b>Input_%d.html</b>" % i for i in INPUTS[n]) + ": Beamer (im Browser öffnen, F = Vollbild, Klick = nächster Gedanke)"
               + ("<br><b>apps/gn1-digital/index.html</b>: Gelingensnachweis 1 am Laptop (eine Datei, offline; die Lehrkraft nennt Variante A oder B)" if n == 1 else ""))
    extern = "".join("<li>%s</li>" % esc(x) for x in DRUCK_EXTERN.get(n, [])) or "<li>–</li>"
    raum = ("<li>Plakat aufhängen, Klammern mit Namen beschriften (Klammer startet bei „Start“).</li>"
            "<li>Zonenschilder an Stillraum, Denkraum und Flur; Karte „Laut denken“ auf die Tische.</li>"
            "<li>GN1 digital vorher auf einem Laptop testen; die Datei auf alle Laptops kopieren oder als Link bereitstellen.</li>") if n == 1 else ""
    h2 = "<h2 style='font-size:16pt;margin:4mm 0 1.5mm'>%s</h2>"
    return doc(GN_CSS + "body{font-size:12.5pt}table{font-size:12.5pt}td,th{padding:1.4mm 2mm}", "".join([
        "<div class=meta>Lehrkraft · Fassung 3 · %s</div><h1>Druckanleitung</h1>" % titel,
        "<div class=hinweis><b>So druckst du:</b> Pakete und Texte sind A4 gesetzt und werden <b>auf A5 verkleinert</b> gedruckt "
        "(2 Seiten pro Blatt, beidseitig, Heftung). Drucke dafür nur die angegebenen <b>Seiten im PDF</b>. Nachweise, Lesebogen und Lehrkraft-Seiten "
        "in <b>A4-Originalgröße</b>. Karten und Schilder laminieren. Alles ist für Graustufen gemacht.</div>",
        "<table style='table-layout:fixed'><tr><th style='width:20mm'>Seiten im PDF</th><th style='width:48mm'>Teil</th><th style='width:34mm'>Format</th>"
        "<th style='width:24mm'>Anzahl</th><th>Hinweis</th></tr>%s</table>" % "".join(rows),
        (h2 % "Digital" + "<p>%s</p>" % digital) if digital else "",
        h2 % "Vom Material der Kollegin (nicht im Paket, von ihren Originalen drucken)", "<ul style='margin-left:6mm'>%s</ul>" % extern,
        "" if n == "s" else h2 % "Vorbereitung im Raum" + "<ul style='margin-left:6mm'>%s<li>Lerntheke: neue Strategiekarten und Merkblätter der Kollegin dazulegen.</li></ul>" % raum]))


def bau_druck(b: f2.Bau, n):
    inv, fehlt = [], []
    for o, d, f, a, h in druck_liste(n):
        p = (AUS / d).resolve()
        if not p.exists():
            fehlt.append(d)
            continue
        inv.append((o, d, f, a, h, len(fitz.open(p))))
    if fehlt:
        b.fehler.append("Druckpaket %s: fehlt %s" % (n, ", ".join(fehlt)))
        return
    tag = "Sprache" if n == "s" else "Etappe%d" % n
    anl = AUS / f"Druckanleitung_F3_{tag}_A4.pdf"
    n_anl = 0
    for _ in range(3):
        b.mach(druckanleitung_html(inv, n, n_anl + 1), anl, "Druckanleitung", 12)
        neu = len(fitz.open(anl))
        if neu == n_anl:
            break
        n_anl = neu
        b.bericht.pop()
    gesamt = AUS / f"Gesamtpaket_F3_{tag}.pdf"
    seiten = verbinde([anl] + [(AUS / d).resolve() for _, d, *_ in inv], gesamt)
    if seiten != n_anl + sum(x[5] for x in inv):
        b.fehler.append("Gesamt-PDF %s: Seitenzahl stimmt nicht" % tag)
    b.bericht.append("%-40s %d S. (Anleitung %d S. + %d Teile), %.1f MB" % (gesamt.name, seiten, n_anl, len(inv), gesamt.stat().st_size / 1e6))


# ------------------------------------------------------------ main
def main(argv: list[str]) -> int:
    was = argv[0] if argv else "alles"
    arg = argv[1] if len(argv) > 1 else None
    b = f2.Bau()
    if was in ("etappe", "alles"):
        for n in ([int(arg)] if arg else [1, 2, 3, 4]):
            f2.bau_etappe(b, n)
    if was in ("input", "alles"):
        for n in ([int(arg)] if arg else [1, 2, 3, 4, 5]):
            bau_input(b, n)
    if was in ("sprache", "alles"):
        for t in SPRACHE:
            if not arg or int(arg) == t["n"]:
                bau_sprache(b, t)
    if was in ("gn1", "alles"):
        pruefe_gn1(b, gn1_digital())
    if was in ("lerntheke", "alles"):
        f2.bau_lerntheke(b)
    if was in ("raum", "alles"):
        bau_raum(b)
    if was in ("druck", "alles"):
        for n in ([arg if arg == "s" else int(arg)] if arg else [1, 2, 3, 4, "s"]):
            bau_druck(b, n)
    return b.ende()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
