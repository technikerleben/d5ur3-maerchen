# Deutsch 5 · Märchen

Unterrichtsreihe 3 im Jahrgang 5 (Aufgabentyp 6, produktionsorientiertes Schreiben). Zeitraum: Anfang Dezember 2026 bis 15.01.2027, ohne Weihnachtsferien; 900 Minuten (180 in vollen, 90 in unvollständigen Wochen). Das Material wird klassenübergreifend im Jahrgang genutzt.

> **Aktuell: Fassung 4 (28.11.2026).** Etappe 1 Merkmale + GN1 (digital), Etappe 2 Spannungsbogen und spannend erzählen + GN2, dann Klassenarbeit „Ein Märchen zu Ende schreiben“ im Unterricht in eigenem Tempo (5 Anfänge ★–★★★, Abgabe des Rohentwurfs bis 13.01.), danach Schreibkonferenz ohne Note. Lernmaterial überwiegend von der Kollegin (`extern/`). Planung: [Fassung 4](planung/Fassung4.md) · Bau: `python3 tools/build_f4.py alles`, dann `python3 tools/build_f4_pakete.py` (Material der Kollegin im HBG-Design und vier Materialpakete; lokal, nicht im Repo).
>
> Vorher: **Fassung 3 (24.11.2026).** Teil 1 mit drei Etappen ab 09.12., Probearbeit am 22.12., Arbeit 3 am 13.01. (früh) und 20.01. (spät); Teil 2 unbenotet bis Halbjahresende; Sprache liest die Märchen freitags vorab. Planung: [Fassung 3](planung/Fassung3.md) · Bau: `python3 tools/build_f3.py alles` · GN1 digital: `apps/gn1-digital/index.html`. Fassung 1 und 2 bleiben als Archiv (Tags `fassung-1`, `fassung-2`).

**Zielaufgabe (LEK):** einen unbekannten, vorgegebenen Märchenanfang passend fortsetzen und zu Ende führen. Weiterschreiben ist der rote Faden aller fünf Etappen; das Märchenbuch ist Projekt P1 in der Wahlzeit.

## Planungsstand

| Gate | Inhalt | Stand |
|---|---|---|
| A | Rahmen: Zeit, Texte, Märchenbuch, Bilder | freigegeben 17.10.2026 |
| B | Rückwärtsplanung: Etappen, Indikatoren, Weiterschreiben-Blätter, Kapazität | freigegeben 17.10.2026 |
| C | Textauswahl und Bearbeitung der Grimm-Texte | abgeschlossen 18.10.2026; Texte gesperrt in `inhalt/texte.json` |
| D | Freigabe der Druckpakete je Etappe | Etappe 1 freigegeben 18.10.2026, Etappe 2–5 freigegeben 19.10.2026 |

## Planung

- [Workflow Materialproduktion](planung/Workflow_Materialproduktion.md) – Phasen, Gates, Lehren aus Zootiere
- [Projektgrundlage](planung/Projektgrundlage.md) – Entscheidungen, Zeitmodell W1–W6, Texte, Bilder, Märchenbuch
- [Textauswahl Gate C](planung/Texte_Gate_C.md) – Grimm-Texte, selbst verfasste Anfänge, Bearbeitungsregeln, „Frau Holle“
- [Texte](texte/) – neun bearbeitete Grimm-Texte und zwölf eigene Anfänge (gesperrt; maschinenlesbar: `inhalt/texte.json`)
- [Bildstil und Bildliste](planung/Bildstil.md) – Stil für KI-Bilder, zehn Motive mit Einsatzort
- **[Fassung 4 (aktuell)](planung/Fassung4.md) – 28.11.2026: GN1, GN2, Klassenarbeit mit 5 Anfängen in 3 Stufen, Material der Kollegin**
- [Fassung 3](planung/Fassung3.md) – Neuplanung 24.11.2026: Zeitplan, drei Etappen + Teil 2, Sprache parallel, GN1 digital**
- [Umbau-Workflow Fassung 2](planung/Umbau_Workflow.md) – Phasen U0–U6 für die verschlankte Reihe mit Tandems und Wocheninputs (geplant 14.11.2026)
- [Rückwärtsplanung Fassung 2 (Entwurf)](planung/Rueckwaertsplanung_F2.md) – 4 Etappen, Arbeit 3 als Ziel, J-W-A-D-D-A-A, Lesestrang
- [Rückwärtsplanung](planung/Rueckwaertsplanung.md) – fünf Etappen, Indikatoren E1.1–E5.5, Pflichtkern Blatt 1–11, Kapazität, Sprachspur, Textbedarf

## Technik (Phase 4)

- [Produktionsregeln](skill.md) – verbindlich für jede Materialarbeit
- `python3 tools/build_texte.py` – alle Märchentexte als A4-Schülerfassung mit Zeilennummern und Fußnoten → `ausgabe/texte/`, Zeilenbelege in `ausgabe/texte/zeilen.json`
- `python3 tools/build_material.py N` – Etappe N komplett, z. B. Etappe 1 → `ausgabe/etappe1/` (Input, Merkblatt, Blatt 1–2, Schülerpaket, GN1 A/B, Erwartungshorizont, Förder 1F–2F, GN1F A/B); Etappe 5 zusätzlich Checkliste K1–K5, Rückmeldekarte, Probearbeit mit Feedbackbogen und Erwartungshorizont, Probearbeit F
- `python3 tools/build_pruefung.py` – Lernerfolgskontrolle V1/V2 mit Bewertungsseite, LEK F, Erwartungshorizont, Training 1/2 und Musterfortsetzungen → `ausgabe/abschluss/`
- `python3 tools/build_wahlzeit.py` – Lernweg, Wahlhilfe, Projekte P1–P3, Reinschriftvorlage → `ausgabe/wahlzeit/`
- `python3 tools/build_kiosk.py` – Kontroll-Kiosk aus `inhalt/kiosk.json` (Zeilenangaben automatisch), prüft alle Ansichten im Browser
- `python3 tools/build_auswertung.py` – Auswertungs-App der LEK aus `inhalt/pruefung.json` (Vorlage `tools/vorlagen/auswertung_lek.html`), mit Rechenprüfung
- `python3 tools/build_pakete.py` – Druckpakete (Schüler, Nachweise, Förder, Lehrkraft, Digital) und Druckplan W1–W6
- `python3 tools/build_f4.py alles` – **Fassung 4** (aktuell): GN1 digital und Papier, Etappe 2 (Bilder im Kopf, GN2), Klassenarbeit (Auftrag, 5 Anfänge normal/F, Erwartungshorizonte, Bewertungsbogen), Inputs 1–5, Lernweg, Zeitplan, Druckanleitung → `ausgabe/f4/`
- `python3 tools/build_f3.py alles` – Fassung 3 (Archiv): Etappen 1–4, Inputs 1–5, Sprache 1–4, GN1 digital (`apps/gn1-digital/`, wird im Browser durchgespielt), Lerntheke, Raum, Lernweg F3, Zeitplan, Druckanleitungen → `ausgabe/f3/`
- `python3 tools/build_f2.py alles` – Fassung 2 (Archiv) (Umbau 11/2026): Etappenpakete, Wocheninputs, Lesebögen, Strategiekarten, Plakat, Lernweg → `ausgabe/f2/`; Material der Kollegin lokal in `extern/` (nicht im Repo)
- Voraussetzungen: Python 3, `playwright` (Chromium), `pymupdf`

## Materialstand

| Etappe | Stand |
|---|---|
| 1 Märchen erkennen | **freigegeben 18.10.2026** (Gate D) |
| 2 Figuren und Rollen verstehen | **freigegeben 19.10.2026** (Gate D) |
| 3 Märchen aufbauen | **freigegeben 19.10.2026** (Gate D) |
| 4 Märchensprache nutzen | **freigegeben 19.10.2026** (Gate D) |
| 5 Ein Märchen weiterschreiben, Probearbeit | **freigegeben 19.10.2026** (Gate D) (Probearbeit in einer Fassung) |

| Abschluss: LEK V1/V2 (+F), Training 1/2 mit Kiosk-Muster | erstellt 19.10.2026 (`python3 tools/build_pruefung.py` → `ausgabe/abschluss/`); Bewertung festgelegt 19.10.2026: K1–K6 je 0–4 Punkte nach Standard (24), Gewichtung ×2 möglich, Notengrenzen in Prozent |
| Wahlzeit: Lernweg (+F), Wahlhilfe, Projekte P1–P3, Reinschriftvorlage Märchenbuch | erstellt 19.10.2026 (`python3 tools/build_wahlzeit.py` → `ausgabe/wahlzeit/`) |
| Kontroll-Kiosk Blatt 1–11, Training 12–13 | erstellt 19.10.2026 (`python3 tools/build_kiosk.py` → `apps/kontroll-kiosk/index.html`, offline, ohne Kinderdaten) |
| Auswertungs-App LEK (K1–K6, 0–4 Punkte, Gewichtung, Notenschlüssel) | erstellt 19.10.2026 (`python3 tools/build_auswertung.py` → `apps/auswertung-lek/index.html`) |
| Druckpakete und Druckplan W1–W6 | erstellt 19.10.2026 (`python3 tools/build_pakete.py` → `ausgabe/pakete/`, ZIP nicht im Repo) |

## Grundlagen

- Jahresplanung Deutsch 5: <https://d5-jahresplanung.vercel.app/>
- Vorgängerreihe und technisches Muster: [d5ur2-zootiere](https://github.com/technikerleben/d5ur2-zootiere)
