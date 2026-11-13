# Bolyai Labs – MI és autonóm ágensek a szoftverfejlesztésben

A 13. évfolyamos tantárgy tanulói weboldala: a nyitóoldal és a 31 blokk oldala, a feliratos útmutató videókkal.

**Az oldal:** https://kizsi2025.github.io/bolyai-labs/

| | |
| --- | --- |
| `index.html` | a tantárgy nyitóoldala: modulok, blokkok, ranglétra, értékelés |
| `blokk/01/` … `blokk/31/` | a blokkok oldalai (`index.html` + `media/` a videóval) |

Statikus oldal, build nélkül: bármelyik webszerver kiszolgálja. Helyben:

```powershell
python -m http.server 8000
# majd a böngészőben: http://localhost:8000
```

A blokkok csomagjai és sablonjai külön repókban vannak (`Kizsi2025/bolyai-labs-NN-…`), a tanári anyagok
(óratervek, diasorok, értékelőlap) nem részei ennek a repónak.
