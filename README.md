# Deutsch 5 · Märchen

Unterrichtsreihe 3 im Jahrgang 5 (Aufgabentyp 6, produktionsorientiertes Schreiben). Zeitraum: Anfang Dezember 2026 bis 15.01.2027, ohne Weihnachtsferien; 900 Minuten (180 in vollen, 90 in unvollständigen Wochen). Das Material wird klassenübergreifend im Jahrgang genutzt.

**Zielaufgabe (LEK):** einen unbekannten, vorgegebenen Märchenanfang passend fortsetzen und zu Ende führen. Weiterschreiben ist der rote Faden aller fünf Etappen; das Märchenbuch ist Projekt P1 in der Wahlzeit.

## Planungsstand

| Gate | Inhalt | Stand |
|---|---|---|
| A | Rahmen: Zeit, Texte, Märchenbuch, Bilder | freigegeben 17.10.2026 |
| B | Rückwärtsplanung: Etappen, Indikatoren, Weiterschreiben-Blätter, Kapazität | freigegeben 17.10.2026 |
| C | Textauswahl und Bearbeitung der Grimm-Texte | abgeschlossen 18.10.2026; Texte gesperrt in `inhalt/texte.json` |
| D | Freigabe der Druckpakete je Etappe | Etappe 1 freigegeben 18.10.2026 |

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
- `python3 tools/build_material.py N` – Etappe N komplett, z. B. Etappe 1 → `ausgabe/etappe1/` (Input, Merkblatt, Blatt 1–2, Schülerpaket, GN1 A/B, Erwartungshorizont, Förder 1F–2F, GN1F)
- Voraussetzungen: Python 3, `playwright` (Chromium), `pymupdf`

## Materialstand

| Etappe | Stand |
|---|---|
| 1 Märchen erkennen | **freigegeben 18.10.2026** (Gate D) |
| 2 Figuren und Rollen verstehen | erstellt 18.10.2026, Gate D offen |
| 3 Märchen aufbauen | erstellt 18.10.2026, Gate D offen |
| 4 Märchensprache nutzen | erstellt 18.10.2026, Gate D offen |
| 5 Ein Märchen weiterschreiben, Probearbeit | folgt |

## Grundlagen

- Jahresplanung Deutsch 5: <https://d5-jahresplanung.vercel.app/>
- Vorgängerreihe und technisches Muster: [d5ur2-zootiere](https://github.com/technikerleben/d5ur2-zootiere)
