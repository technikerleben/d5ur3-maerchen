---
name: maerchen-deutsch-5
description: Materialien der Deutschreihe Märchen in Jahrgang 5 planen, erstellen und überarbeiten; Weiterschreiben eines vorgegebenen Märchenanfangs als roter Faden, A4-Satz (Übungsblätter auf A5 verkleinert, mindestens 14 pt), gesperrte Texte aus inhalt/texte.json mit Fußnoten, Lernbuddy als SRL-Tischrahmen beachten.
---

# Deutsch 5 · Märchen · Produktionsregeln

Stand: 18.10.2026. Übernimmt die Regeln aus `d5ur2-zootiere/skill.md` (Stand 08.10.2026), angepasst an die Märchenreihe.

## Vor jeder Arbeitssitzung lesen

1. Diese Datei
2. `planung/Rueckwaertsplanung.md` – Etappen, Blätter 1–11, Indikatoren E1.1–E5.5, Kapazität, Sprachspur
3. `planung/Projektgrundlage.md` – Zeitmodell W1–W6, Entscheidungen
4. `planung/Texte_Gate_C.md` und `inhalt/texte.json` – gesperrte Texte

Bei Widersprüchen gilt die jüngste Entscheidung von C, wie sie in den Planungsdateien unter „Entscheidungen C“ steht.

## Ziel und roter Faden

- Zielaufgabe der LEK (Typ 6): einen unbekannten, vorgegebenen Märchenanfang passend fortsetzen und zu Ende führen.
- Jede Etappe 1–4 hat zwei Pflichtblätter: **Blatt A** untersucht ein Märchen, **Blatt B** lässt einen vorgegebenen Anfang mit dem Schwerpunkt der Etappe weiterschreiben. Etappe 5: Blätter 9–11 (planen, schreiben, prüfen).
- Das Märchenbuch ist **Projekt P1** der Wahlzeit, kein Pflichtmaterial.

## SRL-Standard (unverändert aus Zootiere)

Etappen im eigenen Tempo: Input + inhaltsgleiches Merkblatt → Pflichtblätter mit freiwilliger Vertiefung → Gelingensnachweis (5 Indikatoren, Freigabe ab 4/5). Etappe 5 endet mit der Probearbeit (= fünfter Nachweis) → Feedback → Wahlzeit → LEK an einem von zwei Terminen.

- Lernbuddy = laminierter Tischrahmen; **nie auf Fachblättern nachbauen**. Begriffe: „Planung – Durchführung – Reflexion“, „Lösungsleiter“.
- Keine Mindestwortzahl, keine Punkte für Tempo oder SRL-Felder, Pflichtblätter nicht zur Wahl stellen, Vertiefungen nie als Hürde.
- Zeitangaben im Material als Woche und Einheit (W1–W6, Einheit 1/2), nie als Wochentag – das Material läuft klassenübergreifend.

## Texte (gesperrt seit 18.10.2026)

- Einzige Textquelle: `inhalt/texte.json`. Texte nur nach Rücksprache mit C ändern; danach `tools/build_texte.py` laufen lassen und alle Zeilenverweise prüfen.
- `sperre_pruefung: true` (Probearbeit, LEK, Training, Gelingensnachweise): Diese Texte erscheinen in keinem Übungsblatt, Merkblatt, Input, Kiosk oder der Lern-App.
- Rollen: Frau Holle = Beispielmärchen · Rumpelstilzchen = Bauplan (Blatt 5) · Weiße Schlange / Jorinde und Joringel = Etappe 5 · Goldene Gans = Probearbeit · Bienenkönigin / Drei Federn = LEK V1/V2 · Blaues Licht / Zertanzte Schuhe = Training · zwölf eigene Anfänge = Blatt 2, 4, 6, 8 und GN1–GN4 A/B.
- Kennzeichnung: „nach den Brüdern Grimm (KHM n), bearbeitet“ bzw. „Märchenanfang, ausgedacht“.

## Fußnoten (verbindlich)

- Schwierige und veraltete Ausdrücke erhalten in **allen Druckfassungen für Kinder** eine Fußnote am Seitenende. Quelle: `fussnoten` je Text in `inhalt/texte.json` (`stelle` = Wort oder Wendung, `erklaerung` = kurze, kindgerechte Erklärung).
- Die erste Fundstelle (ganzes Wort) bekommt die Fußnote; Nummern laufen durch den Text.
- Fußnoten mindestens 14 pt; Fußnotenzeichen 11 pt fett (einzige Ausnahme von der 14-pt-Regel).
- Erklärungen kurz, ohne neue schwierige Wörter; Wendungen erklären die Bedeutung im Satz („die Besinnung verlieren: ohnmächtig werden“).
- Ironie und alte Redewendungen ausdrücklich erklären (z. B. „Da hätte ich Lust …“).
- F-Fassungen: dieselben Fußnoten, bei Bedarf zusätzlich mit Bild.

## Märchenkarten (stellt C her)

41 Bildkarten in vier Kategorien (13 Figuren, 6 Orte, 10 Gegenstände, 12 Märchenmerkmale). Im Material nur als freiwilliger Hinweis erwähnen: *„Dir fehlt eine Idee? Deine Märchenkarten zeigen dir Figuren, Orte, Zauberdinge und Märchenmerkmale.“* Begriffe im Material folgen den Kartennamen (Liste in `planung/Rueckwaertsplanung.md`). Nicht erlaubt in Nachweisen, Probearbeit und LEK.

## Ausgabeformate (aus Zootiere übernommen)

| Material | Satz | Druck | Schrift |
|---|---|---|---|
| Input | HTML-Präsentation, eine Datei, offline | Beamer | groß; farbig im HBG-SRL-Schema |
| Merkblatt | A4 hoch | A4 Originalgröße | ≥ 12 pt |
| Übungsblätter, Weiterschreiben-Blätter, Märchentexte als Material | A4 hoch | **auf A5 verkleinert** | **≥ 14 pt** |
| Gelingensnachweis A/B | A4 mit Rückmeldeteil | A4 Originalgröße | Aufgaben ≥ 14 pt |
| Probearbeit, LEK | wie Gelingensnachweis | A4 Originalgröße | ≥ 14 pt |
| Wahlphase/Projekte, Reinschriftvorlage P1 | A4 | A4 Originalgröße | ≥ 12 pt |
| F-Material (1F–11F) | A4, ein Auftrag pro Kasten, Lösungsstreifen | auf A5 verkleinert | ≥ 14 pt (Grundschrift 16,5 pt) |

- Gedrucktes für Kinder: **Graustufen**, neutral, keine Maskottchen. Bilder: gemeinfreie Illustrationen oder KI-Bilder von C (im Bildnachweis als KI-generiert gekennzeichnet).
- Kopf-/Fußzeile: „Deutsch · Jahrgang 5 · Märchen“; keine Klassenbezeichnung.
- Schrift: Andika (SIL, OFL), eingebettet.
- Einfache, deutliche Du-Form; längere Texte ins Heft, bei Nachweisen und F-Material aufs Blatt.
- Pflicht = durchgezogener Rahmen „PFLICHT“; freiwillig = gestrichelt „FREIWILLIG“.

## Technik

```
inhalt/texte.json        gesperrte Texte mit Fußnoten (Gate C)
tools/satz.py            gemeinsame Hilfen: Schrift, Seitenumbruch mit Zeilennummern und Fußnoten, Schriftprüfung
tools/build_texte.py     Märchentexte A4 -> ausgabe/texte/<id>_A4.pdf, Zeilenbelege ausgabe/texte/zeilen.json
assets/fonts/            Andika
ausgabe/                 erzeugte Dateien (nie von Hand ändern)
```

Voraussetzungen: Python 3, `playwright` (Chromium), `pymupdf`. Jeder Generator prüft automatisch Seitenumbruch und Mindestschriftgröße; die Prüfausgabe wird gelesen, bevor committet wird. Zeilenangaben in Blättern, Kiosk und Erwartungshorizonten beziehen sich auf `ausgabe/texte/zeilen.json`.

Workflow für Änderungen: Inhaltsdatei ändern → Generator ausführen → Prüfausgabe lesen → gerenderte Seiten ansehen → committen. Deployment über Vercel aus `main` übernimmt C; keine Vercel-Einstellungen ändern.
