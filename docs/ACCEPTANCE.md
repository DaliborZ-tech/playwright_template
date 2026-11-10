> **R2: CHANGES_REQUIRED.** Předchozí video není produktově schválené. Platí opravný mandát R2; nejprve referenční kapitola a lidské schválení, teprve potom další produkce.

# Akceptace Playwright Academy

**Aktuální reference R2.1 je APPROVED_REFERENCE.** Vlastník 10. 11. 2026
odpověděl „schvaluji“ na celou referenci. Vizuální i zvukový standard je přijatý
a navazující výroba autorizovaná; zbývající kapitoly vyžadují vlastní ověření.
Doklad: [po_approval.json](../video_course/r21/po_approval.json).
Aktuální důkazy jsou v
[LIVE_EVIDENCE.md](../video_course/r21/LIVE_EVIDENCE.md) a
[REVIEW_R21.md](../video_course/r21/REVIEW_R21.md).

## Předchozí stav reference R2

Nová reference R2 „První vlastní test“ má **5:48.48**, hlas Vlasta a 27 skutečně
navázaných záběrů. Stav je **READY_FOR_HUMAN_REVIEW**; úplné lidské zhlédnutí,
poslech a PO schválení jsou **PENDING**. Další celý kurz zatím nevyrábět.
Podrobná [matice R2](../video_course/r2/ACCEPTANCE_R2.md) odděluje důkazy
reference od dosud nesplněných AC budoucího celého kurzu. Platné pokračování
je v [CONTINUE_HERE.md](../CONTINUE_HERE.md).

## Historická technická kontrola R1

Aktualizace 10. 11. 2026: **Starter Kit, cvičení a celý český videokurz jsou
technicky ověřené.** Distribuční archivy prošly kontrolou a obnovením vstupů
střihu po rozbalení do cesty s mezerou.
Lidská poslechová a pedagogická akceptace zůstává výslovně otevřená.

## Doložené výsledky

| Kontrola | Skutečný výsledek | Důkaz |
|---|---|---|
| Starter Kit společně se všemi řešeními | **44 passed in 40.23s** | `evidence/release-final/` |
| Stejná sada v opačném pořadí | **44 passed in 40.24s** | `evidence/release-reverse/` |
| Viditelný test celé CRUD cesty | 1 passed | `evidence/recorded-commands/08_03.xml`, skutečné headed Chromium |
| Chyba instalátoru v cestě s mezerou | Očekávaný exit 23 | `evidence/installer-exit.json` |
| Zdrojová reference | 78 nezměněných souborů | `video_course/reference_manifest.json` |
| Nová projektová instalace | Funkční `.venv` na existující stanici | Natáčecí kopie `C:\QA\PlaywrightAcademy` |
| Regrese ve videu | 27 passed, 3 deselected, exit 0 | Receipty `01_02`, `11_00`, čerstvý JUnit |
| Řízená chyba a oprava | AssertionError / exit 1, poté pass / exit 0 | `10_00`, `10_04`, PNG/trace/JUnit stejného běhu |
| Původní nahrávky | 97/97, celý decode a shoda 3 archivovaných snímků každého klipu | `evidence/recording-integrity.json` |
| Komentář a původní titulky | 97 odstavců, 10 144 slov, 969 cues | `evidence/speech-validation.json` |
| Finální MP4 | **1:37:11.61**, 1920×1080, H264 / 25 fps, AAC / 48 kHz | `video_course/output/validation.json` |
| Úplné dekódování filmu | Exit 0, prázdný chybový log | Pole `full_decode_*` v `video_course/output/validation.json` |
| Skutečná synchronizace | 97/97, max **21.312 ms** | `video_course/output/audio_alignment.json` |
| Vložené titulky | Všech 969 textů přesně shodných, timing odchylka 0 ms | Stejný audio alignment report |
| Finální obrazová kontrola | Začátky 12 kapitol, konec a vnitřní nástrojové scény; 21 skutečných snímků | `evidence/final-video-frames/manifest.json` |
| Zdroje obrazu | Prostřední snímek každé z 97 scén, reprezentativní nativní snímky a cílené opravy | `evidence/visual-review.json` |
| Nezávislé review | Druhý AI reviewer, konkrétní nálezy a retesty | `docs/REVIEW.md` |
| Archivy a přenositelnost | CRC, manifesty, 78 shodných zdrojů, spojení obou ZIPů a znovusestavení shodných vstupů | `release-audit.json` vedle archivů a kontrolní rozbalení |

## Rozsah a původ videa

Jeden vypravěč Microsoft Vlasta, 12 kapitol a jeden souvislý příběh nad lokální
aplikací. Komentář je syntetizovaný po celých odstavcích. QA se vyslovuje
„kjů ej“. Fonetické úpravy nemění text titulků, přepisu ani kódu.

Video obsahuje skutečný editor, terminál, prohlížeč, Codegen, Inspector,
Trace Viewer a skutečné návratové kódy testů. Vygenerovaný Codegen draft
zůstává zachovaný odděleně od ručně upravené verze. Zdrojový manifest se při
renderu kontroluje; skutečné klipy i hlasy jsou svázané SHA-256.

Finální MP4 SHA-256:
`71bf3706f1c3eb8c173395872a10010ead26ccbdbf8f632a6ddd780dfe1e269f`.
Velikost **200 010 049 B**. Film má 12 platných kapitol a volitelnou českou
mov_text stopu. Vedle něj se předávají SRT a VTT.

Vizuální kontrola je výběrová, nikoli tvrzení nepřerušeného lidského přehrání
celých 97 minut. Celý soubor prošel automatickým dekódováním. ASR rozpoznalo
češtinu ve všech 97 scénách; jde o doplňkovou automatickou kontrolu zvuku.

## Matice kritérií

P = lokálně ověřeno v uvedeném rozsahu, Č = částečně / uvedené omezení.

| Kritéria | Stav | Důkaz nebo omezení |
|---|---|---|
| SK-01 | Č | Nová projektová instalace prošla; čistý nový Windows OS neověřen |
| SK-02, SK-03 | P | Instalace bez administrátorských změn, diagnostika a skutečný návratový kód |
| SK-04 až SK-11 | P | Lokální demo, smoke/regrese, privátní data a reset, stabilní locators |
| SK-12, SK-13 | P | Samostatné případy i skutečné viditelné Chromium |
| SK-14, SK-15 | P | Řízené selhání, trace/PNG, skutečný HTML a JUnit |
| SK-16 | Č | Oddělený externí profil; skutečný firemní systém nebyl kontaktován |
| DOC-01 až DOC-09 | P | České lekce, úkoly, řešení 12 lekcí se 14 ověřenými případy, reference 45 položek a troubleshooting |
| DOC-10 | Č | Simulovaný walkthrough funguje; skutečný začátečník nebyl k dispozici |
| VID-01 až VID-03 | P | Kompletní MP4, všech 12 kapitol a souvislý český komentář |
| VID-04 | Č | Schválený hlas a výslovnost, automatická kontrola 97 scén; plný lidský poslech neproveden |
| VID-05 až VID-09 | P | Skutečné operace, odpovídající zdroj, regrese, chyba/oprava, Codegen a trace |
| VID-10 až VID-12 | P | SRT/VTT, přesné kapitoly, požadovaný profil a úplný decode |
| VID-13 | P | Čitelnost zkontrolována výběrem uvedeným ve vizuální evidenci |
| VID-14 | P | Syntetická data a allowlist; odmítnuté soukromé záběry vyloučené a přetočené |
| VID-15 | Č | Technická a výběrová vizuální kontrola provedena; úplný lidský poslech neproveden |
| VID-16, VID-17 | Č | Scénář a nový test funkčně pokryté simulací; lidské porozumění nebylo měřené |
| VID-18 | P | Oba ZIPy ověřené přes CRC a manifesty; zdroje znovu sestavily stejné vstupy střihu v cestě s mezerou |

Skutečný začátečnický test, čistý nový OS a plný lidský poslech dosud neproběhly.
Automatizace ani druhý AI reviewer se za ně nevydávají. Podrobněji
[známá omezení](KNOWN_LIMITATIONS.md) a [scénář člověka](BEGINNER_WALKTHROUGH.md).
