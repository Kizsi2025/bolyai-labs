# 29. blokk – Etikai és jogi audit

Ez a csomag a záró projekted repójába kerül, a 28. blokk bétája mellé. A 4. modul első blokkja: mielőtt a
projektedet bemutatod, végiggondolod, **szabad-e** úgy működnie, ahogy működik – és kinek mit kell tudnia róla.
Az 1. óra elmélet (MI-etika, AI Act, GDPR, szerzői jog, licencek, szolgáltatási feltételek), a 2. órán a saját
projekteden végzed el az auditot, és a végén zárókvíz.

> Ez nem jogi tanácsadás. Ahol a döntés az iskoláé (pl. a személyes adatok jogalapja), azt le kell írni kérdésként,
> és az iskola adatvédelmi tisztviselőjével kell egyeztetni.

| Fájl | |
| --- | --- |
| `src/app/megfeleles.py`, `megfeleles_futtat.py` | kész: licencek kiolvasása a telepített csomagokból, copyleft-ellenőrzés |
| `kiadas_futtat.py` | frissítve: a teljesítmény-sor ugyanazt a ráhagyást használja, mint a teszt |
| `docs/MEGFELELOSEG.md` | **a te részed** – most példa van benne |
| `LICENSE` | **a te részed** – a projekt licence |
| `tests/test_megfeleles_szerzodes.py` | kész – nem szabad módosítani |

## 1. A csomag bemásolása

```powershell
Expand-Archive ..\bolyai-labs-29-etika.zip ..\csomag29
Copy-Item ..\csomag29\bolyai-labs-29-etika\* . -Recurse -Force
python -m pytest -q                   # 7 piros
python megfeleles_futtat.py
```

## 2. Licenc és licenclista

- **A projekt licence:** a repó gyökerébe `LICENSE`. A GitHubon: *Add file → Create new file*, név: `LICENSE`, majd
  *Choose a license template*. Iskolai projekthez az MIT a legegyszerűbb: bárki használhatja, ha a nevetek benne marad.
- **A függőségeké:** `python megfeleles_futtat.py licencek` → `docs/LICENCEK.md` (a telepített csomagokból, ezért a
  rögzített verziókkal futtasd). Az ellenőrzés a közvetett függőségeket is megnézi: erős copyleft (GPL, AGPL) egy MIT
  projektben nem lehet; ismeretlen licencű csomagot nézz meg kézzel, és írd be a MEGFELELOSEG.md Licencek részébe.
- **A modellé is:** ha helyi modellt használsz (Ollama), nézd meg a licencét (`ollama show <modell> --license`). Például
  a `qwen2.5:3b` a Qwen Research License alatt van: csak kutatásra, kipróbálásra. A `qwen2.5:7b` és az `1.5b` Apache-2.0.

## 3. Átláthatóság: a felhasználó tudja, hogy MI-vel beszél

Az AI Act 50. cikk (1) bekezdése 2026. augusztus 2-től kötelező: aki közvetlenül beszélget egy MI-rendszerrel, annak
tudnia kell róla, hacsak nem nyilvánvaló. Webes felületnél egy jól látható mondat az `index.html`-be, API-nál a
`FastAPI(description=…)`-ba. Például:

```html
<p class="mi-jelzes">A válaszokat <strong>mesterséges intelligencia</strong> állítja össze, és tévedhet:
mindig nézd meg a forrást. Ne írj a kérdésbe nevet vagy más személyes adatot.</p>
```

Ez kódváltozás a kódfagyasztás alatt – megfelelőségi javításként rendben van: verzió `0.8.1-beta`, CHANGELOG,
`python doksi_futtat.py api`, `python kiadas_futtat.py`, címke `v0.8.1-beta`.

## 4. A megfelelőségi dokumentum

`docs/MEGFELELOSEG.md`, ezekkel a fejezetekkel (`## `):

| Fejezet | Kérdés |
| --- | --- |
| **Kockázati besorolás (AI Act)** | `**Besorolás:**` tiltott / nagy kockázatú / átláthatósági kötelezettség / minimális – és `**Indoklás:**`. Oktatásban nagy kockázatú, ami felvételről dönt, tanulmányi eredményt értékel, vagy dolgozatírás közben figyel. |
| **Átláthatóság** | Honnan tudja a felhasználó, hogy MI válaszol, és mire alapoz a válasz? |
| **Személyes adatok (GDPR)** | `**Milyen adat:**`, `**Jogalap:**`, `**Megőrzés:**`, `**Érintetti jogok:**` – és hová kerül az adat (a modell szolgáltatója?) |
| **Szerzői jog és források** | Kié a tudástár szövege, szabad-e használni? Mi a helyzet az MI-vel írt kóddal? |
| **Licencek** | A projekt licence, a függőségeké, a modellé. |
| **Szolgáltatási feltételek** | Mit enged a modell szolgáltatója – kinek, milyen korosztálynak, hol? |
| **MI-etika** | A megbízható MI hét követelménye a te projekteden: hol teljesül, hol nem. |
| **Teendők** | `- [ ]` / `- [x]` – mi van kész, mi marad nyitva. |

Fontos: amit nem tudsz, írd le kérdésként – az őszinte „nyitott kérdés” többet ér, mint a magabiztos tévedés.

## 5. Zárókvíz és napló

A 2. óra végén zárókvíz (Teams). Gyakorolni a blokk oldalán lehet.

A `HALADAS.md` végére:

```markdown
## 29. blokk – Etikai és jogi audit

**Audit:** mit talált, mi a legfontosabb teendő.
**Állapot:** zöld / sárga / piros
```

```powershell
python megfeleles_futtat.py
python doksi_futtat.py
python -m pytest -q
git add .
git commit -m "docs: etikai és jogi audit (feladatkártya #29)"
git push
```

## Ha elakadsz

- **„nincs felismerhető LICENSE”** – a fájl neve `LICENSE` (kiterjesztés nélkül), és a licencszöveg teljes.
- **„A docs/LICENCEK.md … elavult”** – `python megfeleles_futtat.py licencek`; ha a CI-ben más jön ki, a helyi
  venv-edben nem a rögzített verziók vannak: `python -m pip install -r requirements.txt`.
- **„A felületen nem derül ki, hogy MI válaszol”** – a mondat a látható szövegben legyen, ne megjegyzésben.
- **„erős copyleft”** – a csomag GPL/AGPL; keress helyette megengedő licencűt, vagy beszéld meg a tanárral.
- **A doksi-ellenőrző a MEGFELELOSEG.md-ben talál hibát** – maradt benne `PÉLDA`, `TODO` vagy `___`.
