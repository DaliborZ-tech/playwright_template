# Produkce českého kurzu

Aktuální oprava je **R2.1**: hotová reference 5:48.48, měřený plynulý zoom,
vyvážené titulky a skutečný Codegen. Vlastník poslechem schválil 30s ukázku
rytmu a 10. 11. 2026 samostatně schválil celou referenci R2.1. Navazující
výroba je autorizovaná; doklad je v [r21/po_approval.json](r21/po_approval.json).
Zdrojový postup: [r21/REPRODUCE_CZ.md](r21/REPRODUCE_CZ.md).

**Platný mandát R2:** původní celý kurz má verdikt **CHANGES_REQUIRED**.
Nejdříve vzniká pouze referenční kapitola 5–8 minut; před další výrobou
je nutné její úplné zhlédnutí, poslech a výslovné schválení vlastníkem.
Nové zdroje, timeline a samostatný offline build jsou v [r2](r2/REPRODUCE_CZ.md).
Aktuální stav shrnuje [CONTINUE_HERE.md](../CONTINUE_HERE.md).
Níže zůstává dokumentace původní produkce; její starší pokyn o dalších
ukázkách nepřebíjí novou schvalovací bránu R2.

Kurz používá jeden hlas: **Microsoft Vlasta, `cs-CZ-VlastaNeural`, přes
edge-tts**. Vlastník po poslechu schválil fonetické úpravy a doplnil výslovnost
QA jako „kjů ej“. Další ukázky nepožadoval. Každý vysvětlující odstavec se
syntetizuje vcelku, aby zůstaly zachované návaznosti vět.

Slovník `production/pronunciation_vlasta.json` upravuje pouze řečový vstup.
Přepis, titulky a kód zachovávají správná slova Python, pytest, locator a QA.
Časy titulků pocházejí ze skutečných word boundaries služby. Mapování odmítne
neúplná metadata i ztrátu části původního textu.

Edge TTS je online služba, přestože se Python spouští na lokální stanici.
Při realizaci fungovalo generování bez účtu a API klíče. Kurz nepředpokládá
garantovanou dostupnost ani neomezenou kvótu komunitní integrace. Do služby
se odesílá pouze veřejný syntetický komentář. Hotový kurz a lokální demo
při přehrávání žádné TTS připojení nepotřebují.

## Co je zdroj a co je hotový výstup

- `scripts/transcript_cs.md`: úplný kanonický český komentář.
- `storyboard/course_plan.json`: 97 souvislých scén, 12 kapitol, konkrétní
  soubory a skutečné operace. Nejde o videoprezentaci ze screenshotů.
- `reference_manifest.json`: SHA-256 výukového kódu, dat, lekcí, instalátorů
  a zobrazovaných konfiguračních souborů.
- `narration/vlasta/`: MP3, původní a řečový text, word boundaries a lokální
  SRT/VTT každé scény. Historické hlasové pokusy nejsou produkční komentář.
- `recordings/`: skutečné nahrávky obrazovky s audionahrávkou a důkazy původu.
- `output/`: finální MP4, české SRT/VTT, přesné kapitoly, časová osa a validace.

Aktuální stav skutečné dodávky uvádí [akceptace](../docs/ACCEPTANCE.md).
Příprava skriptů nebo existence krátkého probe se za hotový kurz nevydává.

## Opakování produkce na Windows 11

Ukázka projektového interpreteru používá oficiální rozšíření `ms-python.python`
v odděleném adresáři rozšíření. Nainstalujte ho do produkčního profilu skutečného
VS Code; běžné osobní profily se do natáčení nepřebírají:

```powershell
& "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd" --user-data-dir .tools/studio-profile --extensions-dir .tools/studio-extensions --install-extension ms-python.python
```

Tento krok slouží jen k opakování nahrávky IDE; přehrání hotového kurzu ho
nepotřebuje. Pro výběrovou opravu existuje `record_course.py --scenes ID ID`.
Požadavek na zastavení lze zapsat do `evidence/stop-recording.request`;
nový recorder ukončí FFmpeg před zavřením vlastních oken a nepřijme dílčí scénu.
Další výslovné spuštění tento požadavek smaže a dovolí pokračovat.

Nejprve zprovozněte Starter Kit podle hlavního README. Produkce navíc potřebuje
interaktivní desktop 1920 × 1080, skutečný VS Code a mediální závislosti:

```powershell
.\.venv\Scripts\python.exe -m venv .tools\media-env
.\.tools\media-env\Scripts\python.exe -m pip install -r video_course/production/requirements-media.lock
.\.venv\Scripts\python.exe scripts/freeze_reference.py --check
```

Použijte samostatnou výukovou plochu bez osobních oken. Záznam skutečně snímá
viditelnou část obrazovky, proto během něj nepřepínejte foreground aplikaci.
Řízené natáčecí okno je po dobu scény dočasně držené vpředu. Při převzetí
popředí jiným oknem recorder ukončí FFmpeg, nepřijme dílčí scénu a obnoví
původní příznak topmost. Neznámá uživatelská okna nezavírá.
Výjimkou je terminálové spuštění celé cesty s `--headed`: musí smět otevřít
vlastní Chromium nad terminálem. Tato scéna proto vyžaduje nepřerušovanou
výukovou plochu a samostatnou kontrolu záběru.
Natáčecí kopie používá obecnou cestu `C:\QA\PlaywrightAcademy`. Její první
příprava nepřepíše existující složku:

```powershell
.\.venv\Scripts\python.exe video_course/production/prepare_workspace.py
& C:\QA\PlaywrightAcademy\scripts\setup_windows.cmd
```

Při opravě textu lze znovu sestavit storyboard z lekcí a tří souborů doplňkového
výkladu. Tento krok mění plán; nespouštějte ho souběžně s natáčením:

```powershell
.\.venv\Scripts\python.exe video_course/production/build_course.py
.\.tools\media-env\Scripts\python.exe video_course/production/continuous_speech.py
.\.venv\Scripts\python.exe video_course/production/audit_speech.py
.\.venv\Scripts\python.exe video_course/production/record_course.py --resume
.\.venv\Scripts\python.exe video_course/production/verify_recordings.py
.\.venv\Scripts\python.exe video_course/production/render_course.py
.\.venv\Scripts\python.exe video_course/production/audit_video_sync.py
.\.venv\Scripts\python.exe video_course/production/audit_final_frames.py
```

Cache hlasu se váže na původní text, fonetický vstup, hlas a rychlost. Titulky
se přepočítají i při použití existujícího audia. Natáčení při pokračování
kontroluje zdrojový manifest a podpis komentáře. Codegen se obnovuje celou
skupinou akcí, aby se neukázal nový prázdný Inspector místo skutečného záznamu.

Produkční nástroj odmítne demo s jiným build fingerprintem na portu 5000.
Cizí proces sám neukončuje. Terminálové scény ukládají skutečný návratový kód
a čerstvý JUnit. Výuková chyba musí být přesně očekávaný neúspěšný assertion,
se screenshotem a trace z téhož běhu. Osobní hostname v JUnit se před ukázkou
odstraní; počty a výsledky testů zůstávají beze změny a redakce je přiznaná.

Render vyžaduje všech 97 skutečných scén. Spojí je podle naměřených délek,
přidá krátké názvy kapitol, označení syntetického hlasu, sjednotí hlasitost
a vloží českou titulkovou stopu i metadata kapitol. Vedle MP4 zůstanou SRT/VTT.
Následně dekóduje celý obraz a zvuk a uloží SHA-256, parametry a výsledek.

Produkční lock používá `imageio-ffmpeg==0.6.0` s binárním FFmpeg 7.1.
Při kontrole novějšího balíčku se objevil neplatný QuickTime odkaz na kapitoly.
Produkční verze je proto připnutá na stabilní muxer. Historický opravný remux
zachoval identická zakódovaná data; finální střih s opravenými úvodními záběry
se celý vytváří přímo stabilní verzí. Existující střih lze bez rekódování znovu
ověřit volbou `render_course.py --validate-existing`.

Automatická technická kontrola nenahrazuje lidský poslech ani test výuky se
začátečníkem. Rozsah skutečné vizuální a poslechové kontroly musí zůstat výslovný
v akceptaci a nezávislém review.

## Oprava střihu z dodaných archivů

`Playwright_Academy_Starter_Kit.zip` obsahuje projekt, výuku, skripty a důkazy.
`Playwright_Academy_Production_Sources.zip` přidává původní nahrávky, jejich
receipty, komentář, časování a archivované snímky. Oba archivy rozbalte do stejné
složky; společný kořen se jmenuje `playwright-academy`. Každý má vlastní manifest.
Osobní části cest v distribučních kopiích diagnostických trace jsou nahrazené
obecnou cestou a manifest uvádí původní i distribuovaný hash. Zmrazený kód se
neupravuje.

Pro opakovaný střih existujícího materiálu stačí instalace závislostí výše,
`freeze_reference.py --check`, `verify_recordings.py`, `render_course.py`
a `audit_video_sync.py`. VS Code, nové natáčení ani spojení s TTS pro tento
postup nejsou potřeba. Nespouštějte sestavení storyboardu nebo novou syntézu,
pokud nechcete měnit komentář. Relativní playlist je přiložený pro další nástroje;
renderer si pro aktuální umístění vytvoří vlastní playlist.

Distribuci vytváří až po úplné validaci:

```powershell
.\.venv\Scripts\python.exe video_course/production/package_release.py --audit-only
.\.venv\Scripts\python.exe video_course/production/package_release.py
.\.venv\Scripts\python.exe video_course/production/audit_release.py --extract-to "evidence/release-check"
```
