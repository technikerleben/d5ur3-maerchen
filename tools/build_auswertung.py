#!/usr/bin/env python3
"""Auswertungs-App der Lernerfolgskontrolle (apps/auswertung-lek/index.html).

Vorlage: tools/vorlagen/auswertung_lek.html (aus der Zootiere-Auswertung übernommen).
Stufenbeschreibungen, Punkte und Notengrenzen kommen aus inhalt/pruefung.json –
dieselbe Quelle wie Bewertungsseite und Erwartungshorizont.

    python3 tools/build_auswertung.py      (erzeugt und prüft im Browser)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bewertung import notenschluessel  # noqa: E402
from satz import ROOT  # noqa: E402

P = json.loads((ROOT / "inhalt" / "pruefung.json").read_text("utf-8"))
OUT = ROOT / "apps" / "auswertung-lek" / "index.html"

KURZ = {"K1": "Textmuster Märchen", "K2": "Figuren und Rollen", "K3": "Handlung", "K4": "Märchensprache", "K5": "Prüfen und verbessern"}
DESC = {
    "K1": "Die Fortsetzung ist klar ein Märchen: passende Märchenmerkmale gehören zur Handlung.",
    "K2": "Die Figuren handeln passend zu ihren Rollen; Figuren aus dem Anfang werden genutzt.",
    "K3": "Anknüpfung an den Anfang, Weg und Prüfung, Lösung des Problems, passendes Ende.",
    "K4": "Präteritum, wörtliche Rede mit Zeichen, Märchenwörter und Formeln, anschaulich.",
    "K5": "Prüfbeleg (Satzanfänge, Verben, Redezeichen), Checkliste, sichtbare Verbesserungen.",
}
FEEDBACK = {
    "K1": ["Märchenmerkmale sind in deiner Fortsetzung noch nicht zu erkennen.",
           "Erste märchenhafte Dinge sind da. Dein Text wirkt aber noch eher wie eine Alltagsgeschichte.",
           "In deiner Fortsetzung kommen Märchenmerkmale vor.",
           "Deine Märchenmerkmale gehören zur Handlung – man merkt sofort: Das ist ein Märchen.",
           "Du setzt Märchenmerkmale gezielt ein und führst die Merkmale des Anfangs weiter."],
    "K2": ["Die Figuren aus dem Anfang kommen in deiner Fortsetzung noch nicht vor.",
           "Deine Figuren handeln noch nicht immer so, wie es zu ihrer Rolle passt.",
           "Deine Hauptfigur bleibt ihrer Rolle treu.",
           "Held, Helfer und Gegenspieler handeln passend zu ihren Rollen.",
           "Deine Figuren handeln stimmig; man erkennt ihre Eigenschaften an dem, was sie tun und sagen."],
    "K3": ["Deine Fortsetzung knüpft noch nicht an den Anfang an.",
           "Du knüpfst an den Anfang an, aber das Problem wird noch nicht gelöst oder das Ende fehlt.",
           "Du knüpfst an den Anfang an und löst das Problem.",
           "Deine Handlung ist schlüssig: Weg, Prüfung, Lösung und ein passendes Ende.",
           "Deine Handlung ist spannend aufgebaut und nutzt die Hinweise aus dem Anfang."],
    "K4": ["Achte noch auf die Zeitform: Ein Märchen erzählt im Präteritum.",
           "Du wechselst noch oft zwischen Präsens und Präteritum.",
           "Du erzählst überwiegend im Präteritum.",
           "Du erzählst im Präteritum, setzt die Zeichen der wörtlichen Rede und nutzt Märchenwörter.",
           "Du erzählst sicher, anschaulich und in Märchensprache."],
    "K5": ["Eine Prüfung deines Textes ist noch nicht sichtbar.",
           "Du hast mit dem Prüfen angefangen. Zeige alle drei Prüfschritte.",
           "Du zeigst deine Prüfung und hast eine Stelle verbessert.",
           "Du prüfst vollständig und verbesserst mehrere Stellen sichtbar.",
           "Deine Verbesserungen machen deinen Text deutlich besser."],
}
NEXT = {
    "K1": "Nimm Merkblatt 1: Baue in deine nächste Fortsetzung zwei Märchenmerkmale ein, die zur Handlung gehören – zum Beispiel einen Zauber und die Zahl 3.",
    "K2": "Nimm Merkblatt 2: Überlege vor dem Schreiben, wer Held, Helfer und Gegenspieler ist. Lass jede Figur so handeln, wie es zu ihrer Rolle passt.",
    "K3": "Nimm den Bauplan aus Merkblatt 5: Plane in Stichworten Weg, Prüfung, Lösung und Ende. Prüfe: Wird das Problem aus dem Anfang gelöst?",
    "K4": "Nimm die Präteritum-Liste aus Merkblatt 4: Unterstreiche nach dem Schreiben alle Verben und prüfe sie. Setze bei wörtlicher Rede „ “.",
    "K5": "Mach den Prüfbeleg in drei Runden: Satzanfänge einkreisen, Verben unterstreichen, Redezeichen markieren. Verbessere danach zwei Stellen.",
}
SKILLS = {"K1": "ein Märchen mit Märchenmerkmalen erzählen", "K2": "Figuren passend zu ihren Rollen handeln lassen",
          "K3": "eine Handlung vom Problem bis zum Ende aufbauen", "K4": "im Präteritum und in Märchensprache erzählen",
          "K5": "deinen Text prüfen und verbessern"}
STRENGTHS = {"K1": "Man erkennt sofort, dass dein Text ein Märchen ist", "K2": "Deine Figuren handeln passend",
             "K3": "Deine Handlung passt zum Anfang und hat ein gutes Ende", "K4": "Du erzählst wie in einem Märchen",
             "K5": "Du prüfst deinen Text sichtbar"}
EXPECT = {
    "v1": {"K1": "z. B. dankbare Tiere als Zauberhelfer, die Zahl 3 (drei Aufgaben, drei Tiere), Erlösung, Belohnung, Schlussformel.",
           "K2": "Dummling bleibt gütig und tierlieb; Ameisen, Enten, Bienen als Helfer naheliegend; Brüder als Gegenbild (zu Stein); graues Männchen.",
           "K3": "Anknüpfung an die Perlen-Aufgabe (Dummling weint auf dem Stein); weitere Aufgaben möglich; Schloss erlöst, Dummling belohnt."},
    "v2": {"K1": "z. B. sprechende Kröte, Zauber (Teppich aus der Schachtel), Zahl 3 (drei Federn, ggf. drei Aufgaben), Belohnung, Schlussformel.",
           "K2": "Dummling bescheiden und freundlich; Kröte als Helferin; spöttische Brüder machen es sich leicht; König entscheidet.",
           "K3": "Anknüpfung an die Frage der Kröte nach seinem Begehren; der feinste Teppich wird beschafft; Dummling wird König."},
}
K5_EXPECT = "Sichtbarer Prüfbeleg laut Auftrag 3: Satzanfänge eingekreist, Verben unterstrichen, Redezeichen markiert; Checkliste angekreuzt; mindestens zwei Verbesserungen (Regelstandard)."


def tendenz(maximum: int) -> list[tuple[int, str]]:
    """Notentendenz innerhalb eines Notenbereichs: oberstes Drittel +, unterstes −; ungenügend ohne Tendenz."""
    aus = []
    for i, (_, lo, hi) in enumerate(notenschluessel(maximum)):
        n = i + 1
        if n == 6:
            aus.append((0, "6"))
            continue
        breite = hi - lo + 1
        drittel = max(1, breite // 3) if breite >= 3 else 0
        if drittel:
            aus += [(hi - drittel + 1, f"{n}+"), (lo + drittel, f"{n}"), (lo, f"{n}−")]
        else:
            aus.append((lo, f"{n}"))
    return aus


def daten() -> str:
    krit = [{"id": k["k"], "title": f'{k["k"]} · {k["titel"]}', "short": KURZ[k["k"]], "desc": DESC[k["k"]],
             "levels": ["Nicht erkennbar."] + k["stufen"]} for k in P["kriterien"]]
    maximum = sum(k["punkte"] for k in P["kriterien"])
    titel = {t["id"]: t["titel"] for t in json.loads((ROOT / "inhalt" / "texte.json").read_text("utf-8"))["texte"]}
    var = {}
    for v, d in P["lek"].items():
        key = v.lower()
        name = titel[d["maerchen"]]
        var[key] = {"name": name, "animal": name, "short": f"{v} {name.replace('Die ', '')}", "expect": EXPECT[key]}
    pct = {i + 1: g for i, (_, g) in enumerate(P["notengrenzen"][:-1])}
    tend = tendenz(maximum)
    js = [
        "const VARIANTS=%s;" % json.dumps(var, ensure_ascii=False),
        'const TERMINE={frueh:"früher Termin",spaet:"später Termin"};',
        "const CRITERIA=%s;" % json.dumps(krit, ensure_ascii=False),
        "const K5_EXPECT=%s;" % json.dumps(K5_EXPECT, ensure_ascii=False),
        "const FEEDBACK=%s;" % json.dumps(FEEDBACK, ensure_ascii=False),
        "const NEXT_STEPS=%s;" % json.dumps(NEXT, ensure_ascii=False),
        "const SKILLS=%s;" % json.dumps(SKILLS, ensure_ascii=False),
        "const STRENGTHS=%s;" % json.dumps(STRENGTHS, ensure_ascii=False),
        "function criterionFor(c,s){return c}",
        "function feedbackFor(c,s,lv){return FEEDBACK[c.id][lv]}",
        "function nextStepFor(c,s){return NEXT_STEPS[c.id]}",
        "function skillFor(id,s){return SKILLS[id]}",
        "function strengthFor(id,s){return STRENGTHS[id]}",
        "const MAX_POINTS=%d;" % maximum,
        "const GRADE_PERCENTAGES=%s;" % json.dumps(pct),
        "const T=Object.fromEntries(Object.entries(GRADE_PERCENTAGES).map(([g,p])=>[g,Math.ceil(MAX_POINTS*p/100-1e-9)]));",
        'const GRADE_NAMES={1:"sehr gut (1)",2:"gut (2)",3:"befriedigend (3)",4:"ausreichend (4)",5:"mangelhaft (5)",6:"ungenügend (6)"};',
        "const GRADE_ROWS=[1,2,3,4,5,6].map(n=>{const lo=n===6?0:T[n],hi=n===1?MAX_POINTS:T[n-1]-1;"
        'return {n,pct:n===6?"unter "+GRADE_PERCENTAGES[5]+" %":"ab "+GRADE_PERCENTAGES[n]+" %",range:lo+"–"+hi+" Punkte"}});',
        "function gradeFor(p){p=Number(p)||0;for(const g of [1,2,3,4,5])if(p>=T[g])return g;return 6}",
        "const TENDENZ=%s;" % json.dumps(tend, ensure_ascii=False),
        "function gradeDisplayFor(p){p=Number(p)||0;for(const [ab,n] of TENDENZ)if(p>=ab)return n;return \"6\"}",
    ]
    return "\n".join(js)


def check(path: Path) -> list[str]:
    from playwright.sync_api import sync_playwright
    fails = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": 1280, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(path.resolve().as_uri())
        pg.click("#newStudent")
        pg.fill("#studentName", "Test")
        pg.click("[data-variant='v1']")
        if pg.locator(".criterion").count() != 5:
            fails.append("nicht genau fünf Kompetenzen")
        # Notenschlüssel prüfen: Punkte → Note
        soll = {20: "1", 18: "1", 17: "2", 15: "2", 14: "3", 12: "3", 11: "4", 9: "4", 8: "5", 4: "5", 3: "6", 0: "6"}
        for punkte, note in soll.items():
            g = pg.evaluate(f"gradeFor({punkte})")
            if str(g) != note:
                fails.append(f"{punkte} Punkte → Note {g}, erwartet {note}")
        for cid in ["K1", "K2", "K3", "K4", "K5"]:
            pg.click(f"[data-cid='{cid}'][data-level='3']")
        if pg.inner_text("#corePoints") != "15 / 20":
            fails.append("Summe falsch: " + pg.inner_text("#corePoints"))
        if not pg.inner_text("#gradeSuggestion").startswith("2"):
            fails.append("Note bei 15 Punkten: " + pg.inner_text("#gradeSuggestion"))
        if errs:
            fails.append("JS-Fehler: " + "; ".join(errs[:3]))
        pg.evaluate("localStorage.clear()")
        br.close()
    return fails


def main() -> int:
    vorlage = (ROOT / "tools" / "vorlagen" / "auswertung_lek.html").read_text("utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(vorlage.replace("/*__DATEN__*/", daten()), encoding="utf-8")
    fails = check(OUT)
    print("Auswertung: " + ("ok" if not fails else "FEHLER:\n  " + "\n  ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
