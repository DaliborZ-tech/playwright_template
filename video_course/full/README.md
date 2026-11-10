# Produkce celého kurzu podle schválené reference R2.1

Hlas: Microsoft Vlasta `cs-CZ-VlastaNeural`. Titulky používají kanonický text,
nikoli fonetické přepisy pro výslovnost. Schválení vlastníka reference je
v `../r21/po_approval.json`; není vydáváno za poslech celého nového filmu.

Starter Kit: 78 souborů, commit `129d317771d91da04e31e8150a2111188f9ae51f`.
Manifest je v `../r21/reference.json`, úplný Git bundle `../r21/starter-reference.bundle`,
větev `r2-frozen`. Pro výuku použijte přesně tuto verzi.

## Sestavení bez TTS a bez přístupu k síti

Ze složky kořene zdrojů spusťte Pythonem 3.12:

```powershell
python video_course/full/build.py --assemble
```

Potřebné mediální balíčky: `numpy`, `imageio-ffmpeg==0.6.0` (FFmpeg 7.1).
Instalujte do prostředí Pythonu nebo `.tools/media-env`. FFmpeg lze zadat také
proměnnou `IMAGEIO_FFMPEG_EXE`. Použité Windows fonty jsou Segoe UI a jeho
varianta Bold z Windows 11; editor a terminál používají systémový monospace
font VS Code (na této stanici Consolas). Fontové soubory se nepřibaluji. Nahrazení fontu,
verze FFmpeg nebo jiné platformy může změnit obraz i binární hash.

Přesné verze produkčních nástrojů použité na této stanici jsou
v `production_requirements.txt`; pro nové snímání je instalujte až po
závislostech Starter Kitu z `requirements.lock`. Sdílené původní R2/R2.1
pomocné moduly importují i Windows produkční knihovny, proto je nainstalujte
také pro offline sestavení. Samotné sestavení neotevírá GUI a nepoužívá TTS.
Při použití produkčního prostředí umístěného mimo zdroje zpracujte jeho
`site-packages` přes `site.addsitedir` (včetně `.pth` inicializace pywin32);
ověřovací `reproduce.py` tento krok provádí automaticky.

Build ověří hashe vstupů a každého skutečného raw záznamu. Vytvoří po kapitolách
režijní `output/edit_project.json`, kompozice v `rendered/`, globální SRT/VTT,
MP4 s přepínatelnými i s vypálenými titulky a kapitoly. Kapitolu 04 převezme
z přesně schváleného R2.1 MP4, původní zdroj nemění. Cache sestavených záběrů
lze znovu použít jen při shodě renderovacích vstupů.

Pro střih uvnitř schválené kapitoly 04 obsahuje hlavní distribuční balík také
`Reference_R21_Complete.zip`: nezměněnou původní úplnou referenční dodávku
včetně všech jejích raw, původních podkladů, timeline, zvuku a vlastního
ověřeného offline sestavení. Nic se nemusí dohledávat ani stahovat zvlášť.

`narration.wav` v každé kapitole obsahuje spojité odstavce po střihu změřeného
ticha. `timeline.json` uvádí nativní hranice slov, kanonický text, zdrojové MP3
a výslovné akční značky. Build zachová všechny původní hlasové PCM vzorky.
Pokud skutečná činnost vyžaduje více času, vloží čekání pouze do ověřeného
tichého švu a zapíše přesný počet vzorků. Dlouhé provádění testů může být
označeně zrychlené nebo čekání vystřižené; příkaz i výsledek zůstávají
v původní rychlosti. Přesné intervaly a rychlost uchovává editační projekt.

Pohyb kamery není počítán jako nová činnost. Čas, kdy je držen konečný ověřený
stav pro vysvětlení, se vykazuje zvlášť. Nevydává se za psaní ani interakci.

## Nové snímání na Windows

`capture.py` vyžaduje skutečnou viditelnou plochu Windows 11 1920×1080/100 %,
VS Code s Python extension, Playwright Chromium, PyAutoGUI, pywin32,
pywinauto, pyperclip, psutil 7.2.2 a připnuté prostředí Starter Kitu. Nahrává vlastní okna,
nikoli simulovaný editor. Záznam se odmítne při cizím okně v popředí.

Produkční pracovní kopie je `C:\QA\PlaywrightAcademy`; její zdroje se obnovují
z dodaného zmrazeného Starter Kitu. Lokální demo má syntetický účet
`tester@example.test` / `Academy123!`. Nepoužívejte vlastní soukromé údaje.

```powershell
python video_course/full/prepare.py
python video_course/full/director.py
python video_course/full/capture.py --resume
python video_course/full/build.py --assemble
python video_course/full/deliver.py
```

Přípravu ani režijní plán neměňte během rozběhnutého snímání. Každý take je
vázán na přesné hashe plánu, audia a souhlasu s referencí. Nedokončená kapitola
se natáčí od začátku, aby návazné kroky a čerstvé reporty patřily k sobě.
Soubor `stop.request` zastaví produkci na nejbližší hranici záběru.

Samostatné editorové dotáčky mají vlastní kontrakt, uchovanou původní receipt
a výslovnou návaznost na původní kontrakt kapitoly. Původní raw ani důkazy
se nepřepisují. `pickup.py` řeší dvě opravené volby HTML nadpisu kapitoly 01;
jejich samostatné snímání musí proběhnout při volné produkční ploše.

Reporty pod `chapters/*/evidence/` pocházejí ze skutečných běhů. Jejich runtime
cesty uvádějí původní pracovní kopii; přenosné kopie reportů a artefaktů jsou
uvnitř zdrojů a svázané hashi. Odebrání hostname z JUnit je výslovná úprava
metadat, nikoli výsledků testů.

## Přehrání a review

V kořeni distribuce spusťte `PREHRAT.cmd`, přepněte titulky a zvolte kapitolu.
Přehrávač používá lokální HTTP s podporou Range a UTF-8 VTT. Samostatné MP4
`_Titulky.mp4` má titulky přímo v obraze i bez podpory subtitle stopy.
Technické ověření není automatický souhlas s pedagogickou kvalitou.

Hotový kurz má 12 kapitol, 87 min 36,48 s a 1 153 globálních českých titulků.
Pro review skutečných činností se hodí zejména kapitola 04 (schválený první
test a RED→GREEN), 09 (Codegen a úprava jeho exportu), 10 (selhání, Trace Viewer
a Inspector), 11 (regrese a reporty) a 12 (samostatný test). Přesné začátky
a learning outcomes jsou v `output/chapters.json` a v přehrávači.

`ACCEPTANCE_FULL.md` mapuje jednotlivá AC na důkazy. Skutečný viditelný Edge
ověřil přepínané titulky na čtyřech místech včetně poslední věty, vypálenou
variantu a všech 12 tlačítek kapitol. Čerstvě rozbalený Starter Kit prošel
44 testy bez chyb a přeskočení. Výběrová obrazová AI kontrola není vydávána
za lidské zhlédnutí a poslech celého kurzu; ty zůstávají k review vlastníka.

Offline reprodukce rozbalí kompletní distribuční ZIP do nové cesty s mezerami
a sestaví celý kurz z raw a připraveného audia bez nového TTS či snímání.
`evidence/reproduction/validation.json` zaznamenává shodu obou celých MP4,
globálních SRT/VTT a kapitol byte po bytu. Ověření používá existující připnuté
Windows prostředí a stejné systémové fonty, nikoli čistou instalaci OS.
Závěrečné balení přidává důkazy a předávací dokumentaci; shodu všech 493
renderovacích vstupů zachycuje `evidence/reproduction/delivery_binding.json`.
