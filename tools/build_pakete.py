#!/usr/bin/env python3
"""Druckpakete und Druckplan W1–W6.

Vorher alle Einzel-PDFs erzeugen:
    python3 tools/build_texte.py
    for n in 1 2 3 4 5; do python3 tools/build_material.py $n; done
    python3 tools/build_pruefung.py
    python3 tools/build_wahlzeit.py
    python3 tools/build_kiosk.py
    python3 tools/build_auswertung.py
Dann:
    python3 tools/build_pakete.py   → ausgabe/pakete/ (Ordner + ZIP) und ausgabe/pakete/Druckplan_W1-W6_A4.pdf
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import pymupdf as fitz
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_material import doc, drucke, esc  # noqa: E402
from satz import ROOT  # noqa: E402

A = ROOT / "ausgabe"
OUT = A / "pakete"

# Format-Kürzel
A5 = "A5"      # A4 gesetzt → A5 verkleinert, beidseitig
A4 = "A4"      # A4 Originalgröße, beidseitig
A4E = "A4 e"   # A4 Originalgröße, einseitig

# (Ordner im Paket, Dateiname im Paket, Quelle relativ zu ausgabe/ oder ROOT, Format, Anzahl)
PAKETE = [
    # Schüler
    ("1_schueler", "00_Lernweg_A4.pdf", "wahlzeit/Lernweg_Maerchen_A4.pdf", A4E, "je Kind 1"),
    *[("1_schueler", f"0{n}_Schuelerpaket_Etappe{n}_A4.pdf", f"etappe{n}/Schuelerpaket_Etappe{n}_A4.pdf", A5, "je Kind 1") for n in range(1, 6)],
    *[("1_schueler", f"0{n}_Merkblatt_{n}_A4.pdf", f"etappe{n}/Merkblatt_{n}_A4.pdf", A4, "je Kind 1") for n in range(1, 6)],
    ("1_schueler", "06_Wahlhilfe_A4.pdf", "wahlzeit/Wahlhilfe_A4.pdf", A5, "je Kind 1"),
    ("1_schueler", "07_Projekte_P1-P3_A4.pdf", "wahlzeit/Projekte_P1-P3_A4.pdf", A5, "je Tisch 1 Satz"),
    ("1_schueler", "08_Reinschrift_Maerchenbuch_A4.pdf", "wahlzeit/Reinschrift_Maerchenbuch_A4.pdf", A4E, "nach Bedarf (P1)"),
    # Nachweise
    *[("2_nachweise", f"GN{n}_{v}_A4.pdf", f"etappe{n}/GN{n}_{v}_A4.pdf", A4, "je Kind 1" if v == "A" else "ca. ⅓ der Kinder")
      for n in range(1, 5) for v in "AB"],
    ("2_nachweise", "Probearbeit_A4.pdf", "etappe5/Probearbeit_A4.pdf", A4, "je Kind 1"),
    ("2_nachweise", "Training_1_A4.pdf", "abschluss/Training_1_A4.pdf", A4, "je Kind 1"),
    ("2_nachweise", "Training_2_A4.pdf", "abschluss/Training_2_A4.pdf", A4, "je Kind 1"),
    ("2_nachweise", "LEK_V1_A4.pdf", "abschluss/LEK_V1_A4.pdf", A4, "Kinder früher Termin"),
    ("2_nachweise", "LEK_V2_A4.pdf", "abschluss/LEK_V2_A4.pdf", A4, "Kinder später Termin"),
    # Förder
    ("3_foerder", "00_Lernweg_F_A4.pdf", "wahlzeit/Lernweg_Maerchen_F_A4.pdf", A4E, "je F-Kind 1"),
    *[("3_foerder", f"0{n}_Foerder_Etappe{n}_A4.pdf", f"etappe{n}/foerder/Foerder_Etappe{n}_A4.pdf", A5, "je F-Kind 1") for n in range(1, 6)],
    *[("3_foerder", f"GN{n}F_{v}_A4.pdf", f"etappe{n}/foerder/GN{n}F_{v}_A4.pdf", A4, "je F-Kind 1") for n in range(1, 5) for v in "AB"],
    ("3_foerder", "Probearbeit_F_A4.pdf", "etappe5/foerder/Probearbeit_F_A4.pdf", A4, "je F-Kind 1"),
    ("3_foerder", "LEK_V1F_A4.pdf", "abschluss/foerder/LEK_V1F_A4.pdf", A4, "je F-Kind (Termin)"),
    ("3_foerder", "LEK_V2F_A4.pdf", "abschluss/foerder/LEK_V2F_A4.pdf", A4, "je F-Kind (Termin)"),
    # Lehrkraft
    *[("4_lehrkraft", f"GN{n}_Erwartungshorizont_A4.pdf", f"etappe{n}/GN{n}_Erwartungshorizont_A4.pdf", A4, "1") for n in range(1, 5)],
    ("4_lehrkraft", "Probearbeit_Erwartungshorizont_A4.pdf", "etappe5/Probearbeit_Erwartungshorizont_A4.pdf", A4, "1"),
    ("4_lehrkraft", "LEK_Erwartungshorizont_A4.pdf", "abschluss/LEK_Erwartungshorizont_A4.pdf", A4, "1"),
    ("4_lehrkraft", "Training_1_Muster_A4.pdf", "abschluss/Training_1_Muster_A4.pdf", A4, "1 (Kiosk-Ordner)"),
    ("4_lehrkraft", "Training_2_Muster_A4.pdf", "abschluss/Training_2_Muster_A4.pdf", A4, "1 (Kiosk-Ordner)"),
    # Digital
    *[("5_digital", f"Input_Etappe{n}.html", f"etappe{n}/Input_Etappe{n}.html", "Beamer", "–") for n in range(1, 6)],
    ("5_digital", "Kontroll-Kiosk.html", "@apps/kontroll-kiosk/index.html", "Laptop im Raum", "–"),
    ("5_digital", "Auswertung_LEK.html", "@apps/auswertung-lek/index.html", "Lehrkraft-Rechner", "–"),
]

# Druckplan: Woche → Einträge (was, Dateien, Hinweis)
PLAN = [
    ("W1 · 180 Min.", "Reihenstart, Etappe 1 und 2", [
        ("Lernweg", "1_schueler/00_Lernweg_A4.pdf", "vor der ersten Stunde"),
        ("Schülerpaket 1 + Merkblatt 1", "1_schueler/01_…, 01_Merkblatt_1", "vor der ersten Stunde"),
        ("Schülerpaket 2 + Merkblatt 2", "1_schueler/02_…, 02_Merkblatt_2", "bis Ende W1 bereitlegen (schnelle Kinder)"),
        ("GN1 A, GN2 A (+ B als Reserve)", "2_nachweise/GN1_*, GN2_*", "in der Nachweis-Box"),
        ("Förder 1–2, GN1F/GN2F, Lernweg F", "3_foerder/…", "je F-Kind"),
        ("Erwartungshorizont GN1/GN2", "4_lehrkraft/…", "Lehrkraft"),
    ]),
    ("W2 · 180 Min.", "Etappe 2 und 3", [
        ("Schülerpaket 3 + Merkblatt 3", "1_schueler/03_…", "bis Mitte W2"),
        ("GN3 A (+ B)", "2_nachweise/GN3_*", "Nachweis-Box"),
        ("Förder 3, GN3F", "3_foerder/…", "je F-Kind"),
    ]),
    ("W3 · 180 Min.", "Etappe 4 und 5", [
        ("Schülerpaket 4 + 5, Merkblatt 4 + 5", "1_schueler/04_…, 05_…", "Checkliste und Rückmeldekarten sind im Paket 5"),
        ("GN4 A (+ B)", "2_nachweise/GN4_*", "Nachweis-Box"),
        ("Förder 4–5, GN4F", "3_foerder/…", "je F-Kind"),
        ("Probearbeit + Probearbeit F", "2_nachweise/Probearbeit_A4.pdf, 3_foerder/Probearbeit_F_A4.pdf", "für Fenster A in W4 bereitlegen"),
    ]),
    ("W4 · 90 Min. (21.–22.12.)", "Probearbeit Fenster A", [
        ("Probearbeit (Fenster A)", "2_nachweise/Probearbeit_A4.pdf", "nur Kinder mit GN1–GN4"),
        ("Erwartungshorizont Probearbeit", "4_lehrkraft/…", "Korrektur in den Ferien"),
    ]),
    ("W5 · 90 Min. (07.–08.01.)", "Feedback, Training, Fenster B", [
        ("Feedbackbögen zurückgeben", "– (letzte Seite der Probearbeit)", "mit Wahlhilfe"),
        ("Wahlhilfe", "1_schueler/06_Wahlhilfe_A4.pdf", "je Kind"),
        ("Training 1 und 2", "2_nachweise/Training_*", "Muster in den Kiosk-Ordner"),
        ("Probearbeit (Fenster B)", "2_nachweise/Probearbeit_A4.pdf", "Restliche Kinder"),
    ]),
    ("W6 · 180 Min.", "LEK früh/spät, Wahlzeit", [
        ("LEK V1 (früher Termin)", "2_nachweise/LEK_V1_A4.pdf", "Anzahl nach Terminwahl"),
        ("LEK V2 (später Termin)", "2_nachweise/LEK_V2_A4.pdf", "Anzahl nach Terminwahl"),
        ("LEK F", "3_foerder/LEK_V*F_A4.pdf", "je F-Kind"),
        ("Projekte P1–P3, Reinschriftvorlage", "1_schueler/07_…, 08_…", "Wahlzeit, Vorleserunde"),
        ("Auswertung", "5_digital/Auswertung_LEK.html", "Rückmeldung zweiseitig drucken"),
    ]),
]

PLAN_CSS = """
body{font-size:12.5pt;line-height:1.32}
h1{font-size:22pt}h2{font-size:15pt;margin:4mm 0 1.5mm;break-after:avoid}
table{width:100%;border-collapse:collapse;margin-bottom:2mm}tr{break-inside:avoid}td,th{border:1pt solid #111;padding:1mm 2mm;vertical-align:top;text-align:left}
.inv td,.inv th{padding:.6mm 2mm}.f{width:14mm}
th{background:#eee}.w{width:52mm}.n{width:12mm;text-align:right}
.hinweis{border:1.5pt solid #111;border-radius:2mm;padding:2mm 3mm;margin:2mm 0 3mm}
"""


def seiten(p: Path) -> int | None:
    return len(fitz.open(p)) if p.suffix == ".pdf" else None


def plan_html(inventar: list[tuple]) -> str:
    teile = ["<div class=meta>Lehrkraft · Deutsch · Jahrgang 5 · Märchen</div><h1>Druckplan W1–W6</h1>",
             "<div class=hinweis><b>Eigenes Tempo:</b> Schülerpakete eine Etappe im Voraus bereitlegen, damit schnelle Kinder nicht warten. "
             "Nachweise A je Kind, B als Reserve (etwa ein Drittel). Material ist jahrgangsweit nutzbar; Anzahl je Lerngruppe eintragen.<br>"
             "<b>Formate:</b> Schülerpakete, Wahlhilfe und Projekte sind A4 gesetzt und werden auf A5 verkleinert gedruckt. "
             "Merkblätter, Nachweise, Probearbeit, Training und LEK in A4-Originalgröße. Lernweg und Reinschriftvorlage einseitig.<br>"
             "<b>Kürzel im Inventar:</b> A5 = A4 gesetzt, auf A5 verkleinert, beidseitig · A4 = Originalgröße, beidseitig · A4 e = Originalgröße, einseitig.</div>"]
    for woche, thema, eintraege in PLAN:
        teile.append("<h2>%s – %s</h2><table><tr><th class=w>Was</th><th>Datei im Paket</th><th>Hinweis</th><th class=n>Anzahl</th></tr>%s</table>" % (
            esc(woche), esc(thema), "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td class=n></td></tr>" % (esc(a), esc(b), esc(c)) for a, b, c in eintraege)))
    teile.append("<h2 style='break-before:page'>Inventar der Pakete</h2><table class=inv><tr><th>Datei</th><th class=f>Format</th><th class=n>Seiten</th><th>Anzahl</th></tr>%s</table>" % "".join(
        "<tr><td>%s/%s</td><td class=f>%s</td><td class=n>%s</td><td>%s</td></tr>" % (esc(o), esc(n), esc(f), s if s else "–", esc(a)) for o, n, f, s, a in inventar))
    return doc(PLAN_CSS, "".join(teile))


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    inventar, fehlt = [], []
    for ordner, name, quelle, fmt, anzahl in PAKETE:
        src = ROOT / quelle[1:] if quelle.startswith("@") else A / quelle
        if not src.exists():
            fehlt.append(quelle)
            continue
        ziel = OUT / ordner / name
        ziel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, ziel)
        inventar.append((ordner, name, fmt, seiten(ziel), anzahl))
    if fehlt:
        print("FEHLT:", *fehlt, sep="\n  ")
        return 1
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page()
        mn = drucke(pg, plan_html(inventar), OUT / "Druckplan_W1-W6_A4.pdf", "Druckplan")
        br.close()
    with zipfile.ZipFile(OUT / "Druckpakete_Maerchen.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file() and f.suffix != ".zip":
                z.write(f, f.relative_to(OUT))
    blaetter = sum(s or 0 for *_, s, _ in inventar)
    print("Pakete: %d Dateien, %d PDF-Seiten; Druckplan %d S., min %.1f pt; ZIP %.1f MB" % (
        len(inventar), blaetter, len(fitz.open(OUT / "Druckplan_W1-W6_A4.pdf")), mn, (OUT / "Druckpakete_Maerchen.zip").stat().st_size / 1e6))
    return 0 if mn >= 12 else 1


if __name__ == "__main__":
    sys.exit(main())
