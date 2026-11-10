# Playwright Academy – realizační backlog

Referenční zadání: Master Product Contract 1.0; jazyk čeština, Windows 11,
Python 3.12, synchronní Playwright a pytest. Jedna aplikace a jeden příběh:
přihlášení → nový požadavek → úprava → smazání → regrese → diagnostika.

| Etapa | Konkrétní výstup | Akceptační důkaz |
|---|---|---|
| M0 | Ověřené oficiální zdroje, architektura, závislosti, průzkum hlasu a nahrávání | docs/ARCHITECTURE.md, přesný lock |
| M1 | Lokální portál, 12 scénářů, izolace dat, Windows spouštěče | Skutečné Chromium běhy, HTML, JUnit, screenshot, trace |
| M2 | 12 českých lekcí s úkoly a řešeními, 45 položek reference | Spuštění řešení, kontrola odkazů a příkazů |
| M3 | Referenční manifest, souvislý komentář, shot list, produkční nástroje | Vazba scén na soubory, ověření nástrojů a hlasu |
| M4 | Skutečné záznamy, český hlas, synchronní titulky, MP4 1920×1080 | ffprobe, vizuální a poslechová kontrola každé kapitoly |
| M5 | Regrese, nezávislá revize, simulovaný začátečnický walkthrough, distribuce | docs/ACCEPTANCE.md, docs/REVIEW.md, evidence/ |

Stavy se zapisují podle skutečných důkazů. Scénář není hotové video; existence
MP4 sama neprokazuje kvalitu. Čistou instalaci Windows ani uživatelský test
nesmíme označit za ověřené pouhým během v této existující stanici.

## Rizika a opatření

- Hlas: vlastník vybral online Microsoft Vlastu; výslovnost QA je „kjů ej“.
  Fonetické úpravy se týkají jen řeči. Služba nemá touto integrací garantovanou
  kvótu ani dostupnost; hotový komentář je přiložený pro další střih.
- Synchronizace: nejprve stabilizovat kód, zmrazit SHA-256 manifest, potom
  natáčet scény s událostmi a skutečnými výsledky. Změna zdroje zneplatní záběr.
- Izolace: každý browser context má vlastní serverovou session a kopii seed dat.
  Žádný globální reset, který by ovlivnil souběžného uživatele.
- Demo je pouze lokální výuková služba, nikoliv nasaditelná firemní aplikace.
- Firemní aplikace: samostatná výslovná konfigurace; lokální demo testy se
  nesmějí automaticky obrátit na jinou adresu a měnit tam data.
- Nezávislá revize musí prověřit skutečný výsledek, nikoliv pouze převzít tvrzení autora.
