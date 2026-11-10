# Nezávislá technická revize

Revize: 9. 11. 2026. Provedl druhý AI agent odlišný od autora implementace.
Jde o nezávislé technické posouzení v rámci tohoto pracovního prostředí,
nikoliv o lidské pedagogické hodnocení, poslechovou kontrolu nebo skutečný
uživatelský test začátečníka. Kontrola probíhala nad rozpracovaným stavem;
níže jsou zaznamenány původní nálezy i následné nezávislé ověření oprav.

## Závěr při prvním průchodu

**Celý produkt zatím není připraven k akceptaci.** Reálný finální videokurz
nebyl předložen. Nelze potvrdit český komentář, synchronizaci titulků,
čitelnost všech záběrů, úplnost kapitol ani skutečné poslechové hodnocení.
Starter Kit má srozumitelný základ a oddělené lokální a externí testování,
ale první průchod odhalil opravitelné chyby uvedené níže.

## Zjištění

### R1 · Vysoká · Chybný návratový kód instalačního spouštěče

Soubor: `scripts/setup_windows.cmd`, větev existující `.venv`.
`exit /b %errorlevel%` uvnitř bloku v závorkách se expanduje před spuštěním
bootstrapu. Neúspěšný bootstrap tak může vrátit předchozí úspěšný kód.
Současně se v další větvi selhání instalace zaměňuje za selhání Python launcheru
a spouští jiný interpreter. Doporučení: oddělit detekci interpreteru od jeho
spuštění, použít `goto`/podprogram nebo delayed expansion a ověřit skutečnou
chybovou větev. Nestačí kontrola úspěšné instalace.

### R2 · Střední · Neplatné heslo s diakritikou vyvolá HTTP 500

Soubor: `demo_app/app.py`, funkce `login` a obdobně kontrola CSRF.
Reprodukováno přes Flask `test_client`: správný syntetický e-mail a neplatné
heslo obsahující český znak → HTTP 500 a `TypeError`, protože
`hmac.compare_digest` nepodporuje ne-ASCII řetězce typu str. Doporučení:
porovnávat UTF-8 bytes; neplatný vstup musí vyústit v běžnou přihlašovací chybu
nebo 403, nikdy v neošetřenou výjimku.

### R3 · Střední · Chybný JSON typ obejde validační odpověď

Soubor: `demo_app/app.py`, funkce `validated_record`.
Reprodukováno autentizovaným požadavkem s platným CSRF a `owner: []`:
HTTP 500, protože členství v množině vyžaduje hashovatelnou hodnotu.
Stejná třída problému je u `status`. Doporučení: před ověřením členství
ověřit typ str a pro chybný typ vracet 400 bez změny dat. Doplnit ověření
seznamu, objektu a null, nejen textových hodnot z UI.

### R4 · Střední · pytest --debug není Playwright Inspector

Soubor: `training/lessons/10.md`.
`pytest --debug` zapisuje interní diagnostiku pytest; nezapíná běžný
Playwright Inspector. Doporučení: ukázat oficiální `PWDEBUG=1` a `pytest -s`,
včetně odstranění proměnné po dokončení. Přepínače novějšího pluginu uvádět
jen podle skutečného `pytest --help` a jasně odlišit jejich účel.

### R5 · Nízká · Kontrola URL neodmítne všechny přihlašovací údaje

Soubor: `tests_external/conftest.py`.
Podmínka `or parsed.username` dovoluje URL s prázdným uživatelským jménem a
neprázdným heslem. Doporučení: odmítnout jakýkoliv neprázdně přítomný userinfo
pomocí `parsed.username is not None or parsed.password is not None`.
Jde o preventivní kontrolu konfigurace, nikoliv o prokázaný únik skutečného
tajemství. Žádná skutečná přihlašovací data nebyla při revizi použita.

### R6 · Střední · Odhlášení během načítání způsobí neošetřenou výjimku

Soubor: `demo_app/app.py`, GET `/api/records` po simulovaném zpoždění.
Reprodukováno dvěma Flask clients se stejnou session cookie: rozběhnutý
GET záznamů, po 50 ms POST logout. Odhlášení vrátilo 302, rozběhnutý GET
vrátil 500, protože mezitím zmizel workspace. V UI může nastat při okamžitém
odhlášení během načítání dashboardu. Doporučení: po zpoždění pod zámkem
ověřit existenci workspace a pro zrušenou relaci vrátit řízené 401;
stejný přístup použít na ostatních přímých přístupech do session úložiště.

## Skutečně provedené kontroly

- `python -m ruff check .`: PASS při prvním průchodu.
- `python -m pip check`: PASS, žádné porušené požadavky balíčků.
- `pytest --collect-only -q -o addopts=''`: 20 případů, bez teaching testu.
- Smíšený sběr `tests_external tests/examples --external`: odmítnut pomocí
  UsageError před browser během. Toto potvrzuje pojistku oddělení obou sad.
- Flask test client: měnící požadavek bez CSRF → 403; cizí Host → 400.
- Zdrojová kontrola: loopback bind, vypnutý debug server, náhodný session secret,
  HttpOnly a SameSite cookie, ochrana měnících akcí CSRF, escapované vykreslování
  uživatelských textů, oddělené session seznamy a reset aktuální relace.
- Zdrojová kontrola testů: stabilní role/label/test ID lokátory, web-first
  assertions, žádný `time.sleep` pro synchronizaci UI, samostatně zapínaná chyba.
- `ruff format --check`: při prvním průchodu ještě potřebovalo formátovat
  nově doplněná výuková řešení. Jde o průběžný stav, nikoliv finální výsledek.

## Co tato revize nepotvrzuje

Browser testy nebyly druhým agentem spouštěny souběžně s autorem, aby se
nepřepisovaly sdílené reporty. Konečné výsledky musí být doloženy skutečnými
HTML/JUnit artefakty autora. Není ověřena čistá Windows instalace, firemní
proxy ani Azure pipeline. Není provedeno uživatelské testování člověkem.
TTS a video vyžadují samostatný technický i pedagogický průchod; samotná
existence MP4 ani úspěch ffprobe nestačí.

## Požadovaný následný průchod

Po opravách znovu ověřit úplnost lokálních odkazů, všechny ukázky řešení,
běžný i opačný pořádek regrese, headed běh a řízené selhání se screenshotem/trace.

## Nezávislé ověření oprav

Po úpravách autora provedl tento reviewer nový průchod. Bez souběžného
browser běhu a bez přepisování sdílených reportů:

| Nález | Ověřený stav |
|---|---|
| R1 | PASS: dispatch přes goto, detekce launcheru oddělena od bootstrapu, návratový kód čten mimo blok. Předložený důkaz autora `evidence/installer-exit.json` obsahuje očekávaný i skutečný CMD exit 23 v cestě s mezerami. Reviewer tento soubor přečetl; selhávající instalaci sám znovu nespouštěl. |
| R2 | PASS: neplatné heslo s diakritikou vrací běžnou login stránku 200; neplatný CSRF s diakritikou 403, bez HTTP 500. |
| R3 | PASS: owner i status jako seznam, objekt a null vracejí 400 ve všech šesti případech. |
| R4 | PASS: lekce vysvětluje PWDEBUG=1, pytest -s i následné odstranění proměnné; odlišuje interní pytest --debug. Ověřeno proti skutečnému pytest --help. |
| R5 | PASS: URL s prázdným username a heslem odmítnutá; URL s username-only odmítnutá; čistá lokální HTTP URL přijatá. |
| R6 | PASS: zopakovaný souběžný GET/logout vrací řízené 401 a 302, bez neošetřené 500. |

`ruff check .` a `ruff format --check .` po úpravách: PASS, 58 Python souborů
v okamžiku této kontroly. Pozdější přírůstky vyžadují vlastní ověření.
Toto uzavření technických nálezů nemění neověřený stav finálního videokurzu
ani nenahrazuje čistou Windows instalaci a skutečný začátečnický test.

## Následná kontrola instalace, evidence a produkční připravenosti

Další průchod byl pouze read-only: nebyly spuštěny nové testy, prohlížeče ani
instalátory souběžně s autorem. Reviewer zkontroloval následující skutečné soubory:

- `evidence/installer-exit.json`: expected 23, actual 23, pass true, metoda
  skutečného CMD dispatcheru v cestě s mezerami. Tím je doplněn chybějící
  předložený runtime důkaz R1.
- Aktuální `setup_windows.cmd`: detekce Python launcheru nově porovnává řetězec
  errorlevel s nulou a má fallback pro `Astral/CPython3.12`. To řeší i vysoký
  nenulový návratový kód launcheru, u kterého `if errorlevel 1` nemusí odpovídat
  požadované obecné kontrole nenulového výsledku. Prostor pro opakování bootstrapu
  po jeho skutečné instalační chybě již není ve stejné větvi.
- `C:\QA\PlaywrightAcademy\.venv\pyvenv.cfg` potvrzuje existující oddělenou
  projektovou venv Python 3.12.15 a příkaz vytvoření v této cestě. Autor uvádí
  úspěšnou instalaci z nové venv přes setup; reviewer instalaci neopakoval.
  Jde stále o existující stanici, nikoliv čistý nový Windows OS.
- JUnit artefakty byly skutečně XML parserem načteny: `full` 20 případů,
  `reverse` 29, `solutions` 14, `api` 9, `headed` 2. Všechny načtené sady mají
  failures=0, errors=0 a skipped=0. Jejich počty souhlasí s průběžnou akceptací.
- Aktuální `tests/conftest.py` používá pro automatický testovací server
  `werkzeug.serving.make_server`, `shutdown`, join a `server_close`. Ruční demo
  nadále používá Waitress. Rozlišení je v `docs/ACCEPTANCE.md` vysvětlené.
  Změna fixture po starších reportech vyžaduje nový finální regresní běh
  proti skutečně zmrazené zdrojové verzi.
- `video_course/narration/voice_sample.wav` je skutečný čitelný mono WAV,
  16 kHz a 30,28 sekundy. To potvrzuje technickou existenci audio vzorku,
  nikoliv poslechovou srozumitelnost nebo dokončený komentář celého kurzu.
- `video_course/recordings/desktop_probe.mp4` skutečně existuje.
  Jeho obraz reviewer vizuálně nehodnotil a neoznačuje tento probe za kurz.
- Srovnání hlasů má vlastní README a JSON s oběma vzorky. Průběžná akceptace
  správně uvádí, že konkrétní hlas vybírá vlastník po poslechu. Další generování
  komentáře nesmí předbíhat jeho výběr.

Průběžná matice v `docs/ACCEPTANCE.md` nepředstírá hotový produkt: finální
MP4, úplné titulky, přesná časová osa, poslechová QA a část interaktivního
walkthrough jsou otevřené. Finální distribuce tedy dosud není schválená.

Drobnost k dokončení konzistence: úvod `video_course/README.md` při této
kontrole stále deklaroval Jakuba jako hlas kurzu, zatímco vlastník právě
vybírá ze srovnání. Doporučení: označit jej za preferovaný či ukázkový hlas
a výslovně uvést čekající konečný výběr. Nejde o technickou blokaci Starter Kitu.

## Nezávislá revize souvislé produkce s Vlastou

Vlastník následně schválil Vlastu s fonetickými náhradami, požaduje souvislé
odstavce, původní pravopis titulků a žádné další hlasové vzorky. Tento průchod
proto nepožadoval nové vzorky a neprováděl syntézu, browser ani GUI operace.
Zkontroloval zdroje `continuous_speech.py`, `prepare_spoken_text.py`,
`build_course.py`, `record_course.py`, `studio.py` a oba soubory doplňkového
komentáře. Izolované testy používaly jen čisté funkce mapování vytažené přes AST.

### Ověřené opravy titulků

- Původní problém řezu uvnitř identifikátoru byl reprodukován: služba může
  rozdělit `test_login_page` na více boundaries, ale původní titulkový text se
  nesmí rozdělit vloženou mezerou. Nová kontrola dovoluje řez pouze po whitespace
  původního textu. Izolovaný retest zachování identifikátoru: PASS.
- Původní funkce přijala metadata obsahující pouze první slovo a připsala k nim
  celý zbytek odstavce. Nová kontrola pokrytí alfanumerického vstupu mezi tokeny
  i na konci taková neúplná metadata odmítá. Izolovaný retest: PASS.
- Víceslovné fonetické náhrady `BrowserContext`, `Trace Viewer` a
  `get_by_role` se vracejí do původního titulkového pravopisu; chráněný
  identifikátor `test_python` se nezmění. Izolovaný retest: PASS.
- Všech 97 odstavců aktuálního plánu bylo zkontrolováno syntetickými boundaries
  dělícími i underscores a čísla: bez chyby přesného textového roundtripu.
  Jde o test mapování, nikoliv důkaz skutečného znění audia.
- Uložené skutečné metadata `03_01_8b5edafbdaf3.boundaries.json` se novou funkcí
  promítají do čtyř cues a zachovají původní text. Není nutné opakovat TTS.

### Konkrétní otevřené produkční nálezy

| ID / závažnost | Zjištění a požadovaná oprava |
|---|---|
| V1 · Střední | Cache v `synthesize_scene` vrací staré cues při platném audio hashi, aniž je přepočítá aktuálním mapováním. Oprava algoritmu ani smazané SRT/VTT tak nemusí být promítnuty. Při cache hit znovu promítnout uložené boundaries a obnovit titulky, bez nové syntézy audia. |
| V2 · Vysoká | `record_course --resume` identifikuje záběr pouze audio podpisem a screen popisem. Nezahrnuje hash předváděného kódu, demo aplikace či locku; změněný zdroj tak může ponechat starý záběr jako `retained_verified_recording`. Vyžadován zmrazený zdrojový manifest v identitě a receiptu. |
| V3 · Vysoká | Terminálová scéna odešle Enter, ale před statusem `recorded` nekontroluje dokončení příkazu, skutečný exit code ani příslušný JUnit. Nevyrábí falešný stdout, přesto nelze z úspěchu FFmpeg odvozovat úspěch testu. Potřebný je skutečný dokončovací důkaz; řízená chyba musí výslovně očekávat exit 1. |
| V4 · Vysoká | `ensure_demo` po překopírování zdrojů přijme starší běžící demo podle samotného service jména v `/health`. Python proces přitom může držet předchozí kód v paměti. Natáčení potřebuje vlastní proces aktuální zmrazené verze nebo ověřený build fingerprint; nesouhlasící cizí proces neukončovat naslepo. |
| V5 · Střední | Záběry kapitoly 8 s doplňkovým výkladem odkazují na `test_records.py:1`, kde je vytvoření, zatímco komentář rozebírá kompletní `test_12` níže. Úvod kapitoly 7 říká, že na obrazovce jsou tři chybná hesla, ale plán ukazuje `tests/conftest.py`. Upřesnit zdroj, řádek a případné přepínání/scroll podle tématu odstavce. |

### Kontrola obsahu, pravdivosti a soukromí

Oba soubory doplňkového komentáře mají kapitoly 01–12 a souvislý výklad;
nejsou to čtené seznamy metod. Obsahově odpovídají základním principům
projektu: lokální data, oddělené relace, relativní URL, parametrizace,
očekávaná chyba, oddělené reporty a Codegen jako pomocník. Označení screenshotu
v kapitole 10 jako „správné přihlášení“ je vhodné zpřesnit na přihlašovací
formulář, aby nevyznělo jako tvrzení o úspěšné autentizaci.

Ve zkontrolovaných akcích Studio jsou skutečné Playwright/GUI operace a
skutečné příkazy. Reviewer nenašel ručně konstruované PASS terminálové řádky.
Tato skutečnost nenahrazuje chybějící kontrolu dokončení příkazu z V3.

Zdroje používají samostatné natáčecí `C:\QA\PlaywrightAcademy`, vlastní VS Code
profil, relativní cesty do editoru a syntetická data. V aktuálních skriptech
akcí nebyla nalezena natvrdo vložená osobní uživatelská cesta pro zobrazení.
Z toho ale nelze potvrdit nepřítomnost soukromých cest ve skutečném videu:
nutná je vizuální kontrola nahrávek, zejména tracebacků, reportů a Trace Vieweru.
V tomto průchodu reviewer obraz ani zvuk neprohlížel.

Finální souvislé MP4 dosud není předložené. Technické opravy titulků samy
neuzavírají dokončení videa, synchronizaci výkladu s obrazem ani jeho kvalitu.

## Retest V1–V5 po dokončení audia a zavedení zdrojového manifestu

Provedeno během přípravy skutečného natáčení. Reviewer neovládal GUI,
nespouštěl browser, testy s okny ani novou syntézu a nezměnil zmrazené zdroje.
Následující výsledky vycházejí z read-only kódu, metadat a existujících médií.

### Úplnost zvuku, původního textu a titulků

Nezávislý průchod zkontroloval všech **97 aktuálních audio scén**:

- Všude je `cs-CZ-VlastaNeural`, podpis odpovídající aktuálnímu odstavci,
  řečové verzi, slovníku a rychlosti; soubor má shodný uložený SHA-256.
- Skutečné word boundaries se aktuální mapovací funkcí promítnou beze ztráty
  původního textu. Všechna uložená cues souhlasí s novým výpočtem i s plánem.
- Existuje a bylo načteno **194 SRT/VTT souborů**. Po sjednocení whitespace
  mají celý původní text příslušného odstavce a odpovídající počet cues.
- Bylo zkontrolováno **919 cues**: kladné intervaly, žádné překryvy větší
  než 1 ms a žádný konec za probovanou délkou audia s tolerancí 0,1 s.
- Součet délek načtených z metadat FFmpeg je **92,33 minuty**. Je to délka
  samostatných audio scén, nikoliv důkaz existence finálního stejně dlouhého MP4.
- Obě náhrady původního `QA` mají přesně vlastníkem požadované `kjů ej`
  (ověřeno i hodnotou Unicode U+016F); v zobrazovaném textu a titulcích zůstává
  původní `QA`. Toto není chyba k opravě ani žádost o další vzorek.
- Nejdelší cue má 8,273 s ve scéně 03_01, protože zachovává původní nedělitelné
  tokeny. Nejde o ztrátu textu; čitelnost výsledného celého videa zůstává k QA.

Tento audit neobsahoval poslech všech scén ani úplné dekódování veškerého
audia. Nepotvrzuje výslovnost, přirozenost, pedagogickou kvalitu nebo dokonalou
synchronizaci se skutečným děním na obrazovce.

### Stav jednotlivých oprav

| Nález | Aktuální nezávislé zjištění |
|---|---|
| V1 | PASS. Cache nově vždy přepočítává cues z uložených boundaries a obnovuje SRT/VTT; ukládá captions_algorithm=2. Kontrola všech aktuálních audio sidecarů, plánu a titulků nenašla nesoulad. |
| V2 | Zdrojová oprava PASS. Identity i receipt nyní obsahují source_reference. První rozšíření na 58 souborů ještě vynechávalo spouštěče a některé zobrazované dokumenty. Nový manifest má **78 souborů**, zahrnuje scripts/, .env.example i oba konkrétní docs soubory a read-only kontrola nenašla žádnou změnu jeho položek. Autor oznámil přetočení starších scén pod novým hashem; staré 58souborové receipty nejsou finální důkaz. |
| V3 | Výrazně opraveno, zbývá kontrola konkrétního výsledku JUnit. Prompt ukládá skutečný LASTEXITCODE po dokončení příkazu, předem jej nastavuje na sentinel777; recorder odmítá nesprávný exit a řízená chyba očekává1. Historický receipt01_02 skutečně obsahuje exit0. Samotný exit1 ale ještě nerozlišuje zamýšlený assertion od setup/teardown erroru; před přijetím chybové scény je nutné ověřit čerstvý testcase, failures1, errors0 a související nové artefakty. |
| V4 | Zdrojová oprava PASS. Demo zachytí build_id při create_app a recorder jej porovnává s očekávaným fingerprintem zdrojů. Jiná běžící verze je odmítnutá bez ukončení cizího procesu. Reviewer kvůli souběžnému natáčení nevytvářel nový proces ani neměnil soubory. |
| V5 | Obsahová oprava je ve zdroji. Kapitola8 otevře místo definice test_12; kapitola07_00 přepne na parametrizovaná hesla podle skutečného cue se související větou. Zůstává níže uvedená koordinační chyba identity versus dodatečně změněný screen.line; skutečné záběry těchto kapitol ještě nebyly předloženy k vizuální kontrole. |

### Otevřené body před finálním sběrem

1. `prepare_scene` u kapitoly8 mění `scene['screen']['line']` až poté, co
   `main` spočítá identity. Receipt pak obsahuje efektivní řádek jiný než ten,
   který byl součástí podepsaného screen popisu. Normalizovat efektivní screen
   před výpočtem identity nebo zachovat nezměněný raw screen a evidovat
   efektivní řádek samostatně. Jinak poctivá finální kontrola může záznam odmítnout.
2. Řízená chyba potřebuje čerstvý JUnit důkaz očekávaného assertion, nikoliv
   pouze exit1. Pro úspěšné pytest scény ověřit nenulový počet provedených
   testcase a failures/errors0. Soubory se nemají kvůli tomu ručně měnit.
3. Codegen je při `--resume` nově atomická skupina09_00–09_02 a tyto tři
   záběry se opakují společně, čímž se opravuje ztráta živého stavu po restartu.
   Stejnou závislost je vhodné uplatnit i při přímém `--start 09_01` nebo
   `--start 09_02` bez resume; takový nový proces také nemá předchozí nahrávku.

### Omezená vizuální kontrola existujících záběrů

Bez otevření či ovládání GUI byly z již uložených médií prohlédnuty reprezentativní
snímky01_00 a01_02. První ukazuje skutečný lokální Dashboard a syntetická data.
Druhý zachycuje běžící pytest a v pozdním snímku25,7 s skutečný terminálový
souhrn **27 passed, 3 deselected in 23.19s** s návratem promptu.
Zobrazená cesta je `C:/QA/PlaywrightAcademy`; ve zkontrolovaných snímcích nebyla
nalezena osobní uživatelská cesta. Byl vidět doporučovací toast VS Code pro
rozšíření Python, tedy drobný rušivý prvek, nikoliv falešný testovací výsledek.

Autor tyto první záběry následně označil k přetočení kvůli rozšířenému
manifestu a úpravě terminálového panelu. Uvedená vizuální kontrola proto
popisuje historické skutečné záběry a nesmí se zaměnit za schválení jejich
budoucích náhrad nebo celého finálního kurzu. Finální renderer a kompletní
audiovizuální kontrola dosud nejsou uzavřené.

## Stav při ukončení práce vlastníkem

Práce byla na výslovný pokyn vlastníka ukončena do dalšího dne. Po tomto
pokynu reviewer již nespouštěl žádné testy, browser, GUI, rendering ani produkci;
dokončil pouze tento zápis. Celý kurz zůstává nedokončený a neschválený.

### Poslední nezávisle zkontrolované opravy

- V3 je ve zdroji doplněné o čerstvý JUnit, správný konkrétní failure testcase,
  `AssertionError`, failures1/errors0 a čerstvý screenshot/trace. Existující
  důkaz01_02 byl nezávisle načten: **27 testcase, 0 failures, 0 errors**,
  checksum souhlasí a hostname chybí. Nejde o opakovaný testovací běh reviewera.
- Codegen skupina se podle aktuálního zdroje doplňuje také při přímém startu
  uprostřed skupiny bez `--resume`.
- `prepare_scene` nově používá kopii screen a oddělený `effective_screen`;
  kanonický popis pro výpočet identity se již nemění. Tato oprava byla
  zkontrolována zdrojově, nikoliv novým GUI během.
- Renderer vyžaduje neměnný výukový manifest, odpovídající podpis audia,
  skutečné word boundaries, technický profil klipu, terminálový výsledek
  a konkrétní JUnit. Původně chyběl digest předaného klipu; aktuální zdroj
  již vyžaduje `clip_sha256` a stav ověření klipu.
- Nový `verify_recordings.py` podle zdrojové kontroly plně dekóduje klip,
  porovnává RGB obsah tří archivovaných snímků a kontroluje nezměněný hash
  před/po. Teprve poté atomicky doplní integritní receipt. To je technická
  kontrola konzistence, nikoliv úplná vizuální ani poslechová revize obsahu.
- Velký centrální název kapitoly byl změněn na kompaktní horní titulek.
  Finální záběry s touto úpravou dosud nemají úplnou nezávislou vizuální QA.
- Byla odhalena možnost zabalit staré MP4 s nově přepočtenými titulky po
  `--prepare-only`. Aktuální zdroj rendereru nově váže validaci na hashe
  navazujících podkladů a zneplatňuje ji při jejich změně; balení tyto vazby
  vyžaduje. Oprava byla přečtena ve zdroji, finální integrační předávka ještě
  neproběhla.

### Skutečné ověření krátkého renderu

Z již existujícího render smoke byl read-only extrahován vložený mov_text
do paměti. Jeho čtyři cues přesně odpovídají původnímu SRT po sjednocení
whitespace. SHA-256 ukázkového MP4 odpovídá uložené validaci, decode.log je
prázdný a výstup je správně označený `sample_only=true`. Není to důkaz
kompletního vícekapitolového renderu. Starší smoke validation obsahuje
osobní projektovou cestu ve výpisu FFmpeg; nesmí se bez redakce vydávat
jako distribuovaný podklad. Aktuální renderer již obsahuje redakci kořene.

### Otevřená předávka pro pokračování

- Dokončit skutečné nahrávky, jejich integritní receipty, finální render
  a validaci svázanou se všemi výslednými podklady. Krátký smoke nepokrývá
  časování spojů všech scén ani finální úplnost 12 kapitol.
- Archivovat a přibalit původní řízený screenshot/trace odkazovaný v
  `junit_result.artifacts`. Při kontrole balicí allowlist tyto konkrétní
  workspace artefakty ještě nepřebíral; samotný receipt by odkazoval mimo archiv.
- Přibalit skutečný `evidence/codegen/original_codegen_draft.py`; při kontrole
  v balicí allowlist chyběl. Export nesmí být nahrazen ručně vytvořeným příkladem.
- Dokončit kontrolu přenositelnosti obou archivů, jejich návazností a hashů.
  ZIPy ani celá finální distribuce nebyly tímto reviewerem akceptovány.
- Dokončit vizuální kontrolu reprezentativních míst všech kapitol a jasně
  popsat rozsah zvukové kontroly. Automatický ASR audit byl podle autora
  rozpracovaný; reviewer jeho finální výsledek nepřevzal ani jej neoznačuje
  za lidský poslech. Žádný další hlasový vzorek se nepožaduje.

## Offline kontrola při pokračování dne 10. 11. 2026

Vlastník výslovně pokračoval v plném kurzu. Tento průchod neovládal GUI,
browser ani foreground a nespouštěl nové testy, natáčení nebo TTS. Změnil se
pouze tento dokument. Finální video ani finální distribuce ještě neexistují.

### Zkontrolované opravy archivace a vazeb

- `terminal_junit` nově kopíruje skutečný čerstvý PNG, trace a případné
  browser video do per-scene `evidence/recorded-artifacts`. Ověřuje shodný
  checksum zdroje a archivu; pro failure/fixed uchovává také HTML a XML.
  Původní workspace relativní cesta, archivní cesta i digest jsou v receiptu.
- Balicí allowlist nyní zahrnuje recorded-artifacts a vyžaduje skutečný
  `evidence/codegen/original_codegen_draft.py`. Dosud existující preflight
  draft není vydáván za tento budoucí skutečný export. Chybějící finální
  export se nemá při balení tiše přeskočit.
- Read-only vyhodnocení allowlistu potvrdilo zahrnutí všech **78 zmrazených
  zdrojů**. Neobsahuje `.env` ani projektovou `.venv`. Kontrola jejich
  aktuálních hashů rovněž neodhalila změny výukové reference.
- Renderer kontroluje digest MP4 z integritního receiptu, podpis komentáře,
  odpovídající JUnit a původní text cues. Finální validace je svázaná s
  timeline, SRT/VTT, kapitolami, přepisem a výukovou referencí; balení tyto
  vazby vyžaduje. Samotný úspěšný checksum videa již nestačí.
- Podle načteného průběžného integritního souhrnu bylo na začátku tohoto
  průchodu ověřeno14 z97 klipů. Toto číslo není závěrečná akceptace kurzu.

### Konkrétní otevřené nálezy před funkční distribucí

**D1 · Vysoká · Balení vyžaduje neexistující raw metadata17 audio scén.**
`package_release.py` bezpodmínečně přidává `.boundaries.json` pro každé audio.
Nezávislá kontrola skutečných cest potvrdila jejich nepřítomnost u01_00–01_07,
02_00–02_07 a03_00. Ostatní požadované MP3, JSON, SRT a VTT těchto scén existují.
Bez opravy se tvorba produkčního ZIP zastaví na FileNotFoundError. Word
boundaries jsou už v běžném audio JSON, proto lze duplicitní raw metadata
doplnit offline, případně je v balení učinit výslovně volitelnými. Nová
syntéza ani hlasový vzorek nejsou potřeba.

**D2 · Vysoká · Originální trace obsahuje osobní dočasnou cestu.**
Read-only kontrola existujícího skutečného výukového `trace.zip` z natáčecí
workspace našla v `trace.trace`, řádek1, události context-options a poli
`options.recordVideo.dir` cestu do osobní dočasné složky Windows.
Zkontrolované HTML/XML nemají tento uživatelský prefix, ale balicí funkce
binární ZIP nyní nekontroluje ani nerediguje. Nové přibalení původního trace
by proto distribuovalo toto soukromé metadata. Vytvořit přiznanou distribuční
kopii s redakcí nepotřebné dočasné cesty, uchovat oddělený originál a zaznamenat
oba digests i provedenou redakci. Otevřitelnost distribuční kopie ověřit
v povoleném následném walkthrough; tento reviewer během natáčení Trace Viewer
neotevíral.

Tyto dva nálezy byly předány autorovi. Další posouzení kompletních archivů,
časové osy a skutečného finálního MP4 následuje až po dokončení produkce;
dosavadní zdrojové opravy nejsou vydávány za úspěšné finální předání.

## Retest D1/D2 a obsahových úprav dne 10. 11. 2026

**D1 uzavřen zdrojově:** raw `.boundaries.json` je při balení nyní volitelný.
Povinný běžný audio JSON už obsahuje všechny skutečné word boundaries,
proto chybějící duplicitní soubor17 starších cache scén nezablokuje ZIP.

**D2 uzavřen pro offline redakci:** nová funkce payload byla nezávisle spuštěna
na bajtech skutečného existujícího trace, s virtuální evidence cestou a pouze
s výstupem v paměti. Žádný soubor artefaktu nebyl přepsán. Výsledek:

- Změnil se pouze člen `trace.trace`, přesně deklarovanou náhradou osobního
  prefixu; žádné jiné členy ZIP ani jejich obsah se nezměnily.
- Všech19 načtených JSON řádků trace/network zůstalo validních a CRC ZIP prošlo.
- `options.recordVideo.dir` má genericky anonymizovanou hodnotu.
- Původní skutečný trace má před i po kontrole shodný SHA-256.
- Release manifest podle zdroje ukládá zvlášť původní i distribuovaný digest
  a přiznanou redakci. Otevření distribuční kopie v Trace Vieweru zůstává
  naplánované na následný walkthrough mimo aktivní natáčení.

### Nový konkrétní český výklad

Všech **33 ručně upřesněných odstavců** odpovídá aktuálnímu97scénovému plánu;
původní obecná fráze z plánu zmizela. Soubor narration_refinements.json je
v distribučním allowlistu a build_course jej při opětovném sestavení načítá,
takže opravy nezávisí jen na jednorázové ruční změně plánu.

Při kontrole15 existujících receiptů se stavem recorded nebyl nalezen žádný,
jehož uložený komentář by se lišil od současného odstavce. Starší neodpovídající
záznam se tedy v tomto snímku nevydával za aktuální. Historický audit97 audií
a délky92,33 minuty se vztahoval k předchozí verzi; po těchto33 textových
úpravách potřebují nová audio a výsledná časová osa vlastní finální ověření.

Konkrétní Codegen a diagnostické odstavce nově věcně odpovídají předváděným
souborům a krokům. Zůstaly následující obsahové nesoulady předané autorovi:

- **06_03:** plán provádí browser/api_error a zobrazuje řízenou503, ale odstavec
  rozebírá vytvoření požadavku, prioritu a reload. Výklad má vysvětlovat
  viditelnou API chybu, nebo musí být změněn plán záběru.
- **12_03:** plán provádí browser/empty, zatímco odstavec už probírá firemní
  oprávnění a tests_external. Nejprve je potřeba vysvětlit skutečně zobrazený
  prázdný výsledek, případně přesunout záběr ke konfiguraci.
- **10_01:** formulaci „správný hledaný nadpis ani po delší době nevznikne“
  zpřesnit na chybně očekávaný či neexistující nadpis. Správné Přihlášení
  aplikace podle zadání právě zobrazuje.

Reviewer neovládal GUI, nepouštěl browser, natáčení ani TTS a nevytvářel další
hlasový vzorek. Úpravy textu ani tyto offline kontroly nepředstavují finální
schválení celého audiovizuálního kurzu.

### Následné zdrojové opravy tří odstavců

Autor provedl obsahové opravy06_03,12_03 a10_01 v refinements: výklad nyní
popisuje skutečnou503 a alert, skutečný prázdný výsledek se dvěma očekáváními
a chybně očekávaný nadpis. Tyto tři scény v okamžiku opravy ještě nebyly
natočené; jejich komentář se obnovoval samostatně. Nálezy jsou tedy zdrojově
vyřešené, finální obrazové a zvukové důkazy zůstávají k následnému auditu.

Autor dále oznámil úspěšný audit všech97 aktualizovaných MP3/SRT/VTT:
5818,85 s,966 cues a úplné dekódování audia. Tento krátký dokumentační krok
audit neopakoval. Finální video se nadále připravuje; lidský poslech ani
finální akceptace se tím netvrdí.

## Nezávislý průchod před finálním renderem

Tento průchod je **AI revize** existujících souborů a extrahovaných snímků.
Nespouštěl browser, GUI, testy ani natáčení a nezasahoval do foregroundu.
Nenahrazuje lidský poslech ani skutečný začátečnický test. Čtyři právě
přetáčené scény10_02,10_05,12_00,12_01 byly z kontroly aktuálních MP4 hashů
výslovně vynechány, aby rozpracovaný soubor nebyl zaměněn za chybu integrity.

### Skutečně načtené závěrečné důkazy

- `evidence/release-final/junit.xml`: **44 testcase, 0 failures, 0 errors,
  0 skipped**. Stejné součty má nezávisle načtený `release-reverse/junit.xml`.
  Reviewer tyto běhy znovu neprováděl.
- Všech **78 zmrazených souborů** má stále původní SHA-256.
- U **93 stabilních klipů** mimo výše uvedené retakes byl skutečně přepočten
  SHA-256 MP4 a porovnán s receiptem; zkontrolována byla také shoda současného
  komentáře a odkazovaných JUnit digestů. Nebyl nalezen nesoulad.
- Aktuální načtený speech-validation souhrn uvádí passed, Vlastu,97 scén,
  **969 cues a5831,69 s**, s výslovným `human_listening_review=not_claimed`.
  Úplné dekódování tohoto audia bylo důkazem autora, nikoliv novým poslechem
  nebo opakovaným dekódováním v tomto průchodu.

### Opravy produkčních nástrojů

Reviewer odhalil, že původní close_stale_tool_windows zavíral obecně
pojmenovaný Inspector/Trace Viewer bez ověření původu. Autor jej nahradil
neinvazivním seznamem tool_windows. Aktuální zdroj byl ověřen: trace/debug
si zapamatují existující handly a čekají na nový handle s jejich vyloučením.
Neznámá již otevřená okna nezavírají. Tento nález je zdrojově uzavřen.

Trace ukázka nově vybírá skutečný řádek neúspěšného očekávání a při nejasném
výběru skončí chybou. Debug ukázka vypíná tracing/screenshot/video pouze pro
interaktivní demonstrační běh, aby Inspector nezůstal na úklidu diagnostiky;
důkazy řízeného selhání jsou samostatné. Inicializace Studio nyní provádí
View: Reset Zoom a View: Close Panel. Zděděný REPL či nesprávný zoom tak
nemají přejít do další samostatné editorové scény. Nové zvětšení Inspectoru
a poslední retakes musí ještě potvrdit jejich vlastní hotové snímky.

### Omezená nezávislá vizuální kontrola

Z již existujících extrahovaných snímků byly prohlédnuty:

- **10_02/1:** Trace Viewer má vybrané neúspěšné Expect, zobrazuje lokátor
  s Neexistující nadpis a skutečný snapshot přihlašovacího formuláře.
- **09_02/1:** editor zobrazuje skutečný čitelný draft Codegenu s navigací,
  zaznamenanými akcemi a syntetickými přihlašovacími údaji.
- **11_01/1:** skutečný HTML report ukazuje27 passed, použitý Python3.12.15
  a jednotlivé případy vybrané regrese. Jde o jiný rozsah než souhrn44 případů
  v závěrečném ověřování, nikoliv o rozpor ve výsledcích.

V těchto snímcích nebyla nalezena osobní uživatelská cesta. Rozsah kontroly
je pouze uvedený výběr, ne úplné přehrání všech scén či schválení budoucí
finální kompozice.

### Distribuce a zbývající gate

Aktuální allowlist již obsahuje skutečný Codegen export, archivované důkazy,
refinements, oba finální testovací reporty a požadované podklady. Read-only
kontrola nenašla chybějící zdrojový vstup. Sedm zatím chybějících souborů
patří výhradně dosud nevytvořenému finálnímu renderu, titulkům, časové ose
a audio alignment; v této fázi je jejich absence očekávaná.

Balení nově vyžaduje také passed audio alignment všech97 scén svázaný se
SHA-256 výsledného videa. Finální MP4, všechny poslední retakes, jejich
integritní receipty a oba skutečné ZIP archivy ale dosud nebyly předloženy
k závěrečné nezávislé kontrole. **Finální předání se tímto průchodem neuzavírá.**

## Přijetí všech zdrojových klipů před sestavením MP4

Po dokončení posledních retakes reviewer read-only přepočítal SHA-256
**všech97 aktuálních MP4**. Všechny souhlasí se svým receiptem a mají stav
recorded i ověřenou integritu; souhrn recording-integrity uvádí97 z97.
Nezávisle přepočtené digests posledních dvou scén jsou:

- 12_00: `cefd1e06ea5d19b98265ca03707536e6013e25d5d2039ca1e1da8d481dd929ce`
- 12_01: `b7cf2763a9dcb2889a98bcdd1f854972b113ceb268c3a3d89dbedb3dd697e754`

Aktuální recorder zapíše recording_in_progress před změnou klipu.
Verifikátor si uloží původní bajty receiptu a před nahrazením ověří, že se
nezměnily; pozdější přetočení nebo zamítnutí tak nemá být přepsané starým
výsledkem ověřování. Reviewer tuto kontrolu přečetl ve zdroji. Rozhodujícím
důkazem nynějšího stabilního stavu je následné skutečné porovnání všech97 hashů,
provedené po dokončení nahrávání.

Ve zdroji bylo dále potvrzeno cílené přesunutí předaného řízeného okna na
primární monitor a zavření editorového panelu přes skutečné UIA Close Panel,
místo spoléhání na dříve zapamatovaný stav panelu.

### Poslední nezávislá obrazová kontrola zdrojů

Reviewer prohlédl nativní extrahované snímky12_00/1 a12_01/1: obsahují čistý
čitelný pracovní sešit s úkolem, bez zděděného REPL či nesprávně zvětšeného
editoru. Snímek10_05/1 ukazuje čitelný uživatelský kód testu v Inspectoru,
pozastavený na očekávání, nikoliv na úklidu diagnostických artefaktů.
Kontaktní přehledy kapitol10 a12 odpovídají těmto opraveným podobám.

Soubor visual-review nyní pokrývá všech12 kapitol. Reviewer zkontroloval
existenci a SHA-256 všech v něm deklarovaných obrázků: bez nesouladu.
Výslovně zůstává označený jako sampled_visual_review, nikoliv celé souvislé
přehrání nebo lidský poslech. Nezávislé oči tohoto průchodu se omezily na
výše konkrétně uvedené nativní snímky a dva kontaktní přehledy.

### Distribučně redigovaný trace

Byly přepočteny a potvrzeny oba digests z
sanitized-trace-viewer-validation: skutečného redigovaného ZIP i zachyceného
PNG. Reviewer tento PNG prohlédl; ukazuje otevřený Trace Viewer, vybrané
neúspěšné očekávání a správný snapshot přihlašovacího formuláře.
Spolu s dřívějším offline retestem struktury redigovaného ZIP to doplňuje
důkaz jeho praktické otevřitelnosti. Samotné otevření provedl autor, nikoliv
reviewer během tohoto read-only průchodu.

Nebylo zjištěno nové blokující poškození aktuálních zdrojových klipů.
**Finální kompozice MP4 a skutečné distribuční ZIP archivy stále čekají na
samostatný audit.** Tento výsledek je AI revize; lidský poslech se netvrdí.

## Nezávislá diagnostika a oprava MP4 kapitol

První skutečný celovečerní render nebyl přijat: úplná kontrola správně
zastavila validaci na chybě `Referenced QT chapter track not found`.
Reviewer read-only rozebral samotné MP4 boxy. Původní moov měl pouze video,
audio a českou titulkovou stopu s track IDs1–3; všechny obsahovaly neplatný
tref/chap odkaz na track0, který neexistoval. Nešlo tedy jen o neškodný text
v logu. Nero metadata kapitol přitom zůstala přítomná.

Význam vazby potvrzuje oficiální zdroj
[muxeru FFmpeg](https://github.com/FFmpeg/FFmpeg/blob/master/libavformat/movenc.c):
QuickTime kapitoly používají další textovou stopu a odkazy z ostatních stop.
[Demuxer FFmpeg](https://github.com/FFmpeg/FFmpeg/blob/master/libavformat/mov.c)
hlásí nalezenou chybu, pokud se odkazovanou stopu nepodaří dohledat.

Autor zkusil remux stejným FFmpeg9 bez časového omezení, ale poškozenou vazbu
to neopravilo. Následný stream-copy remux stabilním FFmpeg7.1 z připnutého
imageio-ffmpeg0.6.0 vytvořil platnou strukturu. Reviewer žádný movie soubor
neměnil a neprovedl navržený alternativní Nero-only experiment.

### Skutečný nezávislý retest opraveného targetu

- MP4 nyní obsahuje skutečnou textovou chapter stopu **track4 se12 samples**;
  odkazy všech původních stop míří správně na4, nikoliv na0.
- Z jejích sample tables byly přímo přečteny názvy a začátky kapitol.
  Všech **12 českých názvů i časů** odpovídá timeline s tolerancí1 ms,
  časový konec chapter stopy je5831,59 s.
- Reviewer podle stsc/stsz/stco samostatně zahashoval skutečné sample payloady
  původního i opraveného souboru. Výsledky všech tří přenesených streamů
  jsou bitově totožné:

| Stream | Samples | Bajty sample payloadu | SHA-256 před i po opravě |
|---|---:|---:|---|
| H.264 / avc1 | 145790 | 94349377 | `9ed65b4ca93befcff8103fb7b5b3a43f00e6a8550405ad541dac97706786ac68` |
| AAC / mp4a | 273346 | 107312971 | `7211909f76c8d27389340279df1ab3a5f860f086a9531a59644f888ceee0ea23` |
| České titulky / tx3g | 1597 | 81328 | `041e57224bd8f85dabce05fdb97522009417f161d3243e0ebb5dc9a52ad0c3c3` |

Tento výsledek dokládá opravu chapter struktury bez opětovného zakódování
nebo změny původních obrazových, zvukových a titulkových paketů. Nemá být
zaměněn za poslechové hodnocení. Úplný decode opraveného souboru, finální
audio alignment, vazby výsledných podkladů a distribuční ZIPy nadále musí
projít závěrečnou validací; chyba nebyla potlačena ignorováním logu.

## Obrazové vady odhalené až v prvním celém sestřihu

První sestřih zůstává pre-final. Nezávislé prohlédnutí skutečných rámců
začátků kapitol01 a05 potvrdilo ghost během animace okna: více poloprůhledných
kopií browseru překrývá editor. Nejde o zamýšlený fade názvu kapitoly.
Prázdný editor na začátku kapitoly04 je naopak správný začátek psaní testu
a barevné zvýraznění v kapitole09 patří skutečnému Codegenu.

Aby se neopravily jen začátky kapitol a nevynechaly stejné přechody uvnitř
kurzu, reviewer read-only vytáhl rámce1,5 s z pěti dalších existujících
browser klipů přímo do paměti. **Stejná vada je také ve02_04,05_03 a06_03.**
V11_01 a12_03 je obraz stabilní, jen ještě před následující akcí.
Ověřené začátky06_00 a08_00 jsou rovněž bez ghostu.

Na následnou žádost byly stejně zkontrolovány09_00 a09_01 ve2,5 s,
tedy po začátku jejich callbacku. Oba mají stabilní skutečný Codegen bez
tohoto zdvojení; nebyl důvod požadovat opakování jejich atomické skupiny.

Celkový potvrzený rozsah obrazové opravy je **01_00,02_04,05_00,05_03,06_03**.
Autor je přetáčí se současnou opravou focus, poté musí znovu ověřit integritu,
sestavit výsledné MP4 a obnovit jeho návazné důkazy. Dřívější úspěšné hashe,
decode ani audio alignment nesmějí zakrýt tento obrazový nález. Reviewer
během této kontroly neovládal GUI, nevytvářel nové nahrávky ani neměnil
žádný mediální soubor. Finální přijetí videa zůstává otevřené.

## Následná kontrola pěti přetočených scén: zachycené soukromé IDE

**Severity HIGH, opraveno následným retestem níže:** předchozí `01_00.mp4` se SHA-256
`18df514ea2e131d6aebe674efee53a565f1ec7e7e7fc7a7a3a1c11f67a813506`
obsahuje místo požadovaného Dashboardu soukromé uživatelské VS Code
s Codex chatem a panelem source control. Reviewer samostatně prohlédl
všech 15 aktuálních archivovaných snímků pěti retaků. U `01_00/0.png`
je správný Dashboard, ale `01_00/1.png` a `01_00/2.png` zachycují toto IDE.
Při délce klipu 97,92 s jde o vzorky v 48,96 a 88,128 s. Čistý začátek
tedy nedokládá čistotu zbytku klipu. Tento konkrétní klip nesmí být vydán;
je nutné jej přetočit a zopakovat kontrolu skutečného obrazu.

| Scéna | Výsledek všech tří snímků v 10 %, 50 % a 90 % |
|---|---|
| `01_00` | První Dashboard správně; druhý a třetí soukromé IDE s chatem — FAIL |
| `02_04` | Čistý Dashboard se třemi záznamy, bez ghostu a cizího IDE |
| `05_00` | Čistý Dashboard se třemi záznamy, bez ghostu a cizího IDE |
| `05_03` | Čisté vyhledávání Export s jedním odpovídajícím záznamem |
| `06_03` | Čistá řízená chyba API 503, viditelný alert a prázdný výsledek |

Reviewer navíc nezávisle zahashoval všech pět aktuálních MP4: hodnoty
odpovídají receiptům. Všech 15 hashů archivovaných PNG odpovídá příslušným
záznamům integrity. To svazuje vizuální nález se skutečně přijatým klipem,
ale zároveň ukazuje hranici technické integrity: `verified` potvrzuje
dekódování a neměnnost, nikoliv správnost zachyceného okna. U ostatních
čtyř scén jde o PASS těchto tří obrazových vzorků, nikoliv o tvrzení
nepřetržitého vizuálního přehrání. Kontrolu provedl druhý AI reviewer
bez GUI, bez natáčení a bez lidského poslechu; upravil pouze tento dokument.

### Zdrojová kontrola následné ochrany natáčecího okna

Nový `recording_surface` mění TOPMOST pouze předanému řízenému hwnd
a v `finally` obnovuje původní příznak; neznámá okna nezavírá. Kontext
obklopuje spuštění i ukončení FFmpeg. `capture_events` při zjištění cizího
popředí vyvolá chybu, v `finally` ukončí a počká na capture proces a zavře
log. Výjimka zabrání zápisu receiptu `recorded`, takže zůstane předem
uložený stav `recording_in_progress`. Uvolnění TOPMOST následuje až po
této obsluze procesu.

Reviewer read-only vyňal AST obou funkcí a v paměti je spustil s fake Win32
a fake procesem, bez importu GUI modulů. PASS: obnova běžného okna po
úspěchu, po chybě těla i po neplatném popředí; zachování původního TOPMOST;
odmítnutí cizího popředí spojené s ukončením procesu a zavřením logu.
Jde o test řídicího toku s náhradami, nikoliv o praktický Windows test.

Přesná mez ochrany: 0,15 s je prodleva mezi průchody smyčky, nikoliv
garantovaný interval monitorování. Během synchronního event callbacku
a volání `focus` se foreground samostatně neověřuje. Tato zdrojová oprava
proto sama neuzavírá vizuální nález `01_00`; nový dokončený klip a jeho
aktuální snímky nadále vyžadují samostatné ověření.

### Nezávislý retest chráněného `01_00`: PASS obrazových vzorků

Reviewer z aktuálního souboru samostatně spočítal SHA-256
`d8e08cfe39489c611d3284443d77731602326cfa6286d5dd5e6953e9bb64fd90`;
souhlasí s novým receiptem `recorded`, délkou 97,92 s a integrity záznamem.
První dva aktuální archivované snímky zobrazují čistý Dashboard se třemi
syntetickými požadavky. Třetí snímek nástroj při opakovaném zobrazení
prezentoval černě, proto reviewer ověřil přímo soubor: jeho PNG bajty
i všechny RGB pixely jsou přesně totožné s druhým, správným snímkem.
Průměr RGB je přibližně 196/198/203 a směrodatná odchylka 97/94/90;
skutečný soubor není černý.

Pro vyloučení pouhého spoléhání na receipt reviewer z nového MP4 sám
read-only extrahoval rámce v 9,792 s, 48,96 s a 88,128 s přímo do paměti.
Každý má přesně stejné RGB pixely jako příslušný archivovaný snímek.
SHA MP4 před extrakcí i po ní je stejný. **Nález zachyceného soukromého
IDE je pro tuto konkrétní novou verzi opravený**; v ověřených vzorcích
není cizí IDE ani původní ghost. Rozsah tohoto PASS zůstává tři obrazové
vzorky, nikoliv nepřetržitý vizuální přehrávací audit nebo lidský poslech.
Celý výsledný film a distribuční balíčky ještě čekají na závěrečné ověření.

## Závěrečná AI kontrola uzavřeného filmu po opravách

Posuzovaný finální soubor má SHA-256
`71bf3706f1c3eb8c173395872a10010ead26ccbdbf8f632a6ddd780dfe1e269f`,
200 010 049 bajtů a podle aktuální validace délku 5831,61 s. Následující
výsledky se vztahují výhradně k této verzi, nikoliv k dřívějším sestřihům.

- **PASS, vlastní nezávislé čtení MP4 atomů a sample tables:** existuje
  skutečná textová chapter stopa 4 s 12 samples. Všechny ostatní tři stopy
  na ni odkazují přes `tref/chap=[4]`. Všech 12 českých názvů a začátků
  přesně odpovídá aktuální timeline; rozdíl je ve všech případech 0 ms.
  Chapter stopa končí v 5831,59 s. Původní poškozený odkaz na track 0
  není v tomto souboru přítomný.
- **PASS, vlastní hash kontrola:** všech 78 zmrazených souborů odpovídá
  manifestu. Všech 97 klipů i jejich audio odpovídá hashům v timeline
  a receiptech; identity odpovídají kanonickým screen deklaracím a audio
  signaturám, komentář odpovídá aktuálním odstavcům. Všechny receipty jsou
  `recorded` s ověřenou integritou, časová návaznost scén je souvislá.
  Intro odkazuje na opravený chráněný klip `d8e08cfe…64fd90`.
- **PASS, kontrola aktuální evidence:** validation odkazuje na skutečný
  SHA filmu a všechny její linked assets mají správný hash. Deklarovaný
  úplný decode skončil 0 a skutečný `decode.log` má 0 bajtů. Reviewer
  tento dlouhý decode znovu nespouštěl. Aktuální audio alignment je svázán
  se stejným SHA, má PASS všech 97 scén a největší absolutní odchylku
  21,312 ms. Embedded titulky mají 969 cues, původní text shodný a nulový
  maximální časový rozdíl. Jde o automatickou technickou evidenci, nikoliv
  o poslechové hodnocení reviewera.
- **PASS, vlastní kontrola finálních snímků:** nový manifest obsahuje
  21 snímků a správný SHA filmu; všechny PNG hashe souhlasí. Reviewer
  navíc z tohoto MP4 znovu extrahoval všech 21 časových bodů do paměti
  a porovnal přesné RGB pixely: žádný rozdíl proti archivovaným PNG.
  Film zůstal během této kontroly hashově nezměněný.

Reviewer vizuálně prošel kontaktní list všech 21 aktuálních rámců a navíc
nativní snímky kapitol 01, 02, 05, 07 a 12, začátků scén 02_04, 05_03,
06_03, 10_02, 10_05 a konce. Původní ghost v pěti přetáčených scénách
v aktuálních vzorcích není. Vlastní dodatečná extrakce finálního filmu
v 88,128 s ukazuje čistý Dashboard, nikoliv soukromý chat. Trace ukazuje
skutečné chybné očekávání nadpisu, debugger čitelný uživatelský kód
a konec správný samostatný test prázdného výsledku. U časných browser
snímků je někdy ještě stav před dokončením navazující akce; nebyl
zaměněn za její konečný výsledek. Původní tři pozdější snímky těchto
klipů byly ověřeny v předchozím retestu.

Nová ochrana je aktivní pro intro. Současný zdroj explicitně vyjímá pouze
terminálovou akci `journey`, kde je přechod do Chromium součástí skutečné
headed ukázky. Výše popsaná mez synchronních callbacků nadále platí.
Žádná nová blokující chyba nebyla v tomto vymezeném auditu filmu nalezena.
Distribuční ZIPy dosud nebyly předloženy k závěrečné kontrole. Toto je
nezávislá revize druhým AI reviewerem, nikoliv lidský poslech, začátečnické
UAT nebo nepřetržitá vizuální kontrola celého filmu; finální přijetí
celého produktu proto zatím neuzavírá.

## Nezávislý audit distribučních ZIPů

Druhý AI reviewer samostatně přečetl skutečné archivy ve složce distribuce;
nepřebíral pouze výsledek `audit_release`. **V kontrolovaném obsahu nebyla
nalezena blokující chyba technické distribuce.**

| Kontrola | Nezávisle ověřený výsledek |
|---|---|
| CRC obou archivů | PASS; také CRC vnořeného trace ZIPu |
| Úplnost manifestů a hashe obsahu | PASS; Starter 332 payload souborů, Production 976; každý archiv navíc obsahuje vlastní manifest |
| Kontrolní součty distribuce | Všech 8 položek `SHA256SUMS.txt` odpovídá skutečným souborům |
| Zmrazené soubory | Všech 78 položek v ZIPu je skutečně byte-for-byte totožných se zmrazenými pracovními soubory |
| Společné rozbalení | Tři sdílené soubory jsou totožné, žádný konflikt; manifesty mají odlišná jména |
| Produkční média | Všech 97 MP4 odpovídá timeline SHA; přítomných je 97 souborů Vlasta MP3 a povinné JSON/SRT/VTT pro každou scénu |
| Finální obrazové důkazy | Přiloženo všech 21 rámců, jejich hashe odpovídají manifestu svázanému s finálním filmem |
| Přenositelný concat playlist | Všech 97 relativních cílů existuje v produkčním archivu |
| Nepovolené pracovní soubory | Nenalezeny `.env`, `.venv`, `.tools`, `.git` ani cache adresáře |

Reviewer provedl kontrolu osobního Windows user-directory prefixu ve všech
UTF-8 čitelných distribuovaných souborech včetně textových položek uvnitř
trace ZIPu. Nebyl nalezen osobní prefix mimo přiznanou tréninkovou náhradu.
U skutečného distribuovaného trace samostatně ověřil original SHA proti
pracovnímu originálu i distribuovaný SHA proti manifestu. Z 18 vnitřních
položek se změnila pouze `trace.trace`, přesně nahrazením osobní části cesty;
ostatních 17 položek zůstalo byte-for-byte stejných. JSON řádky trace
i network zůstávají parsovatelné. Praktické otevření tohoto redigovaného
trace bylo dříve doloženo autorem a samostatně zkontrolovanou evidencí,
nikoliv novým GUI během tohoto ZIP auditu.

Odmítnutý klip s uživatelským chatem není přítomen podle svého známého
SHA; odmítnutý soukromý screenshot není přítomen podle názvu ani obsahu.
Soukromá pracovní evidence není součástí allowlistu. Reviewer navíc znovu
vizuálně prohlédl všechny tři kontaktní listy první kapitoly a ověřil,
že distribuované JPEG mají stejné bajty jako tyto prohlédnuté soubory:
obsahují čistý Dashboard a správné výukové IDE, nikoliv soukromý chat.
To není tvrzení automatického rozpoznání všech možných osobních údajů
ve všech obrazových a zvukových vzorcích.

Po tomto zápisu autor ještě přebalí aktualizovanou dokumentaci a obnoví
manifesty a kontrolní součty; ty musí znovu projít běžným distribučním
auditem. Hash ZIPů zde záměrně není uveden, protože ZIP sám obsahuje tento
review dokument. Technické PASS výše nenahrazuje lidský poslech,
pedagogickou akceptaci začátečníkem ani instalaci na čistém Windows.
