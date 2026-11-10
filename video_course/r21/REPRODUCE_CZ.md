# Playwright Academy — reference R2.1

Kapitola má 5:48.48, hlas Microsoft Vlasta z Edge a dvě kompletní MP4.
Přepínatelné české titulky se přehrávají v dodaném HTML přehrávači přes
externí WebVTT; základní MP4 má navíc embedded mov_text. Druhá MP4 má
titulky přímo v obraze. Samostatné globální SRT i VTT jsou v kořeni balíku.

Na Windows spusťte `PREHRAT.cmd` (Python 3). Server běží jen na 127.0.0.1;
zastavení Ctrl+C. Přímé otevření player.html přes file URL nemusí načíst VTT.
MP4 s vypálenými titulky lze otevřít samostatně v přehrávači H.264/AAC.
Skutečné přepínání titulků a seek začátek/střed/konec se ověřují v Edge;
konkrétní verze, časové body a viditelné snímky jsou v evidence/player.

## Co je opraveno

- Sekundové pauzy se upravují podle významu, ne podle délky titulku.
  Původní řečové vzorky se nenatahují; vynechány jsou jen změřené tiché úseky.
- Tři vytčené scény jsou kratší a mají konkrétní významové popisky, přiblížení
  na vysvětlované prvky a návrat do kontextu. Pohyb kamery se nevydává za
  novou práci v aplikaci.
- Dvě 2,4s přiblížení jsou doložená měřením velikosti na skutečných snímcích,
  ukázkovými MP4 a snímky začátek/střed/konec v evidence/zoom.
- Titulky se dělí vyváženě; jednotlivá „examples.“ nebo „znovu spusťte.“
  nezůstávají jako krátké osamocené cues.
- Nový skutečný Codegen/Inspector ukazuje vznik návrhu; návrh byl i skutečně
  spuštěn. Důkazy ke zmrazené verzi a starým skutečným RED/GREEN jsou přiložené.

Konkrétní vazby důkazů uvádí `LIVE_EVIDENCE.md`. Původní verze R2 zůstává
zachovaná samostatně. Tato oprava nevyrábí znovu celý kurz.

## Poslechové srovnání

`comparison/before_30s.wav` a `after_30s.wav` začínají u stejné vysvětlované
části. Oba mají 30 s; po úpravě se do stejného času vejde více souvislého
výkladu. Nejde tedy o dvě přesně stejně dlouhé textové pasáže.
Vlastník poslechem schválil nový rytmus a nepřítomnost useknutých slov.
Přesný výrok a WAV hashe jsou v human_listening_review.json.
Následně 10. 11. 2026 vlastník odpověděl „schvaluji“ na celou referenci.
Doklad `po_approval.json` přijímá celý vizuální a zvukový standard R2.1.
Podrobnosti a přesné hashe jsou v APPROVAL_R21.md.

## Offline reprodukce filmu

Adresář `sources` je samostatný zdrojový projekt se Starter Kitem a produkcí.
Uvnitř něj na Windows:

```powershell
py -3.12 -m venv .tools\media-env
.\.tools\media-env\Scripts\python.exe -m pip install imageio-ffmpeg==0.6.0
.\.tools\media-env\Scripts\python.exe video_course\r21\build.py
```

Build pracuje pouze s přiloženým finálním PCM, ověřenými skutečnými klipy,
timeline a titulky. Nepotřebuje přístup k TTS ani desktop. Font Segoe UI není
redistribuován; jeho verzi/hashy a FFmpeg identifikuje FONT_REFERENCE.json.
Byte-identické sestavení vyžaduje stejné fonty a FFmpeg. Kamera, značky,
střih a titulky jsou reprodukovatelné skripty, nikoli pouze exporty scén.

Po novém renderu zaznamenejte již udělené schválení příkazem
`python video_course/r21/approval.py`. Skript ověří shodu s původně schválenými
filmy; změněné video nesmí převzít starý souhlas. `package.py` tento krok
provádí automaticky. Starší PENDING v plánu, měřeních nebo AI revizi je stav
před souhlasem; aktuální rozhodnutí je v po_approval.json.

Pro nové audio přečasování a přegenerování klipů jsou přiložené také původní
R2 audio, nativní word boundaries, raw capture i celá editační mapa. Tato
produkční fáze potřebuje Python prostředí projektu a závislosti z
`video_course/production/requirements-media.lock`. Postup:

```powershell
.\.venv\Scripts\python.exe video_course\r21\prepare.py
.\.venv\Scripts\python.exe video_course\r21\edit_clips.py
.\.venv\Scripts\python.exe video_course\r21\build.py
```

Nový záznam Codegenu navíc vyžaduje interaktivní Windows 1920×1080 při 100%,
VS Code/Chromium a určenou pracovní kopii C:\QA\PlaywrightAcademy s vlastní
instalací Starter Kitu. `capture_codegen.py` spouští skutečný Codegen CLI,
pracuje výhradně ve vlastních oknech a ukládá jeho skutečný Python výstup.
Během capture neovládejte desktop. Existující důkazy se při novém natáčení
musí uložit do samostatné revize; samotné přepsání klipů invaliduje hashe.

## Starter Kit

Commit a 78 hashů jsou v `reference.json`, Git historie ve starter-reference.bundle.
Manuál je v sources/training a sources/docs. Uvnitř sources:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest tests training/solutions
```

Úspěšný technický build, měření nebo AI revize nejsou celkovým produktovým
schválením. Výslovný PO souhlas s referenčním standardem byl udělen
10. 11. 2026 a navazující výroba je autorizovaná. Nový celý kurz vyžaduje
vlastní dokončení, kontrolu a akceptaci.
