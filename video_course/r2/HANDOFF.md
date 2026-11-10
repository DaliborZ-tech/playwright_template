# Pokračování Playwright Academy — opravný mandát R2

Platné PO rozhodnutí: **CHANGES_REQUIRED** pro původní 97minutový kurz.
Aktuální oprava vyrábí **jen jednu referenční kapitolu 5–8 minut**.
Celý kurz znovu nevyrábět před úplným zhlédnutím, poslechem a výslovným
schválením reference vlastníkem. Hlas **cs-CZ-VlastaNeural**; žádný Jakub.
QA se vyslovuje „kjů ej“. Titulky zachovávají běžný pravopis odborných termínů.

## Aktuální práce

- Mandát: `video_course/r2/MANDATE_R2.md`.
- Režijní plán: `video_course/r2/plan.json`, měřená timeline `timeline.json`.
- Hotová reference: **5:48.48**, sedm souvislých odstavců Vlasty,
  27 skutečně natočených a časově navázaných záběrů.
- Zkouška skutečného průchodu prošla: prázdný soubor → psaní → živý DOM →
  tentýž test RED → změna jediné očekávané hodnoty → GREEN → čerstvý report.
- Výsledný zdroj se shoduje se zmrazeným Starter Kitem.
- Natáčení, render obou MP4 a úplné dekódování dokončeno. Globální SRT/VTT
  jsou UTF-8 s kanonickým textem; originální PCM zůstalo souvislé.
- Skutečné přehrávání českých titulků ON/OFF i vypálené varianty ověřeno
  na začátku, ve středu a na konci v Microsoft Edge **157.0.4341.42**.
- Z úplného ZIPu do nové cesty s mezerami: oba nové rendery jsou byte-identické,
  globální SRT/VTT také, všech **44 testů prošlo**, failures/errors/skipped 0.
  Bylo použito stejné připnuté mediální prostředí a Windows fonty, nikoli
  čistá nová instalace Windows. `reproduction_validation.json` uvádí rozsah.
- Doklady: `output/edit_project.json`, `quality_audit.json`,
  `evidence/player/player_validation.json`, `reproduction_validation.json`
  a `distribution_validation.json` s CRC i SHA kontrolou celého ZIPu.
- Nezávislý AI review: `video_course/r2/REVIEW_R2.md`; ověřeny zdroje, důkazy,
  všech 81 raw vzorků a všechny finální záběry na kontaktech, kritické části
  nativně. Ořez reportu i důkaz vypálených titulků byly opraveny a přezkoušeny.
  Delší výkladové pauzy nad funkcí (21 s) a DOM (25,5 s) jsou výslovně
  zdůvodněné a ponechané k obsahovému posouzení vlastníkem, nikoli vydávané
  za aktivní pohyb. Rozsah revize je výslovně uveden.
  Automatická kontrola není lidský poslech nebo produktové schválení.

## Výstupy a brána schválení

Hotový samostatný balík je `dist/Playwright_Academy_R2_Reference/`, jeden celý
archiv `dist/Playwright_Academy_R2_Complete.zip`. Obsahuje kompletní referenční
MP4, druhé MP4 s vypálenými titulky, globální SRT/VTT, kapitoly, přepis,
lokální přehrávač i samostatné produkční sources. Přehrání: `PREHRAT.cmd`.

Platný stav je `READY_FOR_HUMAN_REVIEW`, `po_approval=PENDING`,
`full_course_build_authorized=false`. Vlastník musí posoudit celý konkrétní
film (SHA-256), včetně hlasu a titulků. Při připomínkách opravit referenci;
teprve po schválení rozšířit postup na další kapitoly.

Referenční MP4 SHA-256:
`b79944263185898aa562779aea10c11d7cee0ec3417aeaf71cdb188ba99456fa`.
Varianta s vypálenými titulky:
`03e257aa4287cc0e4ddc41b9a037f17fdb3d266b1545c28d993db913544ff059`.
Hlavní zdrojové vstupy finálního balíku musí odpovídat 126 hashům ze skutečné
reprodukce; package.py při neshodě předání odmítne.

## Reprodukce a bezpečné pokračování

- Zmrazeno 78 souborů; přesný commit a hashe v `video_course/r2/reference.json`,
  úplná Git historie ve `starter-reference.bundle`. Snapshot je izolovaný
  v `.tools/r2-starter-snapshot`; hlavní Git index nebyl stageován ani commitován.
- `.venv/Scripts/python.exe` = Python 3.12.15; produkční média mají vlastní
  `.tools/media-env`. FFmpeg z **imageio-ffmpeg 0.6.0** (verze 7.1), ne 0.8.1.
- Reálný capture používá vlastní profil VS Code R2 a určenou pracovní kopii
  `C:\QA\PlaywrightAcademy`. Nemění zmrazený zdroj projektu.
- `capture_contract.json` svazuje konkrétní take s plánem a audiem. Receipty
  musí odpovídat hashům contractu, pořadí a akcím; jinak render odmítne build.
- Audio se při střihu nesmí roztrhnout tichou vsuvkou. Činnost delší než
  plánovaný výklad vyžaduje opravu režie, ne umělé prodlužování.
- `python video_course/r2/build.py` sestaví pouze referenci z uložených klipů.
  Úplný postup je v `video_course/r2/REPRODUCE_CZ.md`.
- Během capture nespouštět jiné GUI nebo headed testy a neovládat desktop.
  Cizí okno v popředí znamená odmítnutý záběr. Nezavírat uživatelské aplikace.
- PowerShell pipe do Python stdin může poškodit češtinu. Pro úpravy zdrojů
  použít apply_patch nebo explicitní UTF-8, ne Unicode here-string přes pipe.

Původní R1 výstupy zůstávají historické. Staré předání je uchováno v
`docs/ARCHIVE_R1_HANDOFF.md`; jeho technické green nepředstavuje akceptaci
výukové kvality a nesmí přepsat tento mandát R2.
