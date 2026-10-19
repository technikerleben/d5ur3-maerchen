# Deutsch 5 · Märchen

Unterrichtsreihe 3 im Jahrgang 5 (Aufgabentyp 6, produktionsorientiertes Schreiben). Zeitraum: Anfang Dezember 2026 bis 15.01.2027, ohne Weihnachtsferien; 900 Minuten (180 in vollen, 90 in unvollständigen Wochen). Das Material wird klassenübergreifend im Jahrgang genutzt.

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
