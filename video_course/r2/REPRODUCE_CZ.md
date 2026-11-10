# Referenční kapitola R2 — přehrání a reprodukce

Stav: čeká na úplné zhlédnutí, poslech a schválení vlastníkem kurzu. Původní celý kurz má verdikt CHANGES_REQUIRED. Technické kontroly tohoto balíku nejsou produktové schválení. Další kapitoly se před schválením reference nevyrábějí.

## Přehrání

V kořeni balíku jsou dvě kompletní MP4, společné SRT i VTT a přehrávač. Na Windows spusťte `PREHRAT.cmd` (vyžaduje nainstalovaný Python 3). Otevře pouze lokální HTTP server na 127.0.0.1 a prohlížeč; konzoli zavřete pomocí Ctrl+C. Přehrávač má tlačítko českých titulků a přesun na začátek, střed a závěr. `player.html` neotevírejte přímo jako file URL: prohlížeče mohou blokovat VTT.

`Playwright_Academy_R2_Prvni_Test_Titulky.mp4` obsahuje české titulky přímo v obraze. Tuto variantu lze otevřít samostatně v přehrávači podporujícím H.264/AAC. U základní MP4 je také embedded mov_text; jeho přítomnost není zárukou zobrazení ve všech přehrávačích. Dodaný HTML přehrávač používá skutečně otestovaný externí WebVTT. Konkrétní verze Microsoft Edge, časy, texty a snímky zapnutých/vypnutých titulků jsou v `sources/video_course/r2/evidence/player/`.

## Ověření Starter Kitu

`sources` je samostatný zdrojový projekt. Přesný commit a SHA-256 každého ze 78 zmrazených souborů obsahuje `sources/video_course/r2/reference.json`; odpovídající Git historie je v `starter-reference.bundle`. Není třeba přístup k původnímu repozitáři. Případný klon bundle proveďte do nového prázdného adresáře, ne přes adresář sources.

```powershell
git clone --branch r2-frozen .\sources\video_course\r2\starter-reference.bundle .\starter-snapshot
cd .\sources
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest tests training/solutions
```

Starter Kit sám spouští lokální demo přes fixtures. Jde o syntetická data; veřejný cvičný účet není skutečný firemní přístup. Postup a kapitoly manuálu jsou přiložené v training a docs. Výsledný soubor ukázky je `tests/examples/test_video_created.py`.

## Offline sestavení reference z dodaných záznamů

Uvnitř `sources`:

```powershell
py -3.12 -m venv .tools\media-env
.\.tools\media-env\Scripts\python.exe -m pip install imageio-ffmpeg==0.6.0
.\.tools\media-env\Scripts\python.exe video_course\r2\build.py
```

Tento krok nevolá hlasovou službu, neotevírá desktop a nepřepisuje Starter Kit. Potřebné audio, 27 původních klipů, konkrétní hlasové segmenty a metadata jsou přiloženy. Render ověří hashe plánu, audia a klipů a při nesouladu odmítne sestavení. Výsledek zapíše do `video_course/r2/output`. Časová osa a účel každého záběru jsou v `timeline.json` a `output/edit_project.json`; kamera, značky i titulky se generují skriptem build.py. Na Windows je referenční font Segoe UI; soubor fontu není redistribuován. Shodný obraz vyžaduje stejný font a FFmpeg; jiné prostředí může změnit kompresi nebo rasterizaci textu.

## Nové natáčení a hlas

Nový capture vyžaduje interaktivní Windows desktop 1920×1080 při 100% měřítku, VS Code v PATH a Playwright Chromium. `production/requirements-media.lock` obsahuje přesné verze produkčního prostředí. Nejprve nainstalujte Starter Kit a média do výše uvedených venv. Capture používá oddělenou pracovní kopii `C:\QA\PlaywrightAcademy`, která musí mít vlastní `.venv` s requirements.lock a nainstalovaný Chromium. Skripty tuto určenou kopii připravují z frozen manifestu; nezapisují do zmrazených souborů v sources.

`make_plan.py` vytvoří autorský režijní plán; `prepare.py` z něj syntetizuje celé odstavce hlasem **cs-CZ-VlastaNeural**, ukládá nativní časování slov a vytváří plán střihu. Je to síťová operace přes edge-tts, služba nemá garantovanou dostupnost. Pro offline render je nepotřebná. Fonetické aliasy upravují pouze řeč, titulky zachovávají původní odborné názvy; QA se vyslovuje „kjů ej“.

`capture.py --rehearsal` skutečně projde všechny činnosti; `capture.py` natočí referenci. Během záznamu neovládejte klávesnici ani myš. Při cizím okně v popředí záběr selže a nesmí být přijat. Vlastní okna jsou dočasně navrchu jen při capture a jejich původní stav se vrací. Žádný další celý kurz se tímto příkazem nevyrábí.

## Důkazy a omezení

Čerstvé JUnit, HTML reporty a originální pytest WEBM jsou pod evidence/take_…; v obou bězích jde o stejný nodeid. Z JUnit je odstraněn název stanice. Ukázka browseru je výslovně označené přehrání skutečného záznamu daného běhu. Případné držení posledního snímku je uvedené v receipts a nepovažuje se za novou činnost.

Automatický přehrávací test probíhá se ztlumeným zvukem a nenahrazuje poslechové hodnocení. Nezávislý review uvádí přesný rozsah skutečně provedené kontroly. Codegen, Inspector a Trace Viewer nejsou tématem této první kapitoly; jejich povinná ověřená ukázka zůstává podmínkou budoucího celého kurzu. Schválení reference samo o sobě neznamená splnění všech AC celého produktu.
