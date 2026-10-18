# Bildstil und Bildliste · Deutsch 5 · Märchen

Stand: 18.10.2026 · Vorlage für KI-Bilder, die C erstellt. Ziel: kleine Illustrationen, die die Arbeitsmaterialien gliedern und das Verstehen stützen, im Druck (Graustufen, auf A5 verkleinert) genauso funktionieren wie im farbigen Input und neben gemeinfreien Grimm-Illustrationen (z. B. Otto Ubbelohde) nicht fremd wirken.

## a) Bildstil

**Kurzform:** Schwarze Federzeichnung im Stil alter Märchenbuch-Illustrationen, klar und freundlich, auf weißem Grund – mit optionaler zarter Aquarell-Lasur für die Farbfassung.

| Merkmal | Festlegung |
|---|---|
| Technik | Tusche-/Federzeichnung mit gleichmäßigen, eher kräftigen Konturen; Schatten nur durch wenige, lockere Schraffuren; keine großen schwarzen oder grauen Flächen |
| Anmutung | erinnert an Märchenbücher um 1900 (Holzstich, Federzeichnung), aber vereinfacht und kindgerecht; ruhig, warm, leicht humorvoll; nie gruselig |
| Figuren | einfache, gut lesbare Körperhaltungen; freundliche Gesichter mit wenigen Strichen; Kleidung im Stil „alte Zeit“ (Kittel, Schürze, Kopftuch, Umhang); keine Figur aus Filmen oder bekannten Bilderbüchern nachahmen |
| Bildaufbau | ein Motiv, zentral, viel Weißraum; Hintergrund nur angedeutet (eine Baumgruppe, eine Mauer) |
| Hintergrund | rein weiß oder transparent, ohne Rahmen, ohne Vignette, ohne Papierstruktur |
| Text im Bild | **keiner** – keine Buchstaben, Zahlen oder Schilder (auch nicht auf Büchern oder Pergament) |
| Lesbarkeit | muss bei **4–6 cm Breite** in Graustufen eindeutig erkennbar sein (A4 gesetzt, auf A5 verkleinert gedruckt) |
| Farbfassung (Input, digitales Märchenbuch) | dieselbe Strichzeichnung mit zarter, transparenter Aquarell-Lasur in gedämpften Tönen, passend zum HBG-SRL-Schema: Schieferblau, Rostorange, Salbeigrün, warmes Beige; Konturen bleiben schwarz |
| Druckfassung | dieselbe Zeichnung **ohne** Farbe (reine Strichzeichnung) – nicht nachträglich in Graustufen umrechnen, damit keine grauen Flächen entstehen |
| Format | quadratisch (1:1) oder 4:3 quer; mindestens 1500 px an der langen Seite; PNG |
| Dateinamen | `assets/bilder/<motiv>_strich.png` und `<motiv>_farbe.png`; Nachweis „KI-generiert (Werkzeug), C. Wegemann“ in `assets/bilder/quellen.json` |

**Prompt-Baustein (Stil, an jedes Motiv anhängen):**

> *black ink line drawing in the style of a 19th-century fairy tale book illustration, simplified and child-friendly, clean confident outlines, light cross-hatching only, no solid black areas, no grey fill, plain white background, no frame, no text, no letters, single centered motif, generous white space, warm and gentle mood*

Für die Farbfassung ergänzen:

> *with a soft transparent watercolor wash in muted slate blue, rust orange, sage green and warm beige, black outlines kept*

**Negativ-Hinweis (falls das Werkzeug ihn unterstützt):** *text, letters, numbers, signature, frame, photorealistic, 3D, cartoon style of famous studios, dark scary atmosphere, heavy shadows*

**Konsistenz:** Erst Motiv 2 erzeugen und als Stilreferenz für alle weiteren Bilder verwenden. Wenn die Märchenkarten schon einen eigenen Bildstil haben, ist dieser vorrangig – dann den Stil der Karten beschreiben und den Prompt-Baustein daran anpassen.

## b) Bildliste (10 Motive)

| Nr. | Motiv (Dateiname) | Beschreibung | Einsatz |
|---|---|---|---|
| 1 | **Märchenbuch** (`maerchenbuch`) | Ein großes, aufgeschlagenes altes Buch. Aus den Seiten wachsen wie ein Pop-up ein kleines Schloss mit Turm, ein paar Tannen und ein schmaler Weg. | Titel von Input und Merkblatt aller Etappen, Deckblatt des Schülerpakets |
| 2 | **Frau Holle schüttelt das Bett** (`frau_holle_bett`) | Eine freundliche alte Frau mit Haube lehnt aus einem Fenster und schüttelt ein dickes Federbett aus. Federn fliegen heraus und werden unten zu Schneeflocken. | Beispielmärchen; Material zu Blatt 1; Stilreferenz |
| 3 | **Spindel im Brunnen** (`brunnen_spindel`) | Ein Mädchen in Schürze kniet erschrocken an einem runden Steinbrunnen; eine Spindel mit Faden fällt gerade ins Wasser. | Anfang von „Frau Holle“; Merkblatt „Merkmale in Frau Holle“ |
| 4 | **Brot und Apfelbaum** (`brot_apfelbaum`) | Auf einer Blumenwiese ein gemauerter Backofen mit Broten und daneben ein Apfelbaum voller Äpfel; Brote und Baum haben angedeutete, freundliche Gesichter (sie können sprechen). | Merkmal „die Magie“ und „die Prüfung“ |
| 5 | **Gold und Pech** (`gold_pech`) | Zwei gleich große Torbögen nebeneinander: Unter dem linken fallen glänzende Goldstücke wie Regen, unter dem rechten tropft ein dicker, zäher Strom. Keine Figuren. | Merkmale „die Belohnung“ und „die Bestrafung“; Gut und Böse |
| 6 | **Lupe über dem Buch** (`lupe`) | Eine große Lupe liegt schräg auf einer aufgeschlagenen Buchseite; unter dem Glas sieht man vergrößert einen kleinen Stern und einen Schlüssel. | Signet für alle **Blätter A** (Märchen untersuchen) in allen Etappen |
| 7 | **Weiterschreiben** (`weiterschreiben`) | Eine Schreibfeder zieht eine Linie aus einem Tintenfass; die Linie wird zu einer Ranke, an der kleine Symbole hängen: Krone, Schlüssel, Stern. | Signet für alle **Blätter B** (Weiterschreiben) und die Etappe-5-Blätter |
| 8 | **Das stille Mühlrad** (`muehlrad`) | Ein großes hölzernes Mühlrad steht still über einem ausgetrockneten Bachbett; ein Mädchen mit Tuch über den Schultern schaut nachdenklich darauf. | Märchenanfang „Die Müllerstochter“ (Blatt 2) |
| 9 | **Das Mädchen und der Vogel** (`vogel`) | Vor einer kleinen Holzhütte am Waldrand hält ein Mädchen behutsam einen kleinen Vogel in beiden Händen. | Beispiel „Einen Märchenanfang weiterschreiben“ im Input und Merkblatt 1 |
| 10 | **Otter und König** (`otter_koenig`) | Zwei kleine Bilder nebeneinander, durch einen dünnen Strich getrennt: links ein Fischotter am Flussufer (sachlich gezeichnet), rechts ein König mit Krone vor einem Schloss (märchenhaft). | Abschnitt 1 „So erzählt ein Märchen“ (Präsens ↔ Präteritum); Brücke zur Reihe Zootiere |

## Stand der Bilder (18.10.2026)

Alle zehn Motive liegen als Strichzeichnung vor (KI-generiert, bereitgestellt von C) und sind eingebaut. Aufbereitung: Graustufen, Rand beschnitten, höchstens 1000 px, 16 Graustufen (`assets/bilder/<motiv>_strich.png`, Nachweise in `assets/bilder/quellen.json`). Farbfassungen gibt es noch nicht; der Input zeigt die Strichzeichnungen auf weißen Karten.

| Motiv | eingebaut in (Etappe 1) |
|---|---|
| maerchenbuch | Titelfolie Input, Kopf Merkblatt |
| otter_koenig | Abschnitt 1 „So erzählt ein Märchen“ (Input, Merkblatt) |
| gold_pech | Abschnitt 2 „Das ist ein Märchen“ |
| brot_apfelbaum | Abschnitt 3 „Merkmale in Frau Holle“ |
| vogel | Abschnitt 6 „Einen Märchenanfang weiterschreiben“ |
| frau_holle_bett | Kopf des Märchentextes „Frau Holle“ (auch einfache Fassung) |
| muehlrad | Kopf des Märchenanfangs „Die Müllerstochter“ (Blatt 2) |
| lupe | Signet Blatt 1, GN1 A/B, Blatt 1F |
| weiterschreiben | Signet Blatt 2, Blatt 2F |
| brunnen_spindel | Merkkarte 1F |

Hinweis: „gold_pech“ hat eine große schwarze Fläche (Pech). Für den Kopierer unkritisch, aber tonerintensiv; bei Bedarf eine Fassung mit schraffiertem statt flächigem Pech erzeugen. Die Lupe zeigt Textzeilen statt Stern und Schlüssel – passt gut als neutrales Signet.

## Weitere Motive für Etappe 3–5 (Vorschlag, 18.10.2026)

| Nr. | Motiv (Dateiname) | Beschreibung | Einsatz |
|---|---|---|---|
| 11 | **Stroh wird zu Gold** (`spinnrad_gold`) | Ein altes Spinnrad in einer kleinen Kammer; links ein Haufen Stroh, rechts glänzende Spulen voller Goldfaden. Keine Figuren. | Etappe 3: Rumpelstilzchen-Material, Abschnitt „Die Dreimal-Regel“ |
| 12 | **Das Männchen am Feuer** (`maennchen_feuer`) | Ein kleines, bärtiges Männchen hüpft auf einem Bein um ein Lagerfeuer vor einem Häuschen am Waldrand; lustig, nicht unheimlich. | Etappe 3: Kopf von „Rumpelstilzchen“, Abschnitt „Problem und Lösung“ |
| 13 | **Der Weg mit Stationen** (`bauplan_weg`) | Ein geschwungener Weg von einer Hütte (links unten) bis zu einem Schloss (rechts oben); unterwegs drei Stationen: ein Fluss, ein dunkler Wald, ein Berg. | Etappe 3: Abschnitt „Der Märchenbauplan“, Signet für Planungsaufgaben |
| 14 | **Der leuchtende Apfel** (`apfel_schnee`) | Ein Kind im Wintermantel kniet im Schnee unter einem kahlen Baum und hält einen strahlenden Apfel; Lichtstrahlen als feine Linien. | Etappe 4: Märchenanfang Blatt 8, Abschnitt „Zauberszene“ |
| 15 | **Das Zauberbuch der Wörter** (`zauberwoerter`) | Ein aufgeschlagenes Buch, aus dem kleine Sterne, ein Schlüssel und eine Krone aufsteigen (ohne Buchstaben). | Etappe 4: Abschnitt „Märchenwörter und Formeln“ |
| 16 | **Prüfen mit Häkchen** (`pruefen`) | Ein Blatt Papier mit Linien, daneben ein Bleistift und eine Lupe; am Rand drei Häkchen. | Etappe 5: Signet für Blatt 11 „Prüfen und verbessern“ und die Checkliste |

## Regeln für den Einsatz

- Höchstens ein Bild pro Blatt; Bilder schmücken die Kopfzeile oder stehen neben dem Material, nie zwischen Aufgaben und Linien.
- Bilder dürfen **keine Lösungen verraten** (z. B. kein Bild, das auf einem Blatt die gesuchten Merkmale beschriftet).
- In Gelingensnachweisen, Probearbeit und LEK nur die Signets 6 und 7, keine Motivbilder zu den Prüfungstexten.
- F-Material darf die Motive 2–5 zusätzlich als Verstehenshilfe nutzen (z. B. „Kreuze an“ mit Bild).
- Alle Bilder in `assets/bilder/quellen.json` mit Werkzeug und Datum nachweisen; KI-Bilder sind im Bildnachweis als KI-generiert gekennzeichnet (Festlegung Gate A).
