"""A záró projekt etikai és jogi szerződése (29. blokk). Nem a projekted témáját nézi, hanem azt, hogy elkészült-e az
audit: van-e licenc és naprakész licenclista, nincs-e összeférhetetlen licencű függőség, a felhasználó megtudja-e,
hogy MI-vel beszél (AI Act 50. cikk), és a megfelelőségi dokumentum minden kérdésre válaszol-e.
Hogy a válaszok helyesek-e, azt a tanár nézi meg – a teszt csak azt, hogy megvannak.
NE módosítsd – ha valami nem illik a projektedhez, beszéld meg a tanárral."""
import re
from pathlib import Path

import yaml

from app import api, megfeleles

ROOT = Path(__file__).resolve().parent.parent
FEJEZETEK = ["Kockázati besorolás", "Átláthatóság", "Személyes adatok", "Szerzői jog", "Licencek",
             "Szolgáltatási feltételek", "MI-etika", "Teendők"]
BESOROLASOK = ("tiltott", "nagy kockázatú", "átláthatósági kötelezettség", "minimális")
MI_SZOVEG = re.compile(r"mesterséges intelligencia|\bMI\b|\bAI\b")


def dokumentum() -> str:
    f = ROOT / "docs" / "MEGFELELOSEG.md"
    assert f.exists(), "Hiányzik: docs/MEGFELELOSEG.md"
    return f.read_text(encoding="utf-8")


def fejezet(t: str, cim: str) -> str:
    m = re.search(rf"^## [^\n]*{re.escape(cim)}[^\n]*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    return m[1] if m else ""


def test_licenc_fajl():
    assert megfeleles.projekt_licenc(ROOT), \
        "Tegyél LICENSE fájlt a repó gyökerébe (pl. MIT – a GitHubon: Add file → Create new file → LICENSE → Choose a license template)."


def test_licenclista_naprakesz():
    f = ROOT / "docs" / "LICENCEK.md"
    assert f.exists() and f.read_text(encoding="utf-8") == megfeleles.licenc_tabla(ROOT), \
        "A docs/LICENCEK.md hiányzik vagy elavult – python megfeleles_futtat.py licencek"


def test_nincs_osszeferhetetlen_vagy_ismeretlen_licenc():
    hibak = megfeleles.licenc_hibak(ROOT)
    assert not hibak, "python megfeleles_futtat.py ellenoriz\n" + "\n".join(hibak)


def test_a_felhasznalo_tudja_hogy_mi_valaszol():
    integracio = ROOT / "integracio.yaml"
    valasztas = (yaml.safe_load(integracio.read_text(encoding="utf-8")) or {}).get("valasztas") if integracio.exists() else None
    if valasztas == "web":
        html = (ROOT / "src" / "app" / "web" / "index.html").read_text(encoding="utf-8")
        latszo = re.sub(r"<!--.*?-->|<script.*?</script>", "", html, flags=re.S)
        assert MI_SZOVEG.search(latszo), \
            "A felületen nem derül ki, hogy MI válaszol – egy jól látható mondat az index.html-be (AI Act 50. cikk (1))."
    else:
        leiras = api.app.openapi().get("info", {}).get("description", "")
        assert MI_SZOVEG.search(leiras), "Az API leírásában (FastAPI(description=…)) írd le, hogy a válaszokat MI állítja elő."


def test_megfelelosegi_dokumentum():
    t = dokumentum()
    assert not re.search(r"\bP[EÉ]LDA\b|\bTODO\b|_{3,}", t), "A docs/MEGFELELOSEG.md még a példa vagy kitöltetlen (PÉLDA, TODO, ___)."
    hianyzik = [c for c in FEJEZETEK if not fejezet(t, c).strip()]
    assert not hianyzik, f"Hiányzó vagy üres fejezetek (## …): {hianyzik}"
    b = re.search(r"\*\*Besorolás:\*\*\s*(.+)", fejezet(t, "Kockázati besorolás"))
    assert b and any(x in b[1].lower() for x in BESOROLASOK), f"**Besorolás:** az egyik: {', '.join(BESOROLASOK)}"
    assert re.search(r"\*\*Indoklás:\*\*\s*\S", fejezet(t, "Kockázati besorolás")), "**Indoklás:** miért ebbe a kategóriába tartozik."
    gdpr = fejezet(t, "Személyes adatok")
    for mezo in ("Milyen adat", "Jogalap", "Megőrzés", "Érintetti jogok"):
        assert re.search(rf"\*\*{mezo}:\*\*\s*\S", gdpr), f"Személyes adatok: **{mezo}:**"
    assert re.search(r"^- \[[ x]\] \S", fejezet(t, "Teendők"), re.M), "Teendők: legalább egy pont (- [ ] … vagy - [x] …)."


def test_haladasi_naplo_29():
    md = (ROOT / "HALADAS.md").read_text(encoding="utf-8")
    resz = md.split("## 29. blokk", 1)[1].split("\n## ", 1)[0] if "## 29. blokk" in md else ""
    assert resz and "TODO" not in resz, "Töltsd ki a HALADAS.md 29. blokkos részét (minta: ETIKA_JOG.md vége)."
    assert re.search(r"\*\*Audit:\*\*\s*\S", resz), "**Audit:** mit talált az audit, mi a legfontosabb teendő."
    assert re.search(r"\*\*Állapot:\*\*\s*(zöld|sárga|piros)\b", resz), "Az állapot: zöld, sárga vagy piros."
