# Nezávislá AI revize referenční kapitoly R2

Aktuální stav: **TECHNICAL_SOURCE_AND_SAMPLED_VISUAL_REVIEW_COMPLETE; owner/PO gate PENDING**.
Původní celý produkt zůstává podle mandátu R2 **CHANGES_REQUIRED**.
Kontrolu provádí druhý AI reviewer. Skutečný hotový film nebyl dosud
předložen k úplnému zhlédnutí ani poslechu; lidské či PO schválení zůstává
**PENDING**. Výsledky této revize neopravňují k výrobě celého kurzu.

Nálezy níže zachovávají původní stav návrhu. Jejich aktuální stav po
opravách určuje oddíl „Retest oprav“ na konci dokumentu.

Rozsah: `make_plan.py`, `prepare.py`, `capture.py`, `build.py`, aktuální
`plan.json`, `timeline.json`, `reference.json`, přehrávací podklady a nativní
word boundaries. Žádné GUI, browsery ani headed testy reviewer nespustil;
neměnil produkční zdroje. Legacy review není tímto dokumentem nahrazeno.

## Konkrétní nálezy

### R2-01 — HIGH: capture contract není přímo svázaný s přijatými receipty

Soubory: `capture.py` / `main`, `record_shot`; `build.py` / `main`.

Původně build spojoval plán se záběry pouze podle počtu a SHA klipu.
Autor mezitím přidal kontrolu hashů plánu, timeline, narration WAV a sedmi
konkrétních MP3/JSON a ověřování id/akce záběru. Tato část je zdrojově
provedená, ale při této kontrole ještě není úplná vazba na konkrétní take:
nový pokus přepíše `capture_contract.json` před prvním záběrem, zatímco
starý `capture.json` zůstává do dokončení všech záběrů. Pokud nový pokus
skončí před prvním zápisem klipu, build může přijmout starý capture stejného
id/akce a platných clip SHA pod novým contractem změněného komentáře.

Doporučení: contract hash a run_group uložit do každého receiptu i do
souhrnného capture a vyžadovat přesnou shodu při buildu. Nový neúplný take
nesmí být přijat jako dokončený. Po opravě zopakovat offline negativní
kontrolu scénáře starý capture + nový contract.

### R2-02 — HIGH: prodloužení obrazu může roztrhnout již začaté slovo

Soubory: `prepare.py` / příprava shot startů; `build.py` / skládání PCM.

Začátky shotů se zaokrouhlují na nejbližší snímek 25 fps. V aktuální
timeline leží 11 vnitřních začátků až uvnitř nativního prvního slova;
například `02_function` je 12,1 ms uvnitř slova „Pod“, `04_button_dom`
18,5 ms uvnitř „Vrátím“, `06_green_result` 15,6 ms uvnitř „Nyní“.
Samo přesné rozdělení a okamžité spojení PCM by nevadilo. Build ale při
delším skutečném záběru doplňuje za původní audio kus nulové PCM, a to až
do povoleného prodloužení 15 s. Při takové větvi pak vznikne ticho mezi
začátkem slova v předchozím kusu a jeho pokračováním v dalším. Souvislý
hlasový odstavec a nativní caption timing tím nejsou bezpečně zachovány.

Doporučení: případná prodloužení plánovat pouze na ověřených tichých
hranicích, případně zachovat souvislé audio a upravit obrazové časování.
Vyžadovat, aby žádná vložená mezera neležela uvnitř nativního slova nebo
plynulé fráze. Nález je doložen výpočtem z aktuální timeline a skutečných
boundaries, nikoliv tvrzením, že reviewer již slyšel hotový vadný film.

### R2-03 — HIGH: důkazy běhu dovolují staré soubory a deklarovaný nodeid

Soubor: `capture.py` / `Lesson.run`.

Čerstvý status promptu dokládá nový exit code. Načtený `junit.xml`, HTML
a vybraný první WEBM ale nejsou v kontrolované verzi přímo ověřeny jako
nové výstupy právě tohoto běhu; původní výstupní složky RED/GREEN se
opakují i mezi rehearsal a capture. Nový cílový archivní run_group sám
nezaručuje čerstvost kopírovaného zdroje. Dále se do obou důkazů zapisuje
`nodeid: NODE` jako konstanta. Závěrečné porovnání těchto konstant tedy
neověřuje skutečný classname/name testcase z JUnit.

Doporučení: samostatný nový output pro každý take a barvu; čerstvé JUnit,
HTML a browser video svázat se skutečným příkazem, zdrojovým SHA a run id.
Ověřit očekávaný skutečný classname/name, RED assertion a GREEN bez
skip/xfail; potom porovnat skutečnou identitu RED/GREEN. Výsledky starého
nebo jiného případu musí být odmítnuty.

### R2-04 — MEDIUM: výklad odsazení předbíhá napsaný kód

Soubory: `make_plan.py` / sekce 02; `capture.py` / `type_function`.

Věta „Všimněte si dvojtečky a odsazení následujícího řádku“ běží v shotu
`02_function`. Ten přidá pouze hlavičku funkce a newline; při vypnutém
autoIndent je další řádek prázdný. Odsazený `page.goto` přibývá teprve
v následující sekci. Divák tedy nemá pokynem pojmenované odsazení k vidění.

Doporučení: zobrazit skutečné odsazené tělo už při této větě, nebo ji
přepsat do budoucího času a vysvětlení odsazení navázat na jeho napsání.

### R2-05 — MEDIUM: čtyři dlouhé záběry vyžadují obsahové zdůvodnění

Zdroj: aktuální timeline, ještě nikoliv měření hotového filmu.

| Shot | Délka | Co je třeba prověřit nebo upravit |
|---|---:|---|
| `01_password` | 27,48 s | Fill, 1,2 s čekání, clear skončí rychle; potom zůstává dlouho stejný prázdný formulář. Rozdělit či zkrátit tuto část. |
| `02_function` | 23,36 s | Po napsání hlavičky zůstává dlouhý výklad. Konkrétně vybrat argument či skutečně ukázat odsazení, které se vysvětluje. |
| `03_dom` | 28,44 s | DOM výklad je účelný jen s čitelným vybraným h2 a průběžným vedením pozornosti ke skutečnému textu/roli. |
| `04_heading` | 22,20 s | Ukázat vysvětlované části locatoru a očekávání, nikoliv pouze obecný pomalý zoom celého editoru. |

Pohyb kamery nad jinak stejným obrazem sám nedokládá odstranění statiky
ani splnění praktického úkolu. U každé dlouhé pasáže je třeba její účel
ověřit skutečným zhlédnutím a odstranit neúčelnou výplň.

## Co bylo zdrojově nebo offline ověřeno

- Plán má 27 konkrétních shotů v sedmi souvislých odstavcích. Každý má
  voice cue, akci a očekávaný stav; délka aktuálního komentáře je přibližně
  357,67 s, tedy v mezích jediné referenční kapitoly 5–8 minut.
- Hlasová identita zůstává `cs-CZ-VlastaNeural`; předchozí schválení
  jiného hlasu se do R2 nevrací. QA má zůstat fonetická úprava pouze řeči.
- Skutečný DOM používá h2. Prohlédnutý diagnostický snímek ukazuje živý
  formulář a pravé DevTools s příslušným h2. Pro tento layout nebyla
  prokázána konkrétní blokující chyba plánovaného right zoomu; není to
  náhrada kontroly konečného ořezu a čitelnosti renderu.
- Výsledný test obsahuje navigaci a dvě skutečná očekávání, záměr RED
  mění jen text jednoho očekávání. Scénář věcně odlišuje ověření formuláře
  od úplného testu přihlášení.
- Přítomná Git bundle má hash odpovídající `reference.json` a
  `git bundle verify` skončilo 0. Referenční commit má 78 souborů včetně
  výukového manuálu. Kompletní samostatný reprodukční balík a build po
  jeho rozbalení zatím nebyly předloženy k ověření.
- `build.py` omezuje délku na 5–8 minut, výstup označuje
  `READY_FOR_HUMAN_REVIEW`, PO approval jako pending a celý kurz jako
  neautorizovaný. Tyto stavy nesmějí být zaměněny za kvalitativní schválení.

## Dosud neověřeno a podmínky dalšího gate

Čeká se na skutečný dokončený MP4, obrazově ověřené action proofs,
kontrolu smysluplné aktivity a audio–visual návaznosti, čitelnost výsledného
zoomu/značek, obě subtitle varianty a skutečné přehrání s on/off a seek
na začátku, uprostřed a na konci. Source existence nebo decode PASS tyto
body neuzavírají. Automatické přehrávací kontroly rovněž nejsou lidským
poslechem nebo pedagogickou akceptací.

Vlastník musí zhlédnout a poslechnout celou konkrétní referenční verzi
a výslovně ji schválit. Do té doby zůstává gate otevřený a opětovná výroba
celého kurzu není schválena.

## Retest oprav

Tento retest opět proběhl bez GUI a bez spuštění browseru. Nejde o zhlédnutí
nebo poslech hotového filmu. Nová aktuální timeline má sedm odstavců,
27 shotů a 348,456 s původního audia; obrazový plán po zaokrouhlení na
25 fps má 348,44 s.

| Nález | Aktuální stav a skutečný rozsah ověření |
|---|---|
| R2-01 / contract | **Opraveno zdrojově a offline.** Každý receipt nese contract SHA a run_group; build je ověřuje spolu s id a akcí shotu. |
| R2-02 / ticho uvnitř slova | **Opraveno zdrojově a offline.** Obraz používá plánovanou délku a build odmítá akci přesahující rozpočet; prodloužení audia podle délky capture bylo odstraněno. |
| R2-03 / důkaz běhu | **Převážně opraveno a reálná rehearsal evidence ověřena.** Zbývající source mez pro skipped/xfail je popsána níže. |
| R2-04 / předbíhající odsazení | **Opraveno v textu i aktuální timeline.** Nový komentář říká, že příkazy teprve přidáme a odsadíme. |
| R2-05 / dlouhá statika | **Částečně upraveno.** `01_password` zkráceno na 15,4 s; tři další delší úseky čekají na skutečný obraz a kvalitativní kontrolu. |

### Contract: negativní testy bez produkčních mutací

Reviewer vyňal skutečné guard AST z aktuálního `build.py` a spustil je
v paměti s náhradou hash funkce. Správná shoda prošla, starý contract,
starý run_group, jiné id i jiná akce byly odmítnuty. Všech pět případů
PASS. Staré záběry tak při změně contractu nemají být přijaty pouze podle
stejných id a platného SHA klipu. Jde o test těchto konkrétních podmínek,
nikoliv o již provedené nové kompletní capture/render.

### Audio: přímé ověření kontinuity PCM

Reviewer samostatně read-only rozřezal aktuální `narration.wav` podle nové
timeline a znovu složil kusy přesně algoritmem nového buildu, pouze v paměti.
Výsledek je byte-for-byte totožný prefix původního PCM. Rozdíl představuje
jen posledních 768 samples, tj. 16 ms skutečně nulového koncového ticha;
uvnitř komentáře nevznikla žádná nová mezera ani ztráta PCM. Tím se zavírá
konkrétní R2-02 bez tvrzení subjektivní poslechové kvality. Obrazová
návaznost akcí na komentář stále vyžaduje hotový film.

### RED/GREEN: ověření skutečných rehearsal důkazů

Nový příkaz zapisuje do jedinečné složky `reports/r2/{run_group}/{color}`.
Source načítá skutečný classname/name z JUnit, normalizuje je na nodeid,
ověřuje očekávaný test a čerstvost JUnit vůči Enter. Reviewer navíc
samostatně přečetl přítomnou rehearsal se 25 provedenými kroky a skutečné
archivované JUnit, HTML a WEBM obou barev:

- Oba JUnit obsahují stejný skutečný případ
  `tests/examples/test_video_created.py::test_video_login_form[chromium]`.
- RED má exit 1 a jedno failure, GREEN exit 0 a nula failures; obě barvy
  mají nula errors a nula skipped.
- Všech šest artifact SHA odpovídá receiptům; JUnit, HTML i video mají
  skutečné časy po začátku příslušného běhu. Původní starý output se zde
  nekopíroval jako nový důkaz.

**Zbývající konkrétní source mez:** kontrolovaná `Lesson.run` ještě
neodmítá elementy `<skipped>`. Jeden skipped nebo xfail testcase se
správným jménem, nula failures/errors a exit 0 by tak mohl projít jako
GREEN a dostat nesprávný popisek „1 passed“. Přítomný skutečný GREEN není
takto vadný — reviewer ověřil skipped 0. Doporučeno doplnit odmítnutí
`tree.findall('.//skipped')` pro obě barvy před přijetím výsledku.

### Statika a výsledný kvalitativní gate

Aktuální zbývající kandidáti přes 20 s jsou `02_function` 26,24 s,
`03_dom` 28,44 s a `04_heading` 22,20 s. Jde o konkrétní témata, která
lze smysluplně vysvětlit, ale teprve obraz ukáže, zda je výklad vedený
na skutečně viditelný argument, odsazení, DOM nebo části očekávání.
Prodloužení nového výkladu funkce není samo o sobě důkazem odstranění
statiky. Hodnocení čitelnosti, účelnosti pohybu a přirozenosti mluvy
zůstává otevřené. Skutečná owner/PO approval je nadále **PENDING**;
celý kurz není autorizovaný k opětovné výrobě.

## Kontrola skutečného capture: všech 27 akcí

Reviewer prohlédl všech 81 archivovaných PNG
`evidence/frames/{shot_id}_{0,1,2}.png` pro všechna id v tabulce níže.
Pro první průchod vytvořil devět kontaktních listů pouze v paměti, bez
nových souborů. Následně nativně prohlédl `02_function_1`, `03_dom_1`,
`04_heading_1`, `04_button_dom_1`, `05_wrong_1`, `06_fix_1`,
`05_red_result_1`, `06_green_result_1`, `07_details_1`, `07_final_code_1`.
Prohlédl také skutečný `layout_preview.png`.

Každou ze všech 81 PNG pak nezávisle ověřil novou extrakcí ze skutečného
příslušného MP4 do paměti: vzorkovací časy byly 0,3 s,
`min(actual_duration − 0,1; action_finished + 0,4)` a
`actual_duration − 0,3`. Všech 81 vzorků se přesnými RGB pixely shoduje
s archivem; hashe MP4 zůstaly během extrakce stejné. Jde o tři vzorky
každého klipu, nikoliv o nepřetržité zhlédnutí.

Celkový interval je z aktuální timeline; interval akce je relativní
k začátku klipu. Časy jsou v sekundách a zaokrouhlené na dvě desetinná místa.

| Shot id a prefix tří kontrolovaných PNG | Celkový interval | Akce v klipu | Viditelný výsledek |
|---|---:|---:|---|
| `01_open` | 0,00–17,04 | 5,34–5,83 | Skutečné přihlášení lokálního dema |
| `01_email` | 17,04–22,12 | 0,41–0,89 | Syntetický e-mail přibyl do pole |
| `01_password` | 22,12–37,52 | 0,41–3,02 | Pole se vracejí do prázdného stavu |
| `02_blank` | 37,52–54,40 | 0,41–0,41 | Skutečně prázdný soubor |
| `02_import` | 54,40–65,48 | 0,39–8,14 | Přibyl úvodní docstring a import Page/expect |
| `02_function` | 65,48–91,72 | 0,41–4,72 | Přibyla hlavička správné vlastní funkce |
| `03_goto` | 91,72–103,32 | 0,41–2,89 | Přibyl odsazený page.goto |
| `03_save` | 103,32–112,24 | 0,41–0,50 | Správný uložený rozpracovaný kód |
| `03_dom` | 112,24–140,68 | 0,41–3,64 | Živá stránka a skutečně vybraný h2 v DevTools |
| `04_heading` | 140,68–162,88 | 0,41–3,80 | Správný locator heading, exact a to_be_visible |
| `04_button` | 162,88–172,28 | 0,39–3,78 | Přibyla druhá kontrola tlačítka |
| `04_button_dom` | 172,28–188,72 | 0,41–4,67 | Vybrané skutečné button s textem Přihlásit se |
| `05_wrong` | 188,72–205,80 | 5,72–11,19 | Jen očekávaný nadpis změněn na neexistující |
| `05_red_command` | 205,80–209,84 | 0,41–0,41 | Skutečný příkaz jednoho konkrétního testcase |
| `05_red_run` | 209,84–221,76 | 0,41–11,30 | Skutečný běh, AssertionError a 1 failed |
| `05_red_browser` | 221,76–231,88 | 0,00–7,36 | Záznam formuláře ze skutečného RED běhu |
| `05_red_result` | 231,88–242,00 | 0,41–0,50 | Konkrétní failed nodeid a 1 failed |
| `06_failure_detail` | 242,00–258,20 | 0,41–0,86 | Dohledané chybné očekávání v assertion výpisu |
| `06_fix` | 258,20–269,08 | 0,41–5,89 | Oprava stejného řádku na Přihlášení |
| `06_green_command` | 269,08–273,76 | 0,41–0,41 | Tentýž testcase, samostatný GREEN output |
| `06_green_run` | 273,76–280,12 | 0,41–6,08 | Skutečné 1 passed |
| `06_green_browser` | 280,12–284,92 | 0,00–1,44 | Záznam formuláře ze skutečného GREEN běhu |
| `06_green_result` | 284,92–296,48 | 0,41–0,50 | Úspěšný skutečný terminálový výsledek |
| `07_report` | 296,48–306,48 | 0,39–1,09 | Otevřený odpovídající GREEN HTML report |
| `07_details` | 306,48–323,16 | 0,42–0,91 | Rozbalený stejný případ; detail s videem skutečného běhu |
| `07_final_code` | 323,16–334,32 | 0,39–0,50 | Celý správný test se dvěma očekáváními |
| `07_exercise` | 334,32–348,44 | 0,39–1,52 | Živý e-mailový prvek pro samostatné procvičení |

Tři standardní vzorky `01_password` zachycují stav před akcí a po vyčištění,
proto samy neukazují vložené heslo. Reviewer navíc sám extrahoval MP4 rámec
v 1,4 s: skutečné heslové pole je vyplněné maskovanými znaky a syntetický
e-mail je stále viditelný. Tím byl ověřen i prostřední stav této akce.
V kontrolovaných obrazech není soukromý chat, cizí IDE ani dřívější ghost.

### Vazba na skutečné důkazy a zavření R2-03

Reviewer znovu ověřil všech 17 input hashů contractu a všech 27 clip SHA,
id, akcí, run_group a contract SHA: bez nesouladu. Skutečné capture JUnit
mají stejný nodeid
`tests/examples/test_video_created.py::test_video_login_form[chromium]`.
RED má jeden failure a exit 1; GREEN nula failures a exit 0. Oba mají
nula errors a skipped. Všech šest hashů JUnit/HTML/WEBM odpovídá důkazům.
Porovnání skutečných textových snapshotů potvrzuje jedinou změněnou hodnotu
očekávání a finální kód byte-for-byte shodný se zmrazeným příkladem.

`Lesson.run` i následný `audit.py` už explicitně odmítají `<skipped>`.
Původní zbývající mez R2-03 je tedy zdrojově opravená a skutečné finální
capture důkazy jsou bez skip/xfail. Není třeba vydávat rehearsal za finální
capture: obě sady byly posouzeny odděleně.

Finální připravené WAV reviewer rovněž samostatně porovnal s původním:
obsahuje všechny původní PCM bajty a právě 24 ms nulového ticha navíc na
konci. Původní dříve popsané zkrácení koncového ticha tak bylo nahrazeno
úplným zachováním PCM. Nejde o subjektivní hodnocení slyšeného hlasu.

### Posouzení dlouhých držení podle skutečného obrazu

- `02_function`: po dokončení psaní zbývá přibližně 21,52 s. Výklad má
  konkrétní viditelný podklad: jméno testu, argument page, typ Page,
  dvojtečku a vysvětlení fixture; o odsazení nyní mluví pravdivě v budoucím
  čase. Nativní obraz zobrazuje odpovídající hlavičku. Je to obhajitelná
  vysvětlovací pauza, nikoliv doklad dalších prováděných akcí. Plynulost
  a přiměřenou délku musí rozhodnout owner při skutečném poslechu.
- `03_dom`: po výběru je přibližně 24,80 s stejného stavu. Vzorky skutečně
  ukazují h2/Přihlášení v DOM současně s formulářem. To podporuje výklad
  role, názvu a rozdílu vůči dlouhému CSS selectoru. Dlouhé držení má tedy
  konkrétní obsahový účel; nebyla nalezena věcná chyba vybraného prvku.
  Zoom ani případné značky se nepočítají jako nová aplikační aktivita.
- `04_heading`: po dopsání zbývá přibližně 18,40 s. Viditelný celý řádek
  odpovídá výkladu role heading, názvu, exact a viditelnosti. V této délce
  po akci nejde o další úsek nad 20 s. Layout preview zachovává celý
  vysvětlovaný řádek a činí jej čitelným.

Automatická raw activity evidence uvádí nízkou změnu 21,0 s a 25,5 s
u prvních dvou uvedených záběrů. Tyto příznaky zůstávají přiznané a jejich
obsahový účel je popsán výše. Reviewer je nemaže ani nepřeznačuje na nové
akce na základě animace kamery. V tomto vymezeném obrazovém průchodu
nebyla doložena další konkrétní blokující vada těchto tří výkladů;
pedagogická a poslechová akceptace zůstává na vlastníkovi.

### R2-06 — HIGH nalezeno a opraveno: levý ořez výsledku HTML reportu

Reviewer mimo raw PNG samostatně extrahoval původní vyrenderované
`rendered/07_details.mp4` v 8 s. Generický pravý browser zoom uřízl levý
okraj reportu včetně sloupce Result/Passed a části souhrnu 1 Passed;
z titulku report.html zbyl jen konec. Tento nález byl oznámen před dokončením
finálního rerenderu. Správný raw report existoval, takže nebylo třeba
měnit ani znovu natáčet skutečný testový výsledek.

Autor změnil pouze reportové akce na levý/horní anchor a zoom 1,35.
Reviewer po aktualizaci skutečných souborů v 12:36:49/52 znovu samostatně
extrahoval `rendered/07_report.mp4` i `rendered/07_details.mp4` v 8 s.
**Retest opravy PASS:** celý titulek, souhrn 1 Passed, sloupec Result/Passed
i skutečný nodeid jsou viditelné a zvětšené. Nález R2-06 je pro tyto
opravené renderované záběry uzavřený. Vazba na dosud dokončovaný finální
složený MP4 se tím nepředstírá; konečný SHA a regenerované finální snímky
je třeba ověřit po ukončení rerenderu.

Přítomná dřívější player evidence je testem konkrétní předchozí verze,
Microsoft Edge 157.0.4341.42, se ztlumeným audiem. Po změně filmu musí
znovu odpovídat jeho novému SHA. Úspěšné ON/OFF a burned screenshoty se
nesmějí vydávat za lidský poslech. Owner/PO approval a zákaz nové výroby
celého kurzu zůstávají beze změny.

## Závěrečný technický a výběrový obrazový audit referenčního filmu

Reviewer samostatně zahashoval oba uzavřené skutečné soubory. Výsledek:

| Varianta | Bajty | Skutečně ověřený SHA-256 |
|---|---:|---|
| MP4 s přepínatelnými titulky | 16 605 685 | `b79944263185898aa562779aea10c11d7cee0ec3417aeaf71cdb188ba99456fa` |
| MP4 s vypálenými titulky | 16 994 800 | `03e257aa4287cc0e4ddc41b9a037f17fdb3d266b1545c28d993db913544ff059` |

Délka je 348,48 s, tedy 5:48,48. Oba skutečné hashe odpovídají konečnému
`output/edit_project.json`. Přítomné úplné decode logy obou variant mají
0 bajtů; reviewer tento dlouhý decode neopakoval. Nové `quality_audit.json`
i `evidence/player/player_validation.json` odkazují na správný aktuální
základní SHA filmu. Tato vazba už nepoužívá předchozí sestřih.

Reviewer prohlédl všech pět aktuálně regenerovaných kontaktních listů
`evidence/final_frames/contact_1.jpg` až `contact_5.jpg`, které obsahují
všech 27 výsledných záběrů. Dále nativně zkontroloval finální
`02_function.png`, `03_dom.png`, `04_heading.png`, `07_report.png`
a `07_details.png`. Zelené rámečky ukazují skutečně napsané příslušné řádky;
nevytvářejí nový kód ani se nepočítají jako aplikační aktivita. V DOM je
čitelný skutečně vybraný h2 současně s příslušným nadpisem na stránce.
Opravené reportové výřezy nyní zachovávají výsledek i název skutečného testu.
R2-06 je tedy ověřený také v regenerovaných snímcích hotového sestřihu.

### Skutečný přehrávač a meze přehrávacích důkazů

Nová evidence doloženého headed testu Microsoft Edge 157.0.4341.42 má
správný movie SHA a správný SHA dodaného globálního VTT. Reviewer ověřil
všech devět hashů screenshotů. Samostatně prohlédl ON a OFF dvojice na
začátku v 8,203 s, uprostřed v 165,003 s a na konci v 343,177 s:
české titulky jsou skutečně viditelné po zapnutí a zmizí po vypnutí,
bez zakrytí důležitého kódu. Správný původní pravopis a diakritika jsou
v těchto vzorcích zachované. Jde o kontrolu přítomných skutečných důkazů;
reviewer sám GUI neotevíral.

Při prvním průchodu tří `*_burned.png` byly na screenshotu zobrazené
nativní ovládací prvky s tmavým gradientem přes dolní titulky, takže tyto
konkrétní screenshoty nebyly vhodným důkazem jejich dobré čitelnosti.
Samotné vypálené titulky jsou čitelné v prohlédnutých finálních filmových
rámcích; nešlo o novou vadu encodovaného filmu. Autorovi byl předán úzký
požadavek obnovit tyto tři playback screenshoty se skrytými controls,
bez dalšího renderování filmu. Tento dílčí nález byl následným skutečným
vizuálním retestem níže uzavřen; nikoliv pouze podle pole PASS v JSON.

### Závěr v přesně vymezeném rozsahu

Po uvedených opravách nebyla nalezena další blokující chyba zdrojů,
integrity a prohlédnutého obrazového obsahu. Skutečné psaní, živý DOM,
RED/GREEN stejného testu a report mají doložené konkrétní podklady.
Dvě přiznaná delší držení 21,0 s a 25,5 s nejsou vydávána za nové akce:
první vysvětluje viditelnou signaturu/fixture a budoucí odsazení, druhé
viditelný vybraný h2, jeho roli a jméno oproti CSS cestě. Jde o obsahově
odůvodněné vysvětlovací pauzy; subjektivní tempo a naučitelnost musí
posoudit vlastník při plném přehrání.

**Toto je druhá AI revize technických podkladů, skutečných důkazů a
obrazových vzorků. Není to úplné autentické zhlédnutí a poslech 5:48
člověkem ani schválení výukové kvality.** Automatický player test měl
ztlumený zvuk a výslovně uvádí `NOT_PERFORMED` u lidského poslechu.
Owner/PO approval zůstává **PENDING** a výroba celého kurzu je nadále
**neautorizovaná** do výslovného schválení této konkrétní referenční verze.

### Úzký závěrečný retest burned playback důkazů: PASS

Reviewer samostatně prohlédl nové `beginning_burned.png`,
`middle_burned.png` a `ending_burned.png` v `evidence/player/`.
Ovládací prvky i překrývající tmavý gradient jsou skutečně pryč.
Vypálené české titulky jsou ve všech třech snímcích čitelné, včetně
správné diakritiky. Nové vzorky jsou v 8,205 s, 165,005 s a 343,175 s;
všechny tři skutečné PNG hashe odpovídají aktualizovanému
`player_validation.json`. Evidence nadále odkazuje na konečný základní
SHA `b7994426…456fa`; obě varianty filmu se kvůli této opravě screenshotů
neměnily. **Poslední dílčí nález přehrávací evidence je uzavřený.**

Dodatečně byla předložena `reproduction_validation.json` z autorova běhu
skutečného kompletního ZIPu po rozbalení do nové cesty s mezerami.
Uvádí správný commit `129d317771d91da04e31e8150a2111188f9ae51f`,
78 zmrazených souborů, byte-identické oba MP4 i globální SRT/VTT a
44 testů bez failure, error a skipped. Uvedené movie SHA se shodují
s těmi, které reviewer dříve samostatně ověřil v této revizi. Reviewer
tento další render ani testovou sadu znovu nespouštěl; jde o kontrolu
nově předložené konkrétní evidence, nikoliv o druhou nezávislou instalaci.
Reprodukce přiznává použití existujícího připnutého media prostředí
a stejných Windows fontů, bez dalšího TTS požadavku; není vydávána za
test na čistém novém Windows.

Závěrečný rozsah zůstává technická, zdrojová a výběrová obrazová AI revize.
**Celé autentické lidské zhlédnutí a poslech a výslovné owner/PO schválení
zůstávají PENDING. Celý kurz se před tímto souhlasem znovu nevyrábí.**
