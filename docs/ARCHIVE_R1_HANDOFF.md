> **R2: CHANGES_REQUIRED.** Předchozí video není produktově schválené. Platí opravný mandát R2; nejprve referenční kapitola a lidské schválení, teprve potom další produkce.

# Playwright Academy – aktuální předání

Dokončeno 10. 11. 2026: technická dodávka je připravená k internímu ověření.
Včerejší přerušení již neplatí. Nový kompletní kurz není potřeba znovu vyrábět.

## Kde je výsledek

V `dist/Playwright_Academy/` jsou:

- `Playwright_Academy_Python_CZ_Full_Course.mp4` – **1:37:11.61**, 12 kapitol,
  97 skutečných scén, Microsoft Vlasta, 1920×1080 / H264 / 25 fps, AAC / 48 kHz.
- `Playwright_Academy_Starter_Kit.zip` – projekt, výuka, spouštěče a důkazy.
- `Playwright_Academy_Production_Sources.zip` – původní nahrávky, komentář,
  časování, receipty a archivované snímky pro další střih.
- České SRT/VTT, kapitoly, přepis, `DELIVERY.md` a `SHA256SUMS.txt`.

Oba ZIPy mají společný kořen `playwright-academy`; pro opravy se rozbalují
společně. Ke studiu stačí MP4 a Starter Kit. Podrobnosti: `docs/PRODUCT_REPORT.md`,
`docs/ACCEPTANCE.md`, `docs/REVIEW.md`, `video_course/README.md`.

Finální MP4 SHA-256:
`71bf3706f1c3eb8c173395872a10010ead26ccbdbf8f632a6ddd780dfe1e269f`.
Velikost **200 010 049 B**.

## Ověřené výsledky

- Starter Kit a řešení společně **44 passed in 40.23s**; opačné pořadí
  **44 passed in 40.24s**. Řešení 12 lekcí obsahují 14 testovacích případů.
- **78** zmrazených souborů zůstalo beze změny.
- **97/97** zdrojových záběrů ověřeno SHA, úplným decode a třemi archivovanými snímky.
- Finální film: úplný decode exit 0, prázdný chybový log, 12 platných kapitol.
- Synchronizace 97/97, maximální naměřená odchylka **21.312 ms**.
- Všech **969** vložených titulků má přesný původní text a shodné časování.
- Výběrová vizuální kontrola všech kapitol a 21 skutečných finálních snímků;
  opravené soukromé/překreslované záběry se do dodávky nedostaly.
- Archivy prošly CRC, manifesty, 78 zmrazenými zdroji a přenositelností. V nové cestě
  s mezerou znovu sestavily identické podklady pro střih.
- Nezávislou technickou revizi vedl druhý AI reviewer, nikoli člověk.

## Zachovat při dalších změnách

Jediný hlas: **Microsoft Vlasta / cs-CZ-VlastaNeural**. **QA = kjů ej**.
Komentář je souvislý po celých odstavcích; fonetické úpravy se týkají pouze řeči.
Titulky, přepis a kód zachovávají původní pravopis. Další vzorky hlasů nejsou potřeba.

Produkční lock používá `imageio-ffmpeg==0.6.0`, binární **FFmpeg 7.1**.
Novější muxer při kontrole vyráběl neplatné odkazy kapitol, proto se nepoužívá.
Recorder drží jen své okno dočasně vpředu a při cizím popředí nepřijme scénu;
headed terminálová cesta má zdokumentovanou výjimku. Během natáčení nepřepínat GUI.

Před úpravou výuky zkontrolovat `scripts/freeze_reference.py --check`.
Změna kteréhokoli zmrazeného zdroje vyžaduje odpovídající změny dokumentace,
scén a jejich důkazů. Pro běžné přehrání se nic nesyntetizuje ani nerenderuje.

## Co dosud nebylo lidsky ověřené

Čistý nově nainstalovaný Windows, úplný lidský poslech a skutečný začátečnický
uživatelský test nebyly k dispozici. AI revize, ASR a simulovaný walkthrough je
nenahrazují. Scénář případného lidského ověření: `docs/BEGINNER_WALKTHROUGH.md`.
Další omezení: `docs/KNOWN_LIMITATIONS.md`. Placení TTS služeb není schválené
ani potřebné. Edge TTS nemá touto integrací garantovanou kvótu nebo dostupnost;
hotové audio je přiložené a přehrávání žádné TTS připojení nepotřebuje.
