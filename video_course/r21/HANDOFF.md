# Pokračování Playwright Academy — aktuální reference R2.1

Původní 97minutový produkt zůstává **CHANGES_REQUIRED**. R2 má od vlastníka
předanou nezávislou revizi CONDITIONAL PASS jako koncept a opravný mandát
R2.1. **10. 11. 2026 vlastník odpověděl „schvaluji“ na celou referenci.**
Aktuální R2.1 je **APPROVED_REFERENCE** a její vizuální i zvukový standard
je přijatý pro navazující výrobu. Doklad: `video_course/r21/po_approval.json`.
Microsoft Vlasta **cs-CZ-VlastaNeural** zůstává zachovaná.

## Hotová dodávka

- `dist/Playwright_Academy_R21_Reference/` — samostatný balík reference.
- `dist/Playwright_Academy_R21_Complete.zip` — obě MP4, globální SRT/VTT,
  přepis, kapitoly, přehrávač, srovnání zvuku a kompletní editovatelné sources.
- Obě MP4 mají **5:48.48**, 1920×1080/25 fps, H.264/AAC. Nově je 30 záběrů,
  včetně skutečného Codegenu, browseru a nativního Inspectoru.
- Varianta `_Titulky.mp4` má české titulky přímo v obraze. Pro přepínatelné
  WebVTT spusťte `PREHRAT.cmd`; server je pouze na 127.0.0.1.

## Konkrétní opravy R2.1

- Pauzy: medián subtitle gaps **1,018 → 0,377 s**, součet **67,55 → 30,24 s**.
  Počet pravidelných mezer 0,85–1,20 s **62 → 0**. V původním PCM bylo
  64 tichých úseků alespoň 0,7 s pod −45 dB; v upraveném PCM žádný.
- Jde o střih změřeného ticha, bez natahování řeči nebo překrývání hlasů.
  `audio_edits.json` má vzorkově přesnou mapu. Nezávislý AI reviewer celé
  výsledné PCM skutečně rekonstruoval a porovnal byte po bytu.
- **Skutečný lidský poslech 30 s je schválený.** Vlastník odpověděl:
  „Rytmus po úpravě je v pořádku, slova nejsou useknutá.“ Souhlas je vázán
  na SHA obou WAV v `comparison/human_listening_review.json` a neplatí
  automaticky pro celý nový film.
- Tři vytčené scény jsou kratší: funkce 26,24→23,08 s, DOM 28,44→25,32 s,
  očekávání 22,20→19,56 s. Konkrétní popisky se vážou na argument page,
  dvojtečku, roli heading, název a to_be_visible. Kamera pomáhá čtení,
  není vydávaná za novou práci v aplikaci.
- Dvě účelná přiblížení mají **2,4 s**, 24 skutečně změřených různých
  velikostí a změnu přibližně 1,38×. Nezávisle byly změřeny i 2,4s návraty
  do kontextu. Klipy a snímky jsou v evidence/zoom.
- Všech 73 titulků zachovává kanonický text; žádný nemá méně než 1 s nebo
  3 slova. SRT/VTT jsou nejvýše dvouřádkové. Cues 42/72 byly cíleně znovu
  ověřeny v Edge, včetně skutečné poslední věty v 5:45.
- Nový Codegen vytvořil skutečný E-mail textbox locator a fill. Vygenerovaný
  návrh byl samostatně spuštěn: 1 passed. Existující skutečné RED/GREEN,
  DOM a reporty zůstávají zachované včetně původních raw a parent SHA.

## Ověření a zdroje

- Kompletní nová ZIP distribuce byla rozbalena do nové cesty s mezerami.
  Oba filmy a globální SRT/VTT byly sestaveny **byte-identicky** bez TTS;
  všech **44 testů** Starter Kitu a řešení prošlo bez error/failure/skipped.
  Prostředí: existující připnutý media venv a stejné Windows fonty; nebyla
  předstírána čistá instalace nového Windows.
- Balení porovnává finální render vstupy s hashi skutečně testovaného
  rozbaleného projektu. Celý ZIP prochází CRC a kontrolou SHA všech payloadů.
- Starter Kit zůstává zmrazený na **78 souborech**, commit
  `129d317771d91da04e31e8150a2111188f9ae51f`; přiložen je plný Git bundle.
- R2.1 důkazy a skripty: `video_course/r21/`. `LIVE_EVIDENCE.md` přímo mapuje
  zmrazené soubory, skutečný nodeid, JUnit, reporty, raw, Codegen a přehrávání.
- `REVIEW_R21.md` je technická, zdrojová a výběrová obrazová AI revize
  dokončená před PO rozhodnutím. Následný výslovný souhlas vlastníka s celou
  referencí je v `po_approval.json`, přehled v `APPROVAL_R21.md`.
  Původní PENDING ve starších měřeních a timeline je historický snapshot.

Finální MP4 SHA-256:
`6c53aeb9e0b0bc7828e115c2868399b6f2a54411835c92a8ab0893a882d42b20`.
Vypálené titulky:
`c3ca84bdde17c1b5a9e038c8eb88b61c158fec027554d4b00c0aabcca7ea50f4`.

## Další krok

Schvalovací brána reference je splněná: `full_course_build_authorized=true`.
Navázat výrobou zbývajících kapitol podle standardu R2.1, s reálnými úkoly,
akcemi, srozumitelnými odstavci, měřeným focus/zoom a českými titulky.
Stav navazující výroby: **AUTHORIZED_NOT_STARTED**; výchozí stav je v
`video_course/production_status.json`. Reference a její hashe se zachovají.
Akceptace nového celého kurzu bude až po jeho dokončení a ověření všech AC;
starý 97minutový produkt se tímto rozhodnutím nepovažuje za opravený.

Starší R2 soubory a dodávka zůstávají historicky zachované. Nepřepisovat je
novými hashi. Aktuální offline sestavení:
`python video_course/r21/build.py`, potom `python video_course/r21/approval.py`;
balení `package.py` rozhodnutí aplikuje automaticky po ověření hashů.
Úplný postup je v
`video_course/r21/REPRODUCE_CZ.md`. Python3.12, imageio-ffmpeg **0.6.0** /
FFmpeg7.1, Segoe UI. Hlavní Git index nebyl kvůli freeze stageován ani commitován.
