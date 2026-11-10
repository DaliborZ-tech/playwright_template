# Nezávislá AI revize R2.1

Stav: **technická, zdrojová a výběrová obrazová revize dokončena; schválení celé kapitoly PENDING**.
V kontrolovaném rozsahu nebyla nalezena blokující vada. Poslední dva
cílené přehrávací případy dlouhých titulků byly opraveny a skutečně
vizuálně ověřeny; níže jsou uvedené aktuální finální movie hashe.

Reviewer je druhý AI reviewer. Neprováděl lidský poslech, nespouštěl GUI,
browsery ani headed testy a neměnil produkční zdroje. Četl skutečné soubory,
samostatně počítal hashe, rekonstruoval PCM v paměti, ověřil vazby capture
a měřil geometrické změny z existujících renderovaných MP4. Předchozí
podrobná kontrola původních 27 záběrů je v `../r2/REVIEW_R2.md`; zde se
posuzuje jejich doložená R2.1 úprava a tři nové záběry Codegenu.

## Konkrétní finální verze

Reviewer samostatně zahashoval uzavřené skutečné filmy:

| Varianta | Bajty | SHA-256 |
|---|---:|---|
| Základní MP4 | 31 588 498 | `6c53aeb9e0b0bc7828e115c2868399b6f2a54411835c92a8ab0893a882d42b20` |
| MP4 s vypálenými titulky | 31 610 879 | `c3ca84bdde17c1b5a9e038c8eb88b61c158fec027554d4b00c0aabcca7ea50f4` |

Oba odpovídají `output/edit_project.json`; délka je 348,48 s. Skutečné
úplné decode logy obou variant mají 0 bajtů; dlouhý decode reviewer znovu
nespouštěl. `quality_audit.json`, zoom evidence i player evidence odkazují
na stejný aktuální základní movie SHA. Kontrola se nevztahuje k dřívějšímu
prvnímu renderu.

## R2-F01: úprava pravidelných pauz a skutečný rozsah lidského poslechu

**PASS technické rekonstrukce.** Reviewer vzal původní R2 PCM, skutečných
64 řezů z `audio_edits.json`, původní PCM nového Codegen odstavce a jeho
osm řezů. Samostatným odstraněním uvedených vzorků a vložením odstavce
na uvedeném sample indexu zrekonstruoval celé nové WAV přesně byte-for-byte.
Parent i output SHA audia odpovídají manifestu. Nový Codegen úsek má po
úpravě 38,472479 s; původní a nové texty nebyly zkráceny vypouštěním slov.
Celková délka před finálním video-frame paddingem zůstává 348,456 s.

Maximální absolutní amplituda kteréhokoliv skutečně odstraněného vzorku
je 46 z 32768, přibližně −57 dBFS. To je výrazně pod deklarovanou detekční
hranicí −45 dB. Nebylo použito natahování hlasu ani změna jeho identity;
zůstává Microsoft Vlasta. Výstup lze odvodit přesně z doložených střihů,
nikoliv pouze z tvrzení „silence trimmed“.

Přesná mez tohoto důkazu: osm řezů protíná časové intervaly tokenů podle
nativních TTS metadat, které zahrnují i velmi tiché konce. Vlastní odstraněné
PCM vzorky jsou ověřeně pod výše uvedenou nízkou amplitudou. Reviewer proto
netvrdí, že každý metadata interval zůstal nedotčený, ani neodvozuje úplnou
subjektivní poslechovou kvalitu z prahové detekce ticha.

Medián mezer mezi caption cues byl samostatně přepočten: původně
1,0180415 s, nyní 0,37675 s. Je to podpůrné časové měření; samo nenahrazuje
poslech. Upravené audio má doložené skutečné uživatelské schválení
30sekundové ukázky v `comparison/human_listening_review.json`.
Reviewer ověřil oba skutečné hashe srovnávacích WAV proti tomuto záznamu:

- Před úpravou: `9b20f202c47cb71f2a679ce4053d09f09588f91f77ed43eda30d0b805b4690cd`.
- Po úpravě: `e3d016e919fd14c5951bf65e56962d73d6bcda66ceaa37415107bc46dc73ba0b`.

**Tento lidský souhlas platí pro uvedenou ukázku, nikoliv pro celý film.**
V metadatech je správně uvedeno `WHOLE_CHAPTER_PENDING` a owner/PO approval
zůstává pending. Žádný poslech provedený AI reviewerem se netvrdí.

## R2-F02 a R2-F05: retiming, skutečné záběry a zmrazený Starter Kit

**PASS vazeb konkrétních podkladů.** Všech 55 input hashů edit contractu
odpovídá skutečným souborům. Všech 30 child klipů má správný SHA,
správný parent MP4 SHA, shodný parent contract SHA a nezměněný skutečný
proof proti příslušnému parent receiptu. Rodiče tvoří 27 již ověřených
R2 capture a tři nové skutečné Codegen capture. Kontrolní body retimingu
jsou monotónní. Klipy nejsou označovány za nově natočené akce, když jde
o střih existujících čekání.

Aktivní část byla podle doložených control points mírně zrychlena pouze
u `05_red_run` na 1,066699× a `06_green_run` na 1,072212×. Ostatní skutečné
aktivní intervaly nemají toto zrychlení. Úpravy čekání a držení obrazu
jsou odlišeny od aktivního dění a nevytvářejí fiktivní UI stavy.

Všech 78 aktuálních zdrojových souborů odpovídá zmrazenému manifestu,
navázanému na commit `129d317771d91da04e31e8150a2111188f9ae51f`.
Předchozí RED/GREEN zdroj, jeho očekávaná jednobodová oprava, testcase
a příslušné HTML/JUnit/video důkazy zůstávají převzaté přes ověřené hashe.
Byly již konkrétně přezkoumány v R2 revizi; jejich časové přestřižení
nepředstírá nový testový běh.

U nového Codegenu reviewer ověřil uložené skutečné generované Python
soubory proti jejich capture SHA a prohlédl nativní raw
`evidence/frames/cg_open_1.png`, `cg_fill_1.png`, `cg_inspector_1.png`.
Je vidět skutečný browser a Inspector, následné vyplnění správného E-mail
textboxu a odpovídající vygenerovaný `get_by_role(...).fill(...)`.
Následný JUnit `evidence/codegen_execution/junit.xml` má skutečný
`reports.r21-codegen.draft::test_example[chromium]`, jeden provedený případ,
nula failures/errors/skipped. Reviewer jej znovu nespouštěl.
Generated draft zatím neobsahuje vlastní očekávání; přesně to komentář
vysvětluje a navazující ručně napsaný test je skutečně obsahuje. Úspěch
replay draftu se nevydává za úplné ověření přihlašování nebo kvality testu.

### Zbývající klidné výkladové úseky

`02_function` má nyní 23,08 s místo 26,24 s, `03_dom` 25,32 s místo
28,44 s a `04_heading` 19,56 s místo 22,20 s. Výklad nebyl odstraněn:
nové konkrétní popisky jsou navázané na argument page, dvojtečku,
h2/roli/název a locator/metodu očekávání. Plynulé přiblížení a návrat
vedou pozornost ke skutečnému obsahu, nejsou počítány jako nové UI akce.

Aktuální raw activity audit poctivě stále označuje 22,0 s nízké změny
v `03_dom` a 20,0 s v novém `cg_inspector`. První slouží vysvětlení
vybraného skutečného h2 a role/názvu místo CSS cesty. Druhý umožňuje
přečíst viditelný draft a vysvětlit, proč samotný záznam akcí vyžaduje
vlastní očekávání. Tyto úseky mají konkrétní výukový účel, ale přiměřenost
tempa musí posoudit owner při celém přehrání. Nejsou přeznačené na pohyb
na základě kamery, titulků či změny popisku.

## R2-F03: skutečný plynulý zoom a návrat

Source `motion.py` používá spojitou smoothstep křivku, ale tato revize
se neopírá pouze o vzorec. `evidence/zoom/zoom_validation.json` měří
skutečné šířky source-coordinate rámečku v renderovaných MP4 při 10 fps.
U `02_function` je zoom-in v 63,190–65,590 s, u `04_heading`
v 168,521–170,921 s: oba trvají 2,4 s, mají 24 různých měřených velikostí
a poměr koncové/počáteční velikosti přibližně 1,378 a 1,380.

Reviewer navíc samostatně nově extrahoval a změřil skutečné renderované
návraty do kontextu, nikoliv jen přijal jejich exportní metadata:

| Záběr | Celkový interval návratu | Měřená šířka | Počet různých detekovaných velikostí |
|---|---|---|---:|
| `02_function` | 78,96–81,36 s | 1312 → 953 px | 23 |
| `04_heading` | 180,48–182,88 s | 1312 → 953 px | 24 |

Oba návraty trvají 2,4 s a vykazují plynulý pokles velikosti, koncový poměr
0,72637. V prvním bylo jedno z 24 vzorkování pod detekčním prahem rámečku;
není tím tvrzeno, že každý snímek měl úspěšnou detekci. Jde o geometrické
změny skutečného zdrojového obsahu, nikoliv jen dva různě přiblížené stills.

## R2-F04: canonical captions a přehrání

Všech 73 nových cues má správné pořadí, nenulovou délku, nepřekrývá se
a zachovává celý původní pravopis osmi odstavců včetně Codegenu.
Reviewer samostatně ověřil přesnou shodu složeného textu s transcript
odstavci. Žádný cue není kratší než 1 s nebo nemá méně než tři slova.
Původní samostatné fragmenty typu „examples.“ a „znovu spusťte.“ tedy
v této podobě nezůstaly. Fonetické náhrady nejsou v titulcích.

Aktuální player evidence uvádí Microsoft Edge 157.0.4341.42, headed
přehrání a správný finální movie SHA. Reviewer při posledním retestu ověřil
všech 12 skutečných ON/OFF/burned screenshot hashů a SHA globálního VTT. Vizuálně
prohlédl `beginning_on.png`, `middle_on.png`, `ending_on.png` a
`ending_burned.png`: uvedené titulky jsou skutečně viditelné a diakritika
je správná. Ostatní playback kroky jsou doložené autorovým běžícím testem;
reviewer sám browser neotevíral.

**Poslední cílený bod — opraveno, retest PASS:** původní writer s width 43
vytvářel třířádkové SRT/VTT u cues 42 a 72. Autor zavedl vyvážené
zalamování do nejvýše dvou řádků při zachování všech 73 canonical textů
a časů. Reviewer samostatně porovnal skutečné nové SRT s `captions.json`:
všech 73 textů i časů odpovídá, maximální počet řádků je dva.

Reviewer nativně prohlédl nové `long_caption_on.png` v 202,590 s a
`ending_on.png` v 345,168 s. Oba problematické titulky mají dva čitelné
řádky a nepřekrývají note badge. Celý text a diakritika zůstaly zachované;
poslední věta už je skutečně zahrnuta v přehrávacím testu. Evidence
obsahuje čtyři pozice začátek/střed/dlouhý titulek/konec, všechny ON/OFF
i burned PNG hashe souhlasí. Nový základní SHA v tabulce odpovídá filmu,
playeru, aktuální zoom validaci i úzce obnovenému quality auditu.
Burned MP4 je byte-identický s dříve prohlédnutou variantou se SHA
`c3ca84bd…ea50f4`, takže obrazový obsah zůstává v původním rozsahu review.
Kvůli této čistě titulkové opravě nebyl znovu spouštěn celý capture,
hlasový audit ani plošný obrazový průchod.

## Finální výběrové obrazové review

Reviewer prohlédl všech pět aktuálních contactů
`evidence/final_frames/contact_1.jpg` až `contact_5.jpg`, tedy přehled
všech 30 finálních záběrů. Dále nativně prohlédl `cg_open.png`,
`cg_fill.png`, `cg_inspector.png`, `03_dom.png` a `07_details.png`.
Codegen zachovává skutečnou aplikaci a výsledný kód. Finální svislá maska
zakrývá úzkou mezeru mezi dvěma řízenými okny; v prohlédnutých rámcích
neukrývá generované řádky ani textbox. Původní chybné oříznutí levého
výsledku reportu se nevrátilo, Result/Passed a konkrétní testcase jsou
viditelné. V těchto obrazových vzorcích nebyla nalezena nová blokující vada.

Tento rozsah není plné nepřetržité zhlédnutí 5:48,48 ani lidský poslech
celé kapitoly. Doložené osobní schválení krátkého zvukového srovnání
neznamená automatické schválení celého vizuálního a zvukového standardu.
**Owner/PO gate celé referenční kapitoly zůstává PENDING. Výroba všech
12 kapitol před výslovným souhlasem zůstává neautorizovaná.**

## Dodatečná evidence reprodukce ze skutečného ZIPu

Reviewer přečetl nově předloženou `reproduction_validation.json` z autorova
běhu kompletního ZIPu po rozbalení do čerstvé cesty s mezerami. Záznam
uvádí byte-identické oba filmy s aktuálními výše nezávisle ověřenými SHA,
byte-identické globální SRT/VTT, správný commit
`129d317771d91da04e31e8150a2111188f9ae51f`, 78 neporušených zmrazených
souborů a 44 testů bez failure, error a skipped. Obsahuje také konkrétní
`render_inputs_sha256` pro návaznost následného balení na otestované vstupy.

Jde o kontrolu doložené autorovy evidence; reviewer tento další render,
rozbalení ani testovou sadu neopakoval. Běh přiznává existující připnuté
media prostředí, stejné Windows fonty a FFmpeg a nepoužití TTS služby.
Není vydáván za instalaci na čistém novém operačním systému. Toto technické
doplnění nemění rozsah schválené 30sekundové zvukové ukázky ani dosud
otevřené schválení celé kapitoly vlastníkem.
