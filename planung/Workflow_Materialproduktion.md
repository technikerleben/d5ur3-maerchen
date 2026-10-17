# Workflow Materialproduktion · Deutsch 5 · ab Reihe 3 „Märchen“

Stand: 17.10.2026 · abgeleitet aus dem Repo `technikerleben/d5ur2-zootiere` (Stand 11.10.2026) und der Jahresplanung `d5-jahresplanung.vercel.app` (Arbeitsstand 01.10.2026).

## 0 · Was aus Zootiere übernommen wird – und was gelernt wurde

**Bewährt und verbindlich übernehmen**

- SRL-Standard: Etappen im eigenen Tempo · Startinput + inhaltsgleiches Merkblatt → Pflichtblätter mit freiwilliger Vertiefung → Gelingensnachweis mit 5 Indikatoren, Freigabe ab 4/5 → letzte Etappe endet mit Probearbeit → Feedback → Wahlzeit (Projekte, Wiederholung, Vertiefungen) → Lernerfolgskontrolle an einem von zwei Wahlterminen.
- Eine Inhaltsquelle pro Etappe (`inhalt/etappeN.json`), aus der Input (HTML) und Merkblatt (PDF) erzeugt werden; geändert wird nur in `inhalt/`, nie in den Ausgaben.
- Generatoren mit eingebauten Prüfungen (Seitenüberlauf, Schrift ≥ 14 pt, Input = Merkblatt, Links, Kiosk-Ansichten).
- Formate laut `skill.md` vom 08.10.2026: A4 gesetzt, Übungsblätter auf A5 verkleinert (passt in die Mitte des Lernbuddys), Graustufen, neutral ohne Maskottchen, Andika eingebettet, HTML farbig im HBG-SRL-Schema.
- Lernbuddy wird nie auf Fachblättern nachgebaut; Begriffe „Planung – Durchführung – Reflexion“ und „Lösungsleiter“.
- Zieldifferentes F-Material parallel (gleiche Etappen, Blattnummern mit F, Lösungsstreifen).
- `WISSENSBASIS.md` + `skill.md` als Einstieg für jede Arbeitssitzung.

**Lehren aus dem Verlauf (vermeidbare Nacharbeit)**

| Was geschah | Folge | Regel für Märchen |
|---|---|---|
| Format während der Produktion gewechselt (A5-Satz → A4 verkleinert, 08.10.) | ältere Ausgaben unter `materialien/` nur noch Vorfassungen, Generatoren doppelt | Formate in Phase 1 festlegen, danach einfrieren |
| Gestaltung gewechselt (Otter/Dino-Bildfassung → neutral) | Bildfassung Etappe 1 verworfen | Gestaltung vor dem ersten Druckpaket entscheiden |
| Textbasis gewechselt (Sachtext/Steckbrief → Interviews, 10.10.) | Blätter, Zeilenverweise, Kiosk nachgezogen | Textkorpus (Phase 2) vor allen Blättern sperren |
| SRL-Standard erst nach Materialbeginn fixiert (30.09.) | „Vorfassungen“-Kennzeichnung nötig | Standard steht jetzt – nur übernehmen |
| Offene Punkte zu Prüfungen bis zuletzt (Zeit, Punkte, Notengrenzen) | Klassenarbeit spät fertig | Prüfungsrahmen in Phase 1 mitplanen |

## 1 · Phase 1 · Rahmen festlegen (Entscheidungsblatt, vor jedem Material)

Ergebnis: `planung/Projektgrundlage.md` mit allen Festlegungen. **Gate A: C gibt frei.**

1. Zeitrahmen: Wochen, Doppelstunden, Lage der zwei LEK-Termine (Märchen hat fünf statt drei Etappen).
2. Zielaufgabe/LEK aus der Jahresplanung: unbekannten Märchenanfang passend fortsetzen und zu Ende führen (Typ 6).
3. Kompetenzraster K1–K5 übernehmen, um Förderstandard ergänzen (wie Zootiere: vier Standards).
4. Lernprodukt Klassen-Märchenbuch: Form (Heftseiten, Druckheft, digital), wer sammelt, was überarbeitet wird.
5. Formate und Gestaltung: Zootiere-`skill.md` übernehmen; nur Abweichungen notieren (z. B. gemeinfreie Illustrationen erlaubt?).
6. Prüfungsrahmen: Arbeitszeit Probearbeit/LEK, erlaubte Hilfen, Punkteverteilung, Notengrenzen, Nachteilsausgleich.
7. Zieldifferenz: Anzahl Kinder, F-Fassungen ja/nein je Material.
8. Begleitprodukte: Kiosk, Lern-App, Erklärvideos (wie Wunschbriefe), Materialboard – was ist Pflicht, was später.

## 2 · Phase 2 · Rückwärtsplanung

Ergebnis: `planung/Etappen_Gelingensnachweise.md`, `planung/Materialmatrix.md`, `planung/Sprachspur_Maerchen_Feinplanung.md`, `materialien/kompetenzen_etappen.json`. **Gate B: C gibt frei.**

1. Von der LEK zurück: Welche Teilkompetenzen müssen bis zur Probearbeit gezeigt sein?
2. Je Etappe genau fünf Indikatoren mit Erfüllungskriterien (E1.1–E5.5); jeder Indikator wird im Pflichtkern geübt.
3. Gelingensnachweise zuerst skizzieren, dann die Pflichtblätter darauf ausrichten (Abdeckungstabelle Indikator ↔ Blatt).
4. Materialmatrix: Input-/Merkblatt-Abschnitte je Etappe, Pflichtblätter mit Nummern, Vertiefungen, Hilfen, Buchtext-Auftrag je Etappe, Zeitansätze.
5. Sprachspur verteilen (Präteritum, Präsens ↔ Präteritum, Verbformen, wörtliche Rede, Pronomen, Konjunktionen); Einstieg mit dem Vergleich *Der Otter lebt am Fluss. / Der König lebte in einem großen Schloss.*; keine eigene Grammatik-Etappe, höchstens eine Sprachaufgabe pro Blatt.
6. Kapazitätsprüfung Doppelstunde für Doppelstunde (Raumzeit, Flexbudget, Probearbeits- und LEK-Fenster) wie in Zootiere Abschnitt 7.

## 3 · Phase 3 · Textkorpus festlegen und sperren

Ergebnis: `inhalt/texte.json` (Gegenstück zu `interviews.json`), Zeilenbelege. **Gate C: Texte gesperrt – danach keine Textänderung ohne Nachziehen aller Zeilenverweise.**

| Rolle (Zootiere-Entsprechung) | Märchen |
|---|---|
| Beispieltier Fischotter | ein durchgehendes Beispielmärchen für Inputs, Merkblätter, Blätter und GN |
| Übungstiere | zwei Übungsmärchen zur Wahl (Etappe 4–5) |
| Probearbeit Waschbär | neuer Märchenanfang, nicht vorgeübt |
| Klassenarbeit Biber / Nashorn | zwei gleichwertige unbekannte Märchenanfänge |
| Training Antilopen | zwei Trainingsanfänge mit Musterfortsetzungen (Mindest-/Regelstandard) |
| Förder-Kurzinterviews | Kurzfassungen in einfacher Sprache |

- Gemeinfreie Grimm-Texte (Ausgabe letzter Hand) als Basis, für Jahrgang 5 behutsam bearbeitet; Bearbeitung kennzeichnen, Quelle angeben. Märchenanfänge für Prüfungen ggf. selbst verfasst.
- Markup wie bei Zootiere: `[[Stelle|Kürzel]]` für unsichtbare Belege, z. B. F Formel, Z Zahl, H Held, G Gegenspieler, W Helfer/Zauber, P Prüfung, L Lösung.
- Zeilennummern alle 5 Zeilen; `zeilen.json` erzeugen.

## 4 · Phase 4 · Repo und Werkzeuge

Ergebnis: Repo `d5ur3-maerchen` lauffähig, leere Etappe baut fehlerfrei.

1. Neues Repo aus Zootiere ableiten: `tools/`, `assets/fonts`, `skill.md`, `inhalt/`-Schema, `build_wissensbasis.py`, `build_anleitung.py`, `build_pakete.py`.
2. Generatoren verallgemeinern: Etappenzahl aus der Inhaltsquelle statt fest 3; Interview-Renderer → Textrenderer für Märchen; Tier-spezifische Begriffe entfernen.
3. Neuer Baustein „Märchenbuch-Seite“ (Buchtext je Etappe, A4 Originalgröße oder Heft).
4. `skill.md` für Märchen anpassen (Rollen der Texte, Buchtext, Sprachspur), `WISSENSBASIS.md` erzeugen.
5. Deploy-Struktur wie bisher (Vercel aus `main`, statisch, Einstellungen macht C).

## 5 · Phase 5 · Etappenproduktion (Schleife je Etappe)

**Etappe 1 komplett als Muster bauen, freigeben, erst dann Etappen 2–5.**

| Schritt | Ergebnis | Prüfung |
|---|---|---|
| 1 Inhaltsquelle | `inhalt/etappeN.json`: Input-/Merkblatt-Abschnitte mit gesicherten Antworten, Pflichtblätter, Sprachdetektiv, Vertiefungen, Buchtext-Auftrag, GN A/B mit 5 Indikatoren | Abdeckungstabelle aus Phase 2 |
| 2 Erzeugen | `python tools/build_material.py N` → Input, Merkblatt, Übungsblätter, Hilfen, GN A/B | automatische Prüfausgabe fehlerfrei |
| 3 Sichtprüfung | gerenderte Seiten ansehen (A5-Lesbarkeit, Lochrand, Pflicht/freiwillig erkennbar) | Seitenbilder |
| 4 Kiosk | `inhalt/kiosk.json`: Tipps und Lösungen; offene Aufgaben nur mit Vergleichsbeispielen | `build_kiosk.py` mit Browsertest |
| 5 F-Fassung | `inhalt/foerder_etappeN.json`, GN-F | `build_foerder.py N` |
| 6 Freigabe | **Gate D: C sieht Druckpaket durch** | Rückmeldung in `inhalt/` einarbeiten |
| 7 Abschluss | Commit, `WISSENSBASIS.md` und `anleitung.html` neu erzeugen | Linkprüfung |

Kreative Schreibaufträge: Buchtexte sind Lernprodukte, nicht Nachweise; GN und Probearbeit bleiben Lernunterlagen.

## 6 · Phase 6 · Abschluss und Prüfungen

1. Probearbeit (neuer Märchenanfang) im Aufbau der LEK, Feedbackbogen mit 5 Indikatoren, F-Fassung.
2. Zwei gleichwertige LEK-Varianten + F, Erwartungshorizont K1–K5, Bewertungsseite; Auswertungs-App aus Zootiere übernehmen und auf K1–K5 umstellen.
3. Training vor der LEK (zwei Anfänge, Musterfortsetzungen im Kiosk).
4. Wahlphase: drei Projekte (Vorschlag: Märchenbuch gestalten · Märchen gestaltend vorlesen/Hörszene · Märchen umformen), Wiederholungshilfe, Strategiekarten, Lernweg (+F).

## 7 · Phase 7 · Ausgabe und Begleitung

1. Druckpakete Schüler/Lehrkraft + ZIP (`build_pakete.py`), Druckplan je Doppelstunde.
2. Lehrkraft-Leitfaden `anleitung.html`, Materialboard, Ablauf-Animation.
3. Optional: Lern-App-Erweiterung, Erklärvideos zu den fünf Inputs (VoiceOver-Texte aus derselben Inhaltsquelle ableiten).
4. Jahresplanung aktualisieren (Status Märchen, Link zum Repo).

## 8 · Phase 8 · Erprobung und Rückkopplung

Nach jeder Etappe im Unterricht: Zeitbedarf, Stolperstellen, GN-Quote notieren → Änderungen nur in `inhalt/` → neu erzeugen. Nach der Reihe: Lehren in diesen Workflow zurückschreiben, bevor Reihe 4 („Spannend erzählen“) startet.

## Arbeitsweise mit Claude

- Jede Sitzung beginnt mit `skill.md` und `WISSENSBASIS.md` des Repos.
- Ein Auftrag = ein Schritt der Tabellen oben; Ergebnis immer als Commit mit Prüfausgabe.
- Entscheidungen trifft C an den Gates A–D; Claude legt offene Entscheidungen gesammelt vor, statt sie stillschweigend zu setzen.
