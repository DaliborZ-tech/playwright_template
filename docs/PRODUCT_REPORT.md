> **R2: CHANGES_REQUIRED.** Předchozí video není produktově schválené. Platí opravný mandát R2; nejprve referenční kapitola a lidské schválení, teprve potom další produkce.

# Playwright Academy – předání produktu

## Aktuální reference R2.1

Opravy podle nezávislé revize jsou v `dist/Playwright_Academy_R21_Reference/`
a jediném úplném `dist/Playwright_Academy_R21_Complete.zip`.
Film má 5:48.48, Vlastu, 30 záběrů včetně nového skutečného Codegenu.
Pauzy jsou přečasované podle významu, cílené zoomy i návraty jsou měřené
ze snímků a titulky jsou nejvýše dvouřádkové. Zvukovou 30s ukázku vlastník
poslechem schválil. Následně **10. 11. 2026 schválil celou referenci R2.1**
výrokem „schvaluji“. Doklad a rozsah navazující výroby jsou v
[APPROVAL_R21.md](../video_course/r21/APPROVAL_R21.md).

Ze ZIPu byly oba filmy a globální titulky reprodukovány byte-identicky;
všech 44 testů prošlo. Důkazy, přesné omezení poslechového souhlasu a platný
další postup shrnuje [CONTINUE_HERE.md](../CONTINUE_HERE.md).

## Předchozí reference R2

Aktuální opravná dodávka je **reference R2, 5:48.48**, nikoli nový celý kurz.
Obsahuje skutečný průchod od prázdného editoru přes DOM a tentýž test
RED→GREEN až po report. Hlas zůstává Microsoft Vlasta z Edge.

Samostatný balík: `dist/Playwright_Academy_R2_Reference/`; úplný archiv
`dist/Playwright_Academy_R2_Complete.zip` obsahuje obě MP4, globální SRT/VTT,
kapitoly, přepis, přehrávač a všechny zdroje reference. Rozsah a schvalovací
brána: [ACCEPTANCE_R2.md](../video_course/r2/ACCEPTANCE_R2.md).
Úplné zhlédnutí a poslech vlastníkem zůstávají **PENDING**.

Obě MP4 prošly úplným dekódováním. Edge 157.0.4341.42 skutečně zobrazil
české titulky včetně diakritiky na začátku, ve středu a na konci.
Ze ZIPu rozbaleného do nové cesty s mezerami vznikly oba byte-identické
filmy i globální titulky; všech 44 testů Starter Kitu a řešení prošlo bez
failure, error nebo skipped. To nenahrazuje lidské posouzení výukové kvality.

## Historická technická dodávka R1

Stav 10. 11. 2026: **technicky ověřená dodávka je připravená k internímu
akceptačnímu ověření.** Lidská poslechová a pedagogická akceptace zůstává otevřená.

Video má **1:37:11.61**, 97 scén, 12 kapitol a **200 010 049 B**. SHA-256:
`71bf3706f1c3eb8c173395872a10010ead26ccbdbf8f632a6ddd780dfe1e269f`.
Obsahuje volitelnou českou titulkovou stopu; v přehrávači vyberte češtinu.

Kurz navazuje na jeden lokální QA Training Portal: přihlášení, vytvoření
požadavku, úprava, smazání, regrese a hledání příčiny chyby. Používá skutečný
VS Code, Python, Chromium, Codegen, Inspector, Trace Viewer a výsledky pytest.
Codegen vytváří výchozí draft, který se v další ukázce vědomě upravuje.

## Co obsahuje distribuce

| Soubor | Účel |
|---|---|
| `Playwright_Academy_Python_CZ_Full_Course.mp4` | Celý český kurz, 12 kapitol, 1920 × 1080 / 25 fps |
| `subtitles_cs.srt`, `subtitles_cs.vtt` | České titulky se správným zápisem odborných termínů |
| `chapters.md` | Časový přehled kapitol |
| `transcript_cs.md` | Úplný komentář |
| `Playwright_Academy_Starter_Kit.zip` | Projekt, demo, testy, Windows spouštěče, výuka, produkční skripty a důkazy |
| `Playwright_Academy_Production_Sources.zip` | Původní záběry, audio, časování, receipty a archivované snímky pro další střih |
| `SHA256SUMS.txt` | Kontrolní součty distribuovaných souborů |
| `release-audit.json` | Výsledek kontroly archivů a přenositelnosti |

Pro studium stačí MP4 a Starter Kit. Produkční archiv je určený k opravám
videa; oba ZIPy se rozbalují do stejného kořene `playwright-academy`.
Začněte jeho README a `scripts\setup_windows.cmd`, potom `scripts\run_smoke.cmd`.
Ruční demo spouští `scripts\start_demo.cmd`. Syntetický veřejný účet je
`tester@example.test` / `Academy123!`. Běžné testy si server spustí samy.

Výuka obsahuje 12 lekcí, pracovní sešit, řešení se 14 testovacími případy, referenci
45 položek, slovník a řešení problémů na Windows. Výchozí ověřený profil je
Windows 11 x64, Python 3.12.15 a Chromium s přesnými verzemi v locku.

## Doložené ověření

- Celý Starter Kit společně se všemi řešeními: **44 passed in 40.23s**.
- Stejných 44 testů v opačném pořadí: **44 passed in 40.24s**.
- Zmrazených 78 výukových souborů zůstalo beze změny.
- Ve videu je skutečná regrese 27 passed / 3 deselected, řízené selhání
  s návratovým kódem 1 a následná oprava s návratovým kódem 0.
- Všech 97 zdrojových klipů prošlo úplným dekódováním, ověřením SHA-256
  a porovnáním tří archivovaných snímků.
- Všech 97 odstavců komentáře a 969 titulků prošlo kontrolou původního textu,
  metadat časování a dekódování. Lokální ASR rozpoznalo češtinu ve všech scénách.
- Finální film prošel celým dekódováním bez chyby. Zvuková synchronizace
  prošla ve všech 97 scénách, s největší odchylkou **21.312 ms**. Všech
  969 vložených titulků se textem i časováním shoduje s dodaným SRT.
- Oba archivy prošly CRC a kontrolou každé položky manifestu. Všech 78
  zmrazených souborů zůstalo identických; ZIPy se spojí bez konfliktů.
  Po rozbalení do cesty s mezerou se znovu sestavily přesně stejné vstupy střihu.

Konkrétní reporty jsou v `evidence/release-final/`, `evidence/release-reverse/`,
`evidence/recorded-commands/`, `evidence/recorded-artifacts/` a
`video_course/output/`. Rozsah vizuální kontroly zaznamenává
`evidence/visual-review.json`; akceptační matici `docs/ACCEPTANCE.md` a
samostatnou AI revizi `docs/REVIEW.md`.

## Hlas, soukromí a meze ověření

Jediným vypravěčem je syntetická Microsoft Vlasta. Výslovnost QA je „kjů ej“.
Fonetický slovník mění jen řečový vstup; titulky, přepis i kód zachovávají
správný pravopis. Nahraný komentář je přiložený, takže oprava střihu nevyžaduje
další požadavek do online TTS. Dostupnost ani kvótu komunitní integrace
Edge TTS negarantujeme.

Distribuce neobsahuje skutečná firemní přihlášení ani `.env`. Výuková data
a veřejné demo heslo jsou syntetické. U kopií diagnostických důkazů se
odstraňuje osobní část cest a hostname JUnit; manifest přiznává redakce
a původní i distribuované kontrolní součty. Výsledky testů a zmrazený kód se
nemění. Redigovaný trace byl otevřený ve skutečném Trace Vieweru a zachoval DOM
i chybné očekávání.

Skutečný začátečník, úplný lidský poslech a čistý nově nainstalovaný Windows
nebyly k dispozici. Simulovaný walkthrough, automatické kontroly a druhý AI
reviewer je nenahrazují. Připravený scénář pro člověka je v
`docs/BEGINNER_WALKTHROUGH.md`; další omezení v `docs/KNOWN_LIMITATIONS.md`.
