# 01 · Od manuálního testu k regresi

## Scéna 01_00

Vítejte v Playwright Academy. V tomto kurzu budeme pracovat jako testeři, kteří už znají manuální test case a chtějí jeho opakovanou část převést do programu. Naším společným příběhem je jeden požadavek v malém QA portálu. Nejdříve se přihlásíme, pak vytvoříme záznam, zkontrolujeme jeho údaje, změníme stav a záznam odstraníme. Nakonec celou sadu spustíme znovu a podíváme se, co znamená její výsledek. Půjdeme postupně. Když narazíte na nový pojem, nejprve vysvětlíme jeho účel a potom jej spojíme s konkrétním řádkem kódu. Na obrazovce používáme skutečnou lokální aplikaci a skutečně spuštěné testy. Přihlašovací údaje i požadavky jsou syntetické. Pro výuku nepotřebujete firemní síť. Podívejte se na připravený přehled: máme tři požadavky, různé řešitele a různé stavy. Díky tomu můžeme ověřovat více než pouhé otevření stránky. Za chvíli stejný přehled otevře automatizovaný test. Důležité je sledovat návaznost kroku a očekávání. Když člověk klikne na Uložit, přirozeně se podívá, jestli nový řádek přibyl. Program to sám neodhadne. Tuto kontrolu mu napíšeme výslovně. Právě jasná očekávání mění sled kliknutí v užitečný regresní test.

## Scéna 01_01

Regresní test ověřuje, zda dříve fungující chování zůstalo funkční po změně. Manuálně byste otevřeli portál, zadali přístupové údaje a zkontrolovali přehled. Automatizace provede stejnou cestu podle přesně popsaných pravidel. Užitečná je hlavně při opakování stabilních scénářů. Průzkumné testování a úsudek QA tím nekončí: test zná jen očekávání, která mu napíšete.

## Scéna 01_02

Python je jazyk zápisu. pytest soubory najde, připraví testovací prostředí a vyhodnotí výsledek. Playwright provede kroky v prohlížeči. Chromium vykreslí skutečnou aplikaci. Tento vztah není řetězec simulací: test opravdu kliká na HTML prvky a server opravdu ukládá změny do oddělené paměťové relace.

## Scéna 01_03

Při ručním průzkumu nejprve spustíme aplikaci pomocí připraveného spouštěče start_demo. V prohlížeči otevřeme lokální adresu portálu a přihlásíme se syntetickým účtem uvedeným v README. Na stránce Záznamy si můžeme vyzkoušet vytvoření požadavku. Automatickou sadu potom spustíme spouštěčem run_regression. Ta si připraví vlastní server a novou relaci, takže náš ručně vytvořený požadavek v jejích datech nebude. Je to záměr: každý běh potřebuje známý výchozí stav, který neovlivnila předchozí práce jiného testera.

## Scéna 01_04

Podívejme se na první funkci v souboru test_login.py. Její název popisuje otevření aplikace. Na prvním řádku těla testu voláme metodu goto a přecházíme na přihlašovací stránku. Následující očekávání kontrolují titulek a viditelný nadpis. Právě tato spojitost je důležitá: samotné otevření adresy ještě nedokazuje, že se načetl správný obsah. Test potřebuje také výslovně porovnat skutečný výsledek s tím, co požadujeme.

## Scéna 01_05

Teď si video na chvíli zastavte a napište tři části manuálního scénáře pro otevření přihlášení: jeho předpoklad, provedenou akci a očekávaný výsledek. Potom v zobrazeném testu najděte řádky, které jim odpovídají. Pro porovnání máte v řešeních první lekce samostatný příklad otevření stránky. Úkol je hotový ve chvíli, kdy dokážete vlastními slovy vysvětlit, jaká změna aplikace by toto ověření porušila a proč by test správně selhal.

## Scéna 01_06

Zkusme se ještě na chvíli vrátit k tomu, jak by stejný scénář vypadal při manuálním testování. Když zadáte přihlašovací údaje a stisknete tlačítko, nehodnotíte pouze to, zda se na obrazovce něco pohnulo. Zajímá vás, zda aplikace rozpoznala správného uživatele a pustila ho do správné části systému. Automatizovaný test potřebuje stejně konkrétní očekávání. Právě proto v naší první kontrole hledáme nadpis přehledu a nespoléháme se jen na to, že přihlašovací tlačítko šlo stisknout. Kdyby po kliknutí přišla chybová stránka, samotná akce by mohla proběhnout úspěšně, ale náš požadavek by splněný nebyl. Tento způsob přemýšlení už jako manuální testeři znáte. Nové je především to, že musíme jednotlivé podmínky vyjádřit tak přesně, aby je program dokázal opakovat bez našeho úsudku. Podobně je potřeba přemýšlet o výchozím stavu. Pokud si ručně vytvoříte požadavek a potom očekáváte přesně tři položky v automatickém testu, můžete dostat zdánlivě nesrozumitelný výsledek. V našem projektu tomu předcházíme oddělením relací. Ruční prohlížeč má svá data a každý automatický test dostává vlastní kopii tří výchozích požadavků. Neznamená to, že se aplikace tváří pokaždé jinak. Znamená to, že každý případ začíná za stejných předpokladů. Když jeden test záznam odstraní, další má stále k dispozici nezměněný výchozí stav. Při výběru regresních scénářů začínejte chováním, které se často opakuje, má jasný výsledek a pro uživatele je důležité. Přihlášení nebo uložení formuláře bývají vhodnější první krok než dlouhá cesta s mnoha nepředvídatelnými závislostmi. Krátký úspěšný test nám rychle potvrdí, že prostředí vůbec funguje, a teprve potom budeme přidávat další kontroly. Současně si necháme prostor pro manuální průzkum. Automatizace nepozná, že je nová funkce matoucí, pokud jsme srozumitelnost nijak nepopsali. Užitečný výsledek tedy není co největší počet zelených řádků, ale důvěryhodná sada kontrol, u kterých víme, proč existují. Až budete po kurzu přidávat vlastní test, zkuste jeho smysl nejprve vysvětlit kolegovi jedinou souvislou větou. Pokud není jasné, co ověřuje a za jakých předpokladů, bývá lepší ještě upravit samotný scénář. Tím si ušetříte mnoho pozdějšího ladění.

## Scéna 01_07

Na obrazovce se ještě jednou podívejte na malý přihlašovací test a zkuste jeho řádky přiřadit k manuálnímu scénáři. Otevření stránky odpovídá první akci uživatele. Nalezení nadpisu popisuje očekávaný obsah a kontrola viditelnosti z něj dělá skutečné ověření. Kdybychom tento poslední krok odstranili, program by mohl stránku navštívit a skončit bez důkazu, že otevřel správné místo. Zelený výsledek by pak znamenal méně, než jak se na první pohled zdá. Tento rozdíl si budeme připomínat i v delších scénářích. Při automatizaci obvykle nezačínáme od neznámé technické knihovny, ale od známého uživatelského požadavku. Zápis v Pythonu je jeho přesnější, opakovatelná podoba. Když později uvidíte červený řádek v reportu, vraťte se právě k tomuto požadavku. Díky tomu budete vědět, co mělo fungovat a jakým důkazem test poznává správný výsledek.

# 02 · Instalace a první spuštění

## Scéna 02_00

Teď si připravíme prostředí, ve kterém všechny další ukázky poběží. Na této stanici máme Windows jedenáct a ověřený Python řady tři dvanáct. Nejprve kontrolujeme verzi, abychom případné instalační potíže neřešili změnou testovacího kódu. Projekt si můžete představit jako složku se třemi důležitými částmi: aplikací, testy a knihovnami potřebnými k jejich spuštění. Knihovny se instalují do odděleného prostředí. Nepotřebujeme tím měnit Python ostatním projektům ani aktivovat administrátorský účet. V připraveném instalačním spouštěči se každý krok skutečně provádí a případná chyba se vrací do terminálu. Zelenou větu na konci nevytváříme ručně. Objeví se až po úspěšné instalaci balíčků, kontrole jejich závislostí a instalaci browseru. Vidíte také důležitý rozdíl mezi prvním a opakovaným spuštěním. Při prvním vzniká nové prostředí, při dalším se již nainstalované přesné verze použijí znovu. V obou případech ověřujeme skutečný výsledek. Při použití firemní proxy může být potřeba schválená konfigurace od IT. Nevypínáme kvůli tomu kontrolu certifikátů. Jakmile instalace projde, spustíme malý test a teprve pak celou regresi. Tento postup pomáhá odlišit chybu prostředí od chyby aplikace.

## Scéna 02_01

Postupujte podle instalačního průvodce. Terminál je způsob, jak programu předat přesný příkaz a vidět odpověď. Začněte kontrolou Pythonu. py -3.12 --version nevytváří test; pouze zjistí, zda je požadovaný interpreter dostupný. Pokud není, další instalaci zatím nepovažujte za úspěšnou.

## Scéna 02_02

Instalační spouštěč vytvoří .venv, tedy samostatné prostředí tohoto projektu. Balíček je sada cizího kódu, kterou používáme. requirements.lock zaznamenává konkrétní ověřené verze všech potřebných balíčků. Balíčky a browser jsou dvě odlišné instalace: přítomnost Playwrightu ještě neznamená přítomnost Chromia.

## Scéna 02_03

Projekt otevíráme ve VS Code jako celou složku. V nabídce Python: Select Interpreter zvolíme interpreter z projektového virtuálního prostředí. Dříve otevřený terminál však může stále používat jiný Python. Proto v příkazech ukazujeme přímou cestu k python.exe uvnitř projektové složky .venv. Tak jednoznačně určíme, který interpreter test spouští. Prostředí nemusíme ručně aktivovat a nepotřebujeme měnit bezpečnostní politiku PowerShellu.

## Scéna 02_04

Po instalaci začínáme rychlou kontrolou přihlášení pomocí spouštěče run_smoke. Jeho zelený výsledek znamená, že test dokázal otevřít aplikaci a ověřit přihlášení. Pokud chceme kroky sledovat v okně prohlížeče, použijeme připravený spouštěč run_visible. Ten spustí stejný typ kontroly ve viditelném režimu. Parametr slowmo pouze zpomalí prováděné akce pro člověka; nepoužíváme ho jako náhradu správného čekání na připravenost aplikace.

## Scéna 02_05

Ve druhém úkolu spusťte konkrétní test podle řešení instalační lekce. Potom otevřete HTML report a najděte v něm jeho název. Zapište si verzi Pythonu a použitý prohlížeč, abyste uměli výsledek později jednoznačně popsat. Když instalace hlásí chybějící browser, nejprve zkontrolujte instalaci Chromia v projektovém prostředí. Opravujeme prostředí, ve kterém test běží; funkční test kvůli této instalační chybě nepřepisujeme.

## Scéna 02_06

Při instalaci se snadno smíchají tři různé otázky: který Python právě spouštíme, kde jsou nainstalované knihovny a zda už máme připravený prohlížeč. Když je od sebe oddělíte, bude většina běžných potíží mnohem srozumitelnější. Kontrola verze vám řekne pouze to první. Pokud terminál ukáže jinou řadu Pythonu, než očekává projekt, není ještě důvod měnit testovací funkci. Nejprve zvolíme správný interpreter. Potom se podíváme na prostředí projektu. Složka s názvem tečka venv obsahuje jeho vlastní spustitelný Python a balíčky, které jsme do něj nainstalovali. Proto v příkazech používáme přímo cestu do této složky. Tím nezávisíme na tom, jaký Python byl dříve přidaný do systémové proměnné PATH. Můžete mít na jedné stanici více projektů a každý z nich může potřebovat jinou sadu závislostí. Důležité je nepřenášet jednu hotovou virtuální složku mezi počítači, protože může obsahovat cesty navázané na původní instalaci. Kolega dostane zdrojové soubory a na své stanici si prostředí vytvoří znovu. Přesné verze potřebných knihoven najde instalační skript v uzamčeném seznamu závislostí. Třetí částí je samotný browser. Playwright musí mít verzi Chromia, kterou jeho vydání očekává. Běžně nainstalovaný firemní Chrome tento krok automaticky nenahrazuje. Když tedy Python umí knihovnu importovat, ale test hlásí chybějící spustitelný prohlížeč, instalace balíčků už mohla být v pořádku. Doplníme pouze odpovídající browser a znovu spustíme krátký test. Podobně postupujeme u firemní sítě. Chyba certifikátu nebo proxy se řeší nastavením schváleného přístupu, nikoliv vypnutím kontroly bezpečnosti. Pokud si nejste jistí, uchovejte přesné znění chyby a předejte je kolegovi z IT bez přihlašovacích údajů. V editoru pak ještě zkontrolujte vybraný interpreter. Terminál a editor nemusejí automaticky používat stejný program, zvlášť když byl projekt otevřený už před instalací. Jakmile malá smoke sada projde a umíte otevřít její report, máme pevný základ pro další práci. Pokud se později test rozbije po změně aplikace, nebudeme zbytečně znovu instalovat celý počítač. Už víme, které části prostředí byly skutečně ověřené a jak je případně zkontrolovat samostatně.

## Scéna 02_07

V připraveném instalačním postupu si všimněte ještě návratového kódu. Je to stručný signál, který může přečíst člověk i další program. Nulová hodnota obvykle znamená úspěšné dokončení, nenulová upozorňuje na problém. Náš spouštěč proto nesmí po neúspěšné instalaci jen vytisknout povzbudivou zprávu a vrátit úspěch. Kdyby to dělal, začátečník by pokračoval k testům s neúplným prostředím a chyba by vypadala jako závada v kódu. Proto instalátor kontroluje jednotlivé kroky a výsledek zachovává. Při opakovaném spuštění se také nedotýká už vyplněné místní konfigurace. Jednotlivé chyby čteme v jejich souvislosti: chybějící Python, nepřístupná síť a chybějící browser vyžadují rozdílnou opravu. Jakmile rozumíte této návaznosti, není potřeba zkoušet náhodné příkazy z internetu. Máte konkrétní místo, které ověříte, a malý smoke test, kterým následně potvrdíte funkční celek.

# 03 · Python pro testera

## Scéna 03_00

Než začneme psát vlastní browser test, projdeme malé množství Pythonu, které k němu skutečně potřebujeme. Nemusíte se nejprve učit celý programovací jazyk. Budeme číst jednoduché funkce a sledovat, odkud přicházejí jejich hodnoty. Na obrazovce je funkce, která upravuje název syntetického požadavku. Dostane text, odstraní přebytečné mezery a vrátí výsledek. Když po odstranění mezer nezůstane nic, vrátí náhradní název. To je konkrétní důvod pro podmínku. Všimněte si, že funkce sama neví, jaký text jí později předáme. Parametr je právě jméno tohoto vstupu. Stejný princip potkáme u testu, jehož parametrem bude připravená stránka prohlížeče. Také rozlišíme chybu zápisu a neúspěšné očekávání. Když Python nerozumí odsazení, test se ani nezačne provádět. Když je zápis správně, ale očekáváme jinou hodnotu, pytest ukáže neúspěšný test. Obě situace vyžadují jinou opravu. V našem příkladu nejprve čteme funkci, potom ji skutečně spustíme a nakonec si změníte vstupní data sami. U každého řádku se ptejte: jaká hodnota sem vstupuje, co se s ní děje a jak ověřujeme výsledek.

## Scéna 03_01

Proměnná je jméno pro hodnotu: title = "Kontrola exportu". Uvozovky tvoří řetězec, tedy text. Číslo 3 a text "3" jsou různé typy hodnot. Seznam ["Jana", "Petr"] drží více položek; slovník {"status": "Nový"} spojuje jména s hodnotami. Testovací data tak nemusíte opisovat v každém kroku.

## Scéna 03_02

Funkce je pojmenovaný postup. zobrazený výraz definuje funkci, kterou pytest spustí. page je parametr: místo, kam pytest předá připravený objekt stránky. : Page pomáhá editoru, -> None říká, že funkce nevrací výsledek k dalšímu zpracování. O úspěchu testu rozhodují ověření.

## Scéna 03_03

Objekt v programu spojuje data se schopnostmi, které nad nimi můžeme používat. Objekt stránky například umí přejít na adresu pomocí metody goto. Tečka mezi page a názvem metody říká, že tuto schopnost voláme právě na konkrétní stránce. Import na začátku souboru nám zase zpřístupňuje jména z knihovny. Samotný import ještě neotevírá prohlížeč ani neprovádí přihlášení; k těmto akcím dojde až při vykonání příslušných řádků testu.

## Scéna 03_04

Čtyři mezery určují tělo funkce. Míchat tabulátory a mezery vede k chybě odsazení. Podmínka if status == "Nový": provede odsazené řádky jen při splnění porovnání. = přiřazuje hodnotu, == porovnává. V UI testech však nepište podmínku, která při chybě aplikace přeskočí assertion; závada má test zastavit, nikoliv tiše vynechat kontrolu.

## Scéna 03_05

Nyní si vytvořte kopii řešení třetí lekce a v seznamu záznamů změňte dva názvy na jiné syntetické hodnoty. Než soubor spustíte, vysvětlete si, co přijímá funkce normalize a jakou hodnotu vrací. Potom zkuste záměrně poškodit odsazení jednoho řádku. Přečtěte vzniklou chybu, najděte odpovídající místo a odsazení vraťte. V této části procvičujeme práci s daty, funkcí a podmínkou; prohlížeč k tomu ještě nepotřebujeme.

## Scéna 03_06

Podívejme se podrobněji na to, co se děje při zavolání jednoduché funkce. V ukázce máme text názvu požadavku a chceme odstranit mezery, které se mohou objevit na jeho začátku nebo konci. Původní hodnota je řetězec. Když nad ním zavoláme metodu pro odstranění okrajových mezer, dostaneme nový upravený řetězec a uložíme ho do další proměnné. Samotné jméno proměnné nemusí být anglické kouzelné slovo. Volíme ho tak, aby bylo srozumitelné, co uvnitř očekáváme. V testovacím projektu ale používáme jednotné názvosloví, protože kód budou číst další lidé. Funkce pak rozhodne, zda po úpravě něco zůstalo. Pokud je text prázdný, vrátí náhradní název. Pokud prázdný není, vrátí upravenou hodnotu. Návratová hodnota je tedy výsledek, který může použít další část programu. Když funkci zavoláme třikrát s jinými vstupy, provede pokaždé stejná pravidla, ale může vrátit jiný výsledek. Všimněte si rozdílu mezi definicí a voláním. Definicí Pythonu říkáme, jaký postup má být připravený. Voláním mu zadáme, aby tento postup provedl teď s konkrétními daty. Stejný rozdíl platí pro testovací funkce. Jejich těla se nespouštějí jen tím, že je vidíte otevřená v editoru. Najde je a zavolá pytest. Import na začátku souboru zase zpřístupňuje jména z jiného modulu. Není to automatická akce v prohlížeči. Když importujeme ověřovací funkci, pouze si připravujeme možnost ji později použít. Dvojtečka za definicí a následující odsazení určují, které příkazy k funkci patří. Pokud odsazení odstraníte, změní se struktura programu nebo vznikne chyba dříve, než se vůbec otevře stránka. Proto má smysl číst první chybu v terminálu a rozlišit, zda jde o syntaxi, přípravu prostředí, nebo nesplněné očekávání. V běžném testu se vám budou opakovat stejné základní stavební prvky: pojmenovaná hodnota, zavolání metody, předání argumentu a kontrola výsledku. Nemusíte umět napsat vlastní webový server, abyste těmto řádkům rozuměli. Potřebujete ale dokázat ukázat, odkud se do testu bere konkrétní text a proč porovnáváme právě tuto hodnotu. Jakmile to dokážete u malého příkladu, budete stejným způsobem číst i skutečný browser test.

## Scéna 03_07

Zastavme se ještě u argumentů v závorkách. Když metodě předáme text názvu stránky, říkáme jí, jakou konkrétní hodnotu má použít. Jméno parametru v definici je obecné, hodnota při volání je konkrétní. U formuláře tak může být argumentem e-mail, u ověření očekávaný nadpis a u filtrování požadovaný stav. Pojmenované argumenty pomáhají poznat jejich účel. Například požadavek na přesnou shodu jména nezaměňujeme s jiným pozičním vstupem, protože je u hodnoty přímo uvedené, co ovlivňuje. Tečka před názvem metody zase ukazuje objekt, nad kterým ji voláme. To nám při čtení napovídá, zda pracujeme s celou stránkou, vybraným prvkem, nebo třeba textovou hodnotou. Jakmile se naučíte tuto strukturu rozpoznávat, přestane dlouhý řádek působit jako jeden nerozluštitelný příkaz. Rozdělíte si ho na známý objekt, požadovanou schopnost a vstupní hodnoty, jejichž význam umíte vysvětlit.

# 04 · První vlastní test

## Scéna 04_00

Máme připravené prostředí i základní slovník Pythonu. Teď vznikne nový test od prázdného souboru. Nebudeme kopírovat složitou architekturu. Vložíme import, definujeme jednu testovací funkci, otevřeme přihlášení a ověříme viditelný nadpis. Každý řádek má konkrétní účel. Import zpřístupní jména z knihovny. Název funkce umožní pytestu rozpoznat test. Parametr stránky požádá o připravenou browser kartu. Navigace otevře konkrétní cestu. Poslední řádek vyjadřuje očekávaný výsledek. Všimněte si také závorek a odsazení. Není potřeba si pamatovat všechny podoby syntaxe najednou. Důležité je rozpoznat, která část popisuje hledaný prvek a která část říká, co o něm tvrdíme. Po napsání soubor uložíme a spustíme přesně tento jeden test. Pokud se nový soubor nepřidá mezi nalezené testy, zkontrolujeme jeho název i název funkce. Teprve když samostatný test prochází, doplníme další kontrolu. Tím získáme krátkou a čitelnou zpětnou vazbu. Později jej můžeme zařadit do širší sady, ale během psaní nemusíme po každé změně spouštět všechno.

## Scéna 04_01

Před sebou máme nový test v souboru test_video_created.py. Jeho soubor i funkce začínají předponou test_, podle které je pytest při sběru rozpozná. Nejprve importujeme potřebné nástroje, potom definujeme funkci s připravenou stránkou a do jejího těla zapíšeme navigaci i očekávání. Při čtení postupujte shora dolů. Každý řádek by měl mít srozumitelný účel, který dokážete spojit s konkrétní částí manuálního scénáře.

## Scéna 04_02

První řádek importuje typ stránky a ověřovací nástroj. Parametr page požádá pytest o připravenou kartu browseru. Tomuto mechanismu říkáme fixture; zatím potřebujete vědět hlavně to, že ji nemusíte vytvářet ručně. goto přejde na cestu v automaticky spuštěném demu. Základ URL dodává konfigurace fixture, proto nezapisujeme port 5000 do testu.

## Scéna 04_03

get_by_role popíše hledaný prvek jako nadpis se jménem Přihlášení. exact=True požaduje úplnou shodu jména. Výsledek je Locator, tedy popis cíle. expect(...).to_be_visible() opakovaně kontroluje viditelnost do limitu; neporovnává jen jediný okamžik. Pokud nadpis nepřijde, test selže.

## Scéna 04_04

Teď nový soubor skutečně spouštíme projektovým Pythonem přes pytest. V příkazu vybíráme jediný soubor, takže se do výsledku nepřimíchají ostatní testy. Sledujte dokončení běhu i návrat promptu v terminálu. V reportu potom najdete název souboru, funkce a použitý browser. Při samostatném procvičení můžete v kopii změnit očekávaný nadpis na chybný, přečíst selhání a potom správné očekávání vrátit.

## Scéna 04_05

Ve čtvrtém úkolu rozšiřte svůj test o kontrolu viditelného tlačítka Přihlásit se. Najděte ho podle jeho role a názvu, aby bylo z kódu poznat, co uživatel vidí. Potom test znovu spusťte a porovnejte ho s řešením čtvrté lekce. Úspěšný výsledek má nyní dokazovat viditelnost obou důležitých prvků. Pouhé přidání dalšího kliknutí by tento úkol nesplnilo, protože by chybělo nové ověření.

## Scéna 04_06

Přečteme si teď první test tak, jako byste jej měli vysvětlit kolegovi, který u jeho psaní nebyl. Na začátku si z knihovny zpřístupňujeme typ stránky a ověřovací funkci. Typ stránky pomáhá editoru nabízet správné metody a nám připomíná, s jakým objektem pracujeme. Sám o sobě ale browser nevytváří. Připravená stránka přichází do testu jako parametr a její vznik zajistí pytestová fixture. Název funkce začíná předepsanou předponou, podle které ji testovací nástroj pozná. Když soubor nebo funkci pojmenujete jinak, mohou být syntakticky správné, ale při běžném sběru se vůbec nespustí. Proto vždy sledujte také počet nalezených a provedených testů. První skutečný krok otevře přihlašovací cestu. Zapisujeme pouze cestu uvnitř aplikace, protože společnou základní adresu dodává příprava testu. Ta při automatickém běhu vybere volný port. Kdybychom do funkce napevno vložili adresu ručního dema, test by mohl fungovat jen tehdy, když nám vedle něj náhodou běží jiné okno serveru. Takovou skrytou závislost nechceme. Následující výraz popisuje očekávaný nadpis pomocí role a jména. Zatím ještě neprovádí kontrolu viditelnosti; vytváří lokátor. Teprve ověření obalené funkcí expect říká, že má být tento konkrétní nadpis na stránce vidět. Pokud se stránka načítá o něco déle, ověření se po omezenou dobu opakuje. Když se požadovaný stav nedostaví, dostaneme jednoznačné selhání s popisem hledaného cíle. Přidáním kontroly přihlašovacího tlačítka neověříme celý proces přihlášení. Ověříme však, že formulář nabízí očekávanou akci. Je v pořádku mít takto malý test, pokud jeho název a popis odpovídají skutečnému rozsahu. Až budeme kontrolovat úspěšné přihlášení, doplníme vyplnění údajů, odeslání a výsledek v přehledu. Při psaní nového testu ukládejte soubor a spouštějte nejprve právě tento případ. Když uděláte jednu malou změnu a hned vidíte její výsledek, lépe poznáte její dopad. Celou sadu pak použijeme jako kontrolu, že nová práce neovlivnila jiné scénáře. Právě tato krátká zpětná vazba pomáhá začátečníkovi postupovat jistě a bez zbytečného hádání.

## Scéna 04_07

Při porovnání s referenčním řešením není důležité mít úplně stejné jméno vlastní testovací funkce. Důležité je zachovat pravidla sběru a stejné očekávané chování. Pokud jste doplnili kontrolu tlačítka přes jeho roli a jméno, mělo by být z testu jasné, kterou akci formulář nabízí. Jestli jste místo toho sáhli po dlouhé cestě přes několik HTML obalů, zkuste se vrátit k uživatelskému významu prvku. Zároveň si ověřte, že váš test opravdu běží. Uložený soubor otevřený v editoru a provedený test jsou dvě různé věci. V terminálu musí být vidět odpovídající nalezený případ a jeho skutečný výsledek. Tento malý návyk se vyplatí i zkušenějším testerům, protože překlep ve výběrovém parametru nebo jiné jméno souboru může vést k tomu, že kontrolujeme úplně jiný rozsah, než jsme zamýšleli.

# 05 · Stabilní lokátory

## Scéna 05_00

Test už umí otevřít stránku. Potřebujeme ale bezpečně popsat, se kterým prvkem chceme pracovat. Tomuto popisu říkáme lokátor. Není to obrázek prvku ani jeho souřadnice na obrazovce. Browser test musí fungovat i tehdy, když se tlačítko trochu posune. Proto začínáme významem prvku: jeho rolí a přístupným jménem. U formulářového pole často nejlépe pomůže propojený popisek. Ukážeme si přihlášení a potom tabulku, ve které je více stejných akcí. Právě tabulka dobře vysvětluje, proč nestačí napsat pouze Upravit. Tester potřebuje určit, který požadavek upravuje. Nejprve proto vybereme správný řádek a až uvnitř něj hledáme jeho tlačítko. Tato vazba je čitelná i pro kolegu, který test později převezme. Když popis odpovídá více prvkům, Playwright akci odmítne. To není zbytečná překážka. Chrání nás před náhodným kliknutím na jiný záznam. U počtu řádků naopak více shod očekáváme a ověřujeme jejich počet. Stejný lokátor tedy může být správný pro ověření množiny a nejednoznačný pro jednotlivé kliknutí. Tento rozdíl budeme kontrolovat na skutečných prvcích portálu.

## Scéna 05_01

DOM je strom prvků, ze kterých browser skládá stránku. HTML element může být například tlačítko, pole nebo řádek tabulky. Role popisuje jeho účel: button, textbox, heading, row. Accessible name je jméno, které prvek poskytuje asistenčním nástrojům; často odpovídá viditelnému popisku. U tlačítek Upravit je v našem portálu doplněné i jméno konkrétního požadavku.

## Scéna 05_02

Pole vybírejte přes label: zobrazený výraz. Tlačítko přes roli a jméno: zobrazený výraz. page.get_by_test_id("record-row") vybírá všechny datové řádky podle domluveného technického identifikátoru. Test ID je vhodný kontrakt, pokud uživatelská sémantika nestačí. Není to heslo ani interní ID databáze.

## Scéna 05_03

Pokud lokátor pro kliknutí najde více prvků, nastane strict mode violation. To chrání test před kliknutím na náhodný cíl. Nespravujte vše pomocí first. Nejprve omezte oblast: zobrazený výraz a uvnitř řádku hledejte konkrétní tlačítko. to_have_count naopak s více prvky vědomě pracuje.

## Scéna 05_04

CSS selektor jako body se hodí pro obecnou kontrolu dostupnosti. Dlouhá cesta přes pořadí divů nebo XPath snadno přestane odpovídat po změně layoutu. Inspector a Pick Locator pomohou zjistit skutečné role a jména. V Codegenu nejprve vypněte nahrávání, vyberte Pick Locator a ukažte na prvek.

## Scéna 05_05

V této lekci si samostatně najděte lokátor hesla a přihlašovacího tlačítka. Po přihlášení ověřte, že portál obsahuje tři datové řádky. V řešení páté lekce si pak porovnejte způsob, jakým jsou tyto prvky vybrané. Zkuste také vysvětlit rozdíl mezi datovým řádkem a všemi prvky s rolí row. Tabulka má navíc hlavičku, takže její celkový počet řádků nemusí odpovídat počtu uložených požadavků.

## Scéna 05_06

U lokátorů nám pomůže představit si dvě různá rozhraní. V prvním je jen jeden přihlašovací formulář. Pole mají jasné popisky a tlačítko jednoznačný název. Tam je přirozené vybrat pole podle jeho popisku a tlačítko podle role. Ve druhém rozhraní je tabulka s desítkami požadavků a každý řádek má vlastní tlačítko pro úpravu. Slovo Upravit už samo nestačí, protože nerozlišuje, kterého požadavku se akce týká. Test musí nejprve vymezit oblast správného řádku a teprve uvnitř něj určit požadovanou akci. Tím se jeho zápis podobá tomu, jak byste zadání vysvětlili člověku: najdi požadavek s tímto názvem a otevři jeho úpravu. Lokátor není jednou uložený obrázek nebo ukazatel na starý HTML element. Je to popis, který Playwright při další akci znovu vyhodnotí. Proto stejná proměnná řádku může posloužit i po překreslení tabulky. Přesto musí zůstat dostatečně přesná. Kdyby názvy dvou požadavků obsahovaly stejný hledaný podřetězec, náš popis by mohl znovu odpovídat více řádkům. V takové situaci upřesníme testovací data nebo hledanou oblast. Nespravujeme to náhodným výběrem první shody. U počítání položek naopak vědomě pracujeme s množinou prvků. Ověření tří datových řádků tedy používá lokátor, kterému mají odpovídat tři prvky. Kliknutí stejným lokátorem by však bylo nejednoznačné. Pozor také na hlavičku tabulky: i ta má roli řádku, ale není jedním z našich tří záznamů. Právě proto máme pro datové řádky domluvený testovací identifikátor. Popisuje účel prvku pro automatizaci a nezávisí na tom, jaké barvy nebo rozměry má tabulka. Při hledání vhodného cíle vám může pomoci Inspector, ale konečnou volbu stále posuzujete vy. Ptejte se, zda by lokátor fungoval po drobné úpravě vzhledu a zda by kolega z jeho zápisu pochopil, co se vybírá. Stabilita neznamená, že se prvek nikdy nezmění. Znamená to, že náš test reaguje na změnu významu nebo smluveného rozhraní, místo aby se rozbíjel při každém přesunu pomocného HTML obalu.

## Scéna 05_07

Při práci s konkrétním řádkem tabulky si můžete správnost lokátoru ověřit po malých krocích. Nejdříve se ujistěte, že oblast obsahuje právě zamýšlený požadavek. Potom v ní vyhledejte akční tlačítko. Teprve následně proveďte změnu. Takové rozdělení pomáhá odlišit problém ve výběru řádku od problému v samotné akci. Stejně důležité je vědět, kdy používáte přesnou shodu a kdy hledání podřetězce. Název Kontrola přihlášení může být částí delšího názvu po úpravě. Pokud očekáváte jejich rozlišení, musí tomu odpovídat i váš lokátor. Automatizace by neměla spoléhat na to, že zrovna dnes existuje jen jeden podobný požadavek. Naše izolovaná data tuto situaci usnadňují, ale zásada jednoznačného cíle zůstává stejná i ve skutečné aplikaci s větším počtem řádků.

# 06 · Akce a očekávání

## Scéna 06_00

Teď už umíme cíl najít. Dalším krokem je provést akci a ověřit, že skutečně způsobila požadovanou změnu. Otevřeme nový požadavek, vyplníme název, vybereme řešitele a nastavíme prioritu. Potom formulář uložíme. Během tohoto postupu si všímejte rozdílu mezi vyplněním pole a kontrolou jeho hodnoty. Vyplnění může proběhnout úspěšně, i když se po odeslání nic neuloží. Proto po kliknutí nehledáme jen potvrzující zprávu, ale také konkrétní nový řádek a jeho údaje. Očekávání musí vycházet z test case. Když chceme prioritní požadavek, ověříme v jeho řádku právě vysokou prioritu. Příliš obecný text někde na stránce by mohl patřit jinému požadavku. Ukážeme si i neplatný formulář a řízenou chybu API. Zde je správným výsledkem chybová zpráva, nikoliv úspěšné uložení. Automatizovaný test proto nemusí vždy procházet jen bezchybnou uživatelskou cestou. Může potvrdit i správné zacházení s očekávanou chybou. Červený výsledek testu vzniká teprve tehdy, když se skutečné chování rozchází s tímto očekáváním.

## Scéna 06_01

Akce mění stav: fill nahradí obsah pole, click stiskne tlačítko, check zajistí zaškrtnutí a select_option vybere volbu ze selectu. Playwright před akcí ověřuje například viditelnost, stabilitu a dostupnost prvku. To je auto-waiting. Není třeba přidávat čekání v sekundách před každou akcí. Úspěšné kliknutí ale ještě neprokazuje, že server záznam uložil.

## Scéna 06_02

Assertion vyjadřuje očekávaný výsledek. to_be_visible ověřuje viditelnost, to_have_text celý text, to_contain_text část, to_have_value obsah pole, to_have_url adresu a to_have_count počet. Očekávaná hodnota pochází z test case. Skutečnou hodnotu zjišťuje Playwright z aplikace.

## Scéna 06_03

Teď v prohlížeči otevřeme výukové nástroje a záměrně zapneme simulaci chyby API. Portál zobrazí upozornění s kódem 503. I takový stav má svůj očekávaný výsledek: aplikace má chybu srozumitelně oznámit, místo aby působila jako úspěšně dokončená operace. V testu proto po kliknutí ověřujeme obsah chybového upozornění. Nesledujeme pouze to, zda se tlačítko podařilo stisknout. Stejný princip platí pro vytvoření a úpravu záznamu: po akci vždy výslovně kontrolujeme její požadovaný důsledek.

## Scéna 06_04

Pevný time.sleep(3) může být zbytečně dlouhý na rychlém počítači a krátký na pomalém. Web-first assertion čeká přímo na požadované chování. Okamžité assert locator.is_visible() nečeká opakovaně stejným způsobem; pro UI proto preferujte expect. Běžný Python assert je vhodný například pro status API.

## Scéna 06_05

Jako šestý úkol vytvořte požadavek s prioritou a zkontrolujte text Vysoká v jeho konkrétním řádku. Porovnejte své řešení s příkladem akcí v materiálech této lekce. Pro další práci už také máme připravený samostatný spouštěč run_failure, který zapíná úmyslně chybný test. Ten očekává neexistující nadpis, a proto má skončit červeně. Běžnou aplikaci kvůli této výukové chybě neměníme; podrobnou diagnostiku a opravu společně projdeme v desáté kapitole.

## Scéna 06_06

Při práci s formulářem máme několik různých okamžiků, které je vhodné rozlišovat. Nejprve se musí zpřístupnit ovládací prvek. Potom do něj test předá hodnotu nebo provede kliknutí. Následně může browser odeslat požadavek serveru a teprve po jeho zpracování se změna projeví v uživatelském rozhraní. Playwright nám pomáhá s připraveností samotné akce, ale očekávaný obchodní výsledek musíme popsat samostatně. U našeho nového požadavku proto nekončíme na stisku ukládacího tlačítka. Vyhledáme vzniklý řádek a zkontrolujeme údaje, které jsme do formuláře zadali. Pokud má být řešitelem Petr a požadavek má mít vysokou prioritu, ověříme právě tuto kombinaci u správného záznamu. Představte si závadu, při které se vždy uloží výchozí řešitel, přestože uživatel vybral jiného. Test kontrolující jen zelenou zprávu by mohl projít. Kontrola skutečného řádku tuto chybu odhalí. Podobně u úpravy sledujeme stav i po obnovení stránky. Tím si ověříme, že nejde jen o dočasně změněný text v browseru. Rozdíl je také mezi úplnou a částečnou shodou textu. U samostatné chybové zprávy obvykle očekáváme celý konkrétní text. U řádku tabulky, který obsahuje více buněk a akční tlačítka, často ověřujeme jednotlivé důležité části. Výběr příliš obecného očekávání může zbytečně oslabit celý scénář. Pokud například ověřujete jen slovo Nový někde na stránce, může být přítomné v tlačítku pro vytvoření dalšího záznamu. Takový úspěch by nic neříkal o stavu uloženého požadavku. U chybových scénářů přemýšlíme stejně. Neplatný formulář má zobrazit srozumitelnou chybu a nesmí přidat položku do seznamu. Obě podmínky dávají dohromady užitečný výsledek. Není potřeba odhadovat, kolik sekund bude aplikace zrovna potřebovat. Ověření čeká na konkrétní požadovaný stav. Pokud neprojde, nejprve zjistíme, zda byl správný předpoklad a správné očekávání. Pevné čekání přidané bez diagnózy by nás o tuto informaci připravilo a mohlo jen zakrýt skutečný problém.

## Scéna 06_07

Zkuste si při čtení testu vytvoření požadavku v duchu oddělit tři souvislé části. Nejprve připravíme uživatelský vstup, potom provedeme uložení a nakonec posoudíme výsledek. V první části kontrolujeme, že vyplňujeme správná pole. Ve druhé části očekáváme dokončení konkrétní akce. Třetí část už patří chování aplikace: vznikl správný záznam a mají jeho údaje očekávané hodnoty? Toto členění není důvodem zavádět složitou technickou vrstvu. Pomáhá hlavně při čtení a diagnostice. Pokud chybu ukazuje poslední ověření řešitele, víme, jaká hodnota byla předaná a kterého řádku se kontrola týká. Při změně zadání pak upravíme odpovídající vstup i očekávání vědomě. Nejde o náhodné přepisování textů podle posledního screenshotu, ale o udržování jasné vazby mezi testovacím scénářem a skutečným výsledkem aplikace.

# 07 · Projekt, fixtures a data

## Scéna 07_00

Přímý test je dobrý začátek. Jakmile máme několik scénářů, potřebujeme rozumět jejich společné přípravě. Otevřeme proto strukturu projektu a soubor, ve kterém pytest hledá naše fixtures. Jedna z nich připraví server. Jiná dodá stránku už přihlášeného uživatele. Každý test přesto dostane novou browser relaci a vlastní data. Nejde o sled funkcí, které se musejí spustit ve správném pořadí. Test úpravy si nepůjčuje záznam vytvořený předchozím testem. Kdyby jej potřeboval, při samostatném spuštění by selhal a výsledek by byl obtížně vysvětlitelný. U parametrizace naopak záměrně opakujeme stejný postup s různými vstupy. Na obrazovce jsou tři nesprávná hesla. Každé vytváří vlastní případ a vlastní výsledek. To nám pomáhá najít konkrétní problematická data, aniž bychom třikrát opisovali stejnou funkci. Nakonec uvidíte malý Page Object. Je to volitelný způsob, jak sdružit opakované akce stránky. Nepotřebujeme jej používat všude. Přidává smysl tam, kde skutečně zjednoduší čtení a údržbu. Účel testu a jeho očekávání musí zůstat dobře viditelné.

## Scéna 07_01

pytest běžně vyhledává soubory s předponou test_ a v nich stejně pojmenované testovací funkce. Soubor conftest.py umožňuje sdílet přípravu testů bez opakovaného ručního importu. Takové pojmenované přípravě a případnému úklidu říkáme fixture. Její scope určuje, jak dlouho připravený objekt žije. Funkční rozsah znamená novou instanci pro každý test, zatímco session rozsah sdílí jednu instanci v rámci celého běhu. Nejde tedy o libovolnou globální proměnnou.

## Scéna 07_02

Plugin dodává browser, context a page. Browser je běžící prohlížečový proces, BrowserContext oddělená relace cookies a úložišť, Page konkrétní karta. Naše base_url fixture spustí server a nakonec jej zavře. logged_in_page provádí přihlášení a ověří výchozí tři záznamy. Test tak začíná z jasného stavu.

## Scéna 07_03

Smoke je rychlé ověření základního provozu, regression širší opakovaná kontrola. Jsou to markery, tedy štítky; pytest -m smoke je výběr podle štítku. Všechny smoke scénáře jsou současně označené regression. Řízené selhání je z výchozího sběru vyřazené a vyžaduje --teaching-failure.

## Scéna 07_04

Parametrizace spustí stejný postup s různými daty: zobrazený výraz vytvoří dva případy. Každý dostane novou stránku a vlastní výsledek. Hesla v tomto kurzu jsou syntetická; skutečné tajné hodnoty do parametrů nepatří, protože se mohou objevit v názvu testu a reportu.

## Scéna 07_05

Nyní se díváme na jednoduchý Page Object v souboru login_page.py. Sdružuje související lokátory a opakované přihlašovací akce na jednom místě. Tuto abstrakci zavádíme až teď, když už umíme stejný test přečíst přímo přes page. Pomáhá tehdy, když omezuje skutečné opakování. Pokud by naopak zakrývala účel několika jednoduchých kroků, není důvod ji do prvního testu přidávat.

## Scéna 07_06

V sedmém úkolu přidejte do parametrizovaného řešení další syntetické chybné heslo. Po spuštění zkontrolujte, že přibyl právě jeden testovací případ a všechny očekávané chybové zprávy stále odpovídají zadání. Potom zkuste regresi také v opačném pořadí pomocí přepínače --reverse-order. Každý test musí mít vlastní správný výchozí stav a nesmí očekávat, že potřebná data připravil některý předchozí test.

## Scéna 07_07

U společné přípravy testů je důležité vědět, co se sdílí a co naopak vzniká znovu. Běžící proces prohlížeče můžeme v rámci jedné sady používat společně, protože jeho spuštění něco stojí. To ale neznamená společné přihlášení nebo společná data všech testů. Browser context představuje oddělenou relaci s vlastními cookies a úložišti. Uvnitř této relace máme konkrétní kartu stránky. V našem projektu dostává každý test čerstvou relaci, takže si nepředává vedlejší účinky. Fixture přihlášené stránky pak zajišťuje známý uživatelský stav pro ty případy, které ho potřebují. Test samotného přihlašovacího formuláře ji přirozeně nepoužívá, protože by tím přeskočil právě oblast, kterou chce kontrolovat. Když se podíváte na argumenty funkce, zjistíte tak mnohé o jejích předpokladech ještě před čtením jednotlivých kroků. Příprava má také svůj úklid. Po ukončení sady se zavírá lokální server a po testu jeho browser context. To je důvod, proč nechceme v každé funkci ručně zakládat další browser a zapomínat ho uzavřít. Společná pravidla držíme na jednom místě a jednotlivé scénáře se mohou soustředit na uživatelské chování. Podobně pracujeme s testovacími daty. Veřejný syntetický účet má v projektu své jasné místo. Když se má změnit, nemusíme procházet desítky opisovaných řetězců. U skutečných přihlašovacích údajů bychom navíc nepoužili sdílený zdrojový soubor, ale schválenou správu tajemství. Parametrizace pak pomáhá tam, kde máme stejnou cestu a více smysluplných vstupů. Každé chybné heslo vytvoří samostatný výsledek, takže poznáme, která kombinace selhala. Není ale cílem vytvořit dlouhý seznam náhodných hodnot jen kvůli počtu případů. Vybíráme data, která reprezentují rozdílné situace. Také při zavádění Page Objectu sledujte skutečný přínos. Pokud objekt pouze schová dvě jednoduché akce a čtenáře nutí přeskakovat mezi mnoha soubory, nemusí začátečníkovi pomoci. Jestli ale soustředí opakované lokátory a dobře pojmenované kroky jedné stránky, může údržbu výrazně zpřehlednit. Je užitečné umět číst obě varianty a rozhodnout se podle konkrétní sady, nikoliv podle představy, že každý testovací projekt musí mít co nejsložitější strukturu.

## Scéna 07_08

V našem projektu lze nezávislost ověřit i prakticky opačným pořadím případů. Pokud by test úpravy potřeboval záznam vytvořený jinou funkcí, tato skrytá vazba by se při jiném pořadí nebo samostatném spuštění rychle projevila. Testům proto nestačí pouze jednou projít v předem daném seznamu. Potřebují vlastní přípravu a srozumitelnou strategii dat. To neznamená, že každá hodnota musí být náhodná. U izolované relace jsou stálé syntetické názvy často přehlednější a snadněji se hledají v reportu. Náhodnost má smysl teprve tehdy, když řeší konkrétní problém a stále lze zpětně zjistit použité vstupy. Při přidávání další fixture se také ptejte, komu slouží a jak dlouho její stav žije. Díky tomu si zachováte čitelný projekt, ve kterém příprava pomáhá jednotlivým testům místo toho, aby mezi nimi vytvářela další neviditelné závislosti.

# 08 · Celá regresní cesta

## Scéna 08_00

V předchozích částech jsme jednotlivé schopnosti zkoušeli odděleně. Teď je spojíme do jedné skutečné regresní cesty. Začínáme přihlášením. Použijeme známý syntetický účet a počkáme na zobrazení přehledu. Vytvoříme nový syntetický požadavek. Vyplníme jeho údaje a po uložení ověříme, že má stav Nový. Potom otevřeme právě jeho úpravu. Změníme stav na Hotový a zkontrolujeme uložený výsledek. Nakonec požadavek smažeme. Jeho odstranění potvrdíme v dialogu a ověříme, že řádek zmizel. Potom se odhlásíme. Zkusíme ještě otevřít chráněnou stránku a zkontrolujeme návrat k přihlášení. Všimněte si, že celá tato cesta patří do jedné testovací funkce. Je tak jasné, které kroky spolu souvisejí. Současně máme i menší samostatné testy vytvoření, úpravy a mazání, které při závadě rychleji ukážou postiženou oblast. Delší cesta ověřuje jejich propojení. Zvláštní pozornost věnujeme potvrzovacímu dialogu. Reakci na něj připravujeme před kliknutím na smazání, aby test nezůstal čekat na odpověď. Poslední kontrola přístupu po odhlášení je stejně důležitá jako první úspěšné přihlášení. Nestačí pouze zmizení tlačítka nebo změna nadpisu; potřebujeme ověřit skutečné ukončení přihlášené relace.

## Scéna 08_01

Samostatné testy rychle ukazují, která oblast přestala fungovat. Jeden delší test navíc ověří propojení kroků. Naším scénářem je přihlášení, vytvoření požadavku, ověření výchozího stavu, dokončení, odstranění a odhlášení. Nejde o závislost mezi několika testy: celá cesta je v jedné funkci.

## Scéna 08_02

Podívejme se na kompletní regresní cestu v souboru test_records.py. Fixture logged_in_page nám připraví přihlášenou stránku. Test potom otevře Záznamy a vytvoří požadavek se stálým syntetickým názvem. Náhodný čas do něj přidávat nemusíme, protože každá relace má vlastní data. Proměnná row uchovává lokátor, který při dalším použití vyhledá aktuální řádek. Díky tomu se po úpravě neopíráme o zastaralou kopii HTML prvku.

## Scéna 08_03

Po uložení kontrolujeme Nový a po změně Hotový. Před smazáním připravujeme obsluhu dialogu. Nativní confirm blokuje stránku, dokud jej test nepřijme nebo nezamítne. Posluchač proto registrujeme před kliknutím, nikoliv až po něm. Potom ověřujeme nulový počet odpovídajících řádků a návrat na přihlášení.

## Scéna 08_04

Reset výchozích dat v portálu mění pouze aktuální relaci. Test test_reset_is_private_to_current_session otevírá dvě oddělené relace a ověřuje, že reset jedné nevrátí změny druhé. To je skutečný důkaz izolace. Čistota celé sady se nesmí opírat jen o spouštění vždy ve stejném pořadí.

## Scéna 08_05

V osmém úkolu spusťte právě tuto kompletní cestu jako jeden konkrétní test. Pro pozorování můžete použít viditelný prohlížeč a zpomalení akcí. Potom v pracovní kopii změňte řešitele na Petra a doplňte kontrolu příslušného řádku. Základní referencí je předvedený regresní test; rozšíření najdete také mezi řešeními osmé lekce. Znovu ověřte celou cestu včetně odstranění a odhlášení, aby změna jednoho údaje nenarušila ostatní očekávání.

## Scéna 08_06

Při delším regresním scénáři si předem určeme, na kterých místech potřebujeme získat důkaz správného chování. Kdybychom jen rychle prošli přihlášení, vytvoření, úpravu a smazání, mohli bychom přehlédnout chybu v prostředním kroku. Po vytvoření proto zkontrolujeme, že požadavek opravdu existuje s výchozím stavem. Po úpravě ověříme nový stav u stejného záznamu. Teprve potom přejdeme k odstranění. Tím zároveň získáme srozumitelnější místo selhání. Když se po uložení neobjeví očekávaný řádek, test skončí tam, kde vznikl problém, místo aby později neurčitě hlásil, že nejde najít tlačítko pro smazání. Náš syntetický název je záměrně stálý. V izolované relaci nepotřebujeme náhodné časové přípony, abychom se vyhnuli cizím datům. Díky tomu lze výsledek snadno porovnat mezi opakovanými běhy. U skutečné sdílené aplikace by strategie dat mohla být jiná a musela by odpovídat jejím pravidlům. Základní princip ale zůstává: test nesmí omylem měnit záznam jiného uživatele. Potvrzovací dialog dobře ukazuje rozdíl mezi viditelným HTML formulářem a nativním browser dialogem. Formulář v modálním okně stále najdeme běžnými lokátory stránky. Nativní potvrzení mazání má vlastní událost a jeho obsluhu připravíme před akcí. Můžeme je přijmout nebo zamítnout. Obě větve mají své očekávání: při potvrzení záznam zmizí, při zamítnutí musí zůstat zachovaný. U komplexní cesty používáme potvrzení, v samostatném menším testu kontrolujeme i zamítnutí. Na konci nezapomeneme na odhlášení. Návrat na přihlašovací stránku je první kontrola, ale ještě se pokusíme znovu otevřít chráněnou část. Pokud by se stále zobrazovala, samotné přesměrování po stisku odhlašovacího tlačítka by nestačilo jako důkaz ukončené relace. Až si budete vytvářet vlastní delší scénář, rozepište si podobná kontrolní místa nejprve do manuálního test case. Potom se rozhodněte, která patří do jedné propojené cesty a která dávají smysl také samostatně. Výsledkem bude sada, která ověří důležitou návaznost kroků, ale současně vám při chybě pomůže rychle najít konkrétní postiženou oblast.

## Scéna 08_07

Po dokončení delší cesty se vrátíme k jejímu účelu. Nepotřebovali jsme prokázat jen existenci jednotlivých tlačítek. Chtěli jsme ověřit, že na sebe přihlášení, práce s požadavkem a odhlášení správně navazují. Každý mezivýsledek proto kontrolujeme dříve, než jej použije další krok. Když se požadavek nevytvoří, nepokračujeme předstíranou úpravou jiného řádku. Když se nezmění stav, neskrýváme to okamžitým smazáním. To je důvod, proč delší scénář stále potřebuje několik dobře umístěných očekávání. Přesto by neměl být jediným testem celé aplikace. Menší případy nám pomohou určit konkrétní oblast a propojená cesta ověří jejich souhru. Až budete rozhodovat, kolik podobných cest přidat, zvažte jejich přínos pro regresi i to, jak snadno z jejich selhání dokážete určit další krok diagnostiky.

# 09 · Codegen jako pomocník

## Scéna 09_00

Teď znáte základy potřebné k tomu, abyste mohli rozumně použít Codegen. Otevřeme skutečný generátor a provedeme několik akcí v našem lokálním portálu. V druhém okně bude postupně vznikat Python kód. Sledujte, jak vybrané pole a tlačítko odpovídají jednotlivým řádkům. Generátor může ušetřit čas při hledání lokátoru a prvním zápisu postupu. Neměl by ale být černou skříňkou. Před zařazením do regrese potřebujeme vědět, co přesně záznam ověřuje. Codegen umí přidat také některá očekávání, například viditelnost nebo text. Neurčuje však za nás obchodní význam výsledku. To, zda nový záznam musí mít správného řešitele nebo zůstat uložený po obnovení stránky, vyplývá z testovacího scénáře. Po záznamu proto kód přeneseme do pytest struktury. Použijeme projektová data a relativní adresu, aby test fungoval proti automaticky spuštěné aplikaci. Absolutní port z ručního nahrávání do stabilní sady nepatří. Upravený test nakonec skutečně spustíme. Úspěšné generování kódu samo o sobě není důkazem, že již máme samostatný a spolehlivý regresní test.

## Scéna 09_01

Codegen zaznamenává akce v prohlížeči a navrhuje lokátory. Umí také vložit některá ověření přes tlačítka pro viditelnost, text nebo hodnotu. Neurčuje však, které obchodní chování je důležité, zda data zůstala uložená a jak test izolovat. Záznam je výchozí materiál k úpravě a kontrole.

## Scéna 09_02

Teď už máme z Codegenu skutečně uložený původní draft a prohlížíme si ho v editoru. Vznikl z našich akcí v lokálním prohlížeči, takže obsahuje konkrétní vyplněné hodnoty i navigaci na nahrávanou adresu. Je užitečné ho uchovat v této původní podobě. Vedle něj si připravíme upravený test a postupně vysvětlíme každou změnu. Samotné zaznamenání přihlášení ještě nenahrazuje rozhodnutí, které chování a jakým očekáváním ověřujeme.

## Scéna 09_03

Vedle původního draftu teď čteme upravený referenční příklad. Připravený spouštěč Codegenu používá target python-pytest, aby výstup odpovídal našemu způsobu spouštění. Draft se záměrně nejmenuje s předponou test_, takže ho běžný sběr automaticky nezařadí. Před integrací nahradíme absolutní adresu lokálního dema relativní cestou /login, použijeme společná syntetická data a doplníme jasná očekávání. Prohlížeč v našich testech připravuje fixture; ruční vytváření nového browseru proto do každé testovací funkce nekopírujeme.

## Scéna 09_04

Upravený příklad teď ověřujeme skutečným spuštěním. Jde o ručně zpřehledněný referenční test, který má vlastní očekávání a používá testovací prostředí projektu. Původní export z Codegenu přitom zůstává zachovaný zvlášť. Díky tomu můžeme ukázat konkrétní cestu od nahraných akcí k udržovatelnému testu: oddělení dat, relativní navigaci a kontrolu požadovaného výsledku. Zelený běh potvrzuje funkčnost tohoto konkrétního příkladu, nikoli automaticky všech dalších scénářů.

## Scéna 09_05

Úkol 09: Nahrajte přihlášení a otevření stránky Záznamy. Přidejte ověření nadpisu a počtu tří datových řádků, přeneste kód do nové testovací funkce a spusťte ji proti automatickému demu. Úspěchem je samostatně spustitelný test, který projde i bez ručního portálu na portu 5000.

## Scéna 09_06

U nahraného kódu je dobré rozlišit, co jsme opravdu zaznamenali, a co teprve potřebujeme jako testeři doplnit. Generátor dobře vidí vyplnění formuláře a stisk tlačítka. Dokáže také navrhnout popis cílového prvku a některá ověření, která při záznamu sami vybereme. Nemá však naše zadání a nemůže za nás posoudit úplnost scénáře. Pokud jsme při nahrávání omylem otevřeli jiný řádek nebo zadali nesprávná data, vygenerovaný program může tuto chybu velmi spolehlivě opakovat. Proto nahrávku čteme se stejnou pozorností jako ručně napsaný test. Nejprve se podíváme na navigaci. Adresa ručně spuštěného portálu obsahuje jeho konkrétní port. Naše automatická sada si ale připravuje vlastní instanci, takže tuto část upravíme na relativní cestu. Potom projdeme vstupní data. Syntetický účet můžeme převzít ze společného modulu a význam nově vytvořeného požadavku pojmenovat přímo v testu. Následují lokátory. Pokud generátor našel stabilní roli a přístupné jméno, není nutné zápis měnit jen proto, že vznikl automaticky. Když je ovšem založený na pořadí více podobných prvků, zkusíme najít přesnější uživatelský význam. Nakonec se vrátíme k očekávanému výsledku. Ověříme nadpis přehledu, počet výchozích řádků nebo konkrétní uloženou hodnotu podle toho, co má scénář prokazovat. Všimněte si také toho, zda výstup odpovídá pytest stylu. V naší sadě používáme připravenou stránku z fixture, takže z každé nahrávky nepotřebujeme přebírat ruční založení a zavření browseru. Původní draft uchováme odděleně od upraveného testu. Má to praktický důvod: při výuce nebo revizi pak můžeme ukázat, které změny záznam proměnily v udržovatelnou kontrolu. Nejde o hodnocení, zda je automaticky vzniklý kód horší nebo lepší. Jde o to, zda po úpravě splňuje stejná pravidla jako zbytek projektu. Posledním krokem je skutečné samostatné spuštění. Teprve tím ověříme, že test nevyužívá cookies z nahrávacího okna, nepotřebuje ručně rozběhnuté demo a provádí právě ta očekávání, která jsme mu určili. Codegen nám tak šetří práci na začátku, zatímco rozhodování o kvalitě testu zůstává čitelné a pod naší kontrolou.

## Scéna 09_07

Při používání Codegenu si můžete vytvořit jednoduchý pracovní návyk. Nejprve proveďte krátkou známou cestu, potom nahrávání zastavte a vzniklý kód si přečtěte. Nesnažte se zachytit celou aplikaci do jednoho dlouhého záznamu. U menšího úseku lépe poznáte, zda každý řádek odpovídá vašemu záměru. Potom přidejte nebo ověřte assertions, upravte adresu a data a výsledek spusťte samostatně v projektu. Pokud se při přenosu objeví problém, máte stále k dispozici původní draft a víte, které změny jste provedli. Záznam tedy nenahrazuje porozumění, ale může výrazně urychlit jeho praktické uplatnění. Největší přínos získáte ve chvíli, kdy už dokážete posoudit jednoznačnost lokátoru a úplnost očekávání. Právě proto jsme generátor zařadili až po prvních ručně napsaných testech, nikoliv na úplný začátek kurzu.

# 10 · Selhání a diagnostika

## Scéna 10_00

Přichází část, která bývá při automatizaci nejcennější: rozpoznat příčinu skutečného selhání. Záměrně spustíme test s chybným očekáváním nadpisu. Terminál ukáže neúspěch a návratový kód bude nenulový. Nic z tohoto výstupu nepřepisujeme na úspěch. Místo toho si přečteme, co test hledal, a porovnáme to s aplikací. Nejprve použijeme screenshot, který ukazuje konečný stav. Potom otevřeme trace, kde uvidíme i cestu k tomuto stavu. Na neúspěšném kroku je hledaný lokátor, čekání a snapshot stránky. To umožní odlišit dvě situace: prvek vůbec nevznikl, nebo jsme jej popsali nesprávně. V našem výukovém příkladu říká zadání Přihlášení a aplikace tento nadpis skutečně má. Chybné je tedy očekávání testu. Opravíme je podle požadavku a spustíme opravenou verzi. Není správné mechanicky převzít jakýkoliv skutečný výsledek do očekávání. Kdyby se od požadavku odchylovala aplikace, závada by patřila jí. Pro ladění si ještě ukážeme Inspector a princip krokování. Následně se vrátíme k běžnému neinteraktivnímu běhu, aby regresi nic neblokovalo.

## Scéna 10_01

Před chvílí jsme spustili samostatnou výukovou chybu a teď si prohlížíme její zdroj. Test očekává nadpis, který aplikace podle zadání vůbec nemá zobrazit. Jeho neúspěch je proto záměrný a běžná regresní sada zůstává oddělená. Selhání budeme číst jako konkrétní informaci o nesplněném očekávání. Náhodně přidané čekání by zde nepomohlo, protože chybně očekávaný nadpis ani po delší době nevznikne.

## Scéna 10_02

V Trace Vieweru vybereme neúspěšné očekávání a porovnáme jeho hledaný text se skutečným obsahem stránky. Traceback nám pomohl najít soubor a řádek, zatímco call log ukazuje lokátor a průběh čekání. Screenshot zachycuje přihlašovací formulář; trace k němu přidává posloupnost akcí, snímky DOM a síťové události. Tento archiv otevíráme lokálně. Prohlídka tak spojuje chybový výsledek s konkrétním okamžikem, kdy se požadavek testu rozešel s aplikací.

## Scéna 10_03

V tomto případě je chyba v očekávání testu. Zadání i aplikace používají nadpis Přihlášení, zatímco výukový test požadoval jiný text. V opraveném příkladu proto nastavíme očekávání podle platného požadavku. Není to obecné pravidlo přepsat expected na cokoli, co právě ukazuje actual. Kdyby aplikace porušovala správné zadání, opravovali bychom aplikaci. Za chvíli opravený test spustíme a jeho zelený výsledek ponecháme oddělený od původního červeného důkazu.

## Scéna 10_04

Opravenou verzi teď skutečně spouštíme pomocí spouštěče run_fixed. Sledujeme nejen zelenou barvu, ale také dokončený běh a jeho samostatný report. Pokud bychom potřebovali další interaktivní diagnostiku, použijeme proměnnou PWDEBUG a Playwright Inspector, který otevřeme v následující ukázce. Přepínač pytest --debug má jiný účel: slouží k internímu logování pytest. Po ladění prostředí vrátíme do běžného stavu a do finálního testu nebudeme nechávat dočasnou pauzu.

## Scéna 10_05

Úkol 10: Najděte v trace první navigaci, poslední assertion a screenshot. Vysvětlete příčinu jednou větou. Spusťte opravu a srovnejte oba výsledky. Neoznačujte původní test za xfail jen proto, aby report vypadal zeleně.

## Scéna 10_06

Při červeném testu si položme několik otázek ve správném pořadí. Začal scénář ve správné aplikaci a ve správném stavu? Proběhl krok, který měl hledaný prvek zobrazit? Popisuje lokátor skutečně tento prvek? A odpovídá očekávání platnému požadavku? Teprve po těchto otázkách dává smysl měnit kód. Ve výukové závadě hledáme nadpis, který na přihlašovací stránce vůbec nemá být. Screenshot přitom ukazuje správné přihlášení. Call log obsahuje hledané jméno a informaci, že se požadovaný prvek nepodařilo najít. Už tyto důkazy napovídají, že problém nebude v rychlosti načítání. Delší čekání by pouze prodloužilo cestu ke stejnému výsledku. V Trace Vieweru si potom projdeme dění podrobněji. Vybereme navigaci a neúspěšné ověření, podíváme se na snapshot stránky a porovnáme ho s lokátorem. Je užitečné rozlišovat stav před akcí a po ní, protože konečný obrázek sám nemusí odhalit, co ke chybě vedlo. Síťové požadavky mohou například ukázat, že server vrátil chybový status, zatímco stránka ještě obsahuje stará data. V takové situaci by samotná přítomnost řádku nemusela být důkazem čerstvého správného načtení. Naše řízená chyba ale má jednodušší příčinu, a proto opravujeme pouze očekávané jméno nadpisu. Assertion zachováme. Nepřeskočíme ji podmínkou ani ji neoznačíme za očekávaný neúspěch jen proto, abychom měli zelený report. Po opravě spustíme nejprve konkrétní případ a potom podle rozsahu změny i příslušnou sadu. Starý červený výsledek si ponecháme odděleně od zeleného důkazu opravy. Pro kolegu je pak srozumitelné, jaká závada byla reprodukovaná a čím se ověřilo její odstranění. Inspector může pomoci při zkoušení lokátoru za běhu, ale do finální regresní funkce nepatří zapomenuté pozastavení. Automatická sada musí doběhnout i bez člověka u klávesnice. Dobrá diagnostika tedy není jen sbírka obrázků. Je to postup, kterým z konkrétního neúspěchu získáme vysvětlitelnou příčinu a po změně také ověřitelný výsledek. Tento návyk se vám bude hodit u chyb testu stejně jako u skutečných závad aplikace.

## Scéna 10_07

Před uzavřením nalezené chyby si ještě ověřte, že nová zelená kontrola opravdu provádí původní požadavek. Když assertion omylem odstraníte nebo upravíte výběr tak, že se test vůbec nespustí, může souhrn působit příznivě, ale důkaz opravy chybí. Porovnejte tedy název případu, jeho jednotlivé kroky i skutečný počet provedených testů. U výukové závady máme jednoduché srovnání: stejná přihlašovací stránka, stejný typ ověření a opravené očekávané jméno nadpisu. Screenshot a trace původního neúspěchu přitom zůstávají dostupné. Tento postup se dá použít i při hlášení skutečné vady vývojáři. Uveďte předpoklady, konkrétní akci, očekávání a skutečný výsledek. Diagnostické soubory pak doplní souvislosti, které by samotný krátký text nemusel zachytit. Díky tomu se z neúspěšného testu stane použitelný podklad pro další práci.

# 11 · Regresní výsledky a reporty

## Scéna 11_00

Jednotlivý test už umíme napsat i opravit. Při regresi ale předáváme výsledek celé vybrané sady. Spustíme ji proto znovu a přečteme skutečný souhrn. Nezůstávejme pouze u zelené barvy. Potřebujeme vědět, které případy byly vybrány, kolik jich proběhlo a zda některé nebyly vynechány. Potom otevřeme HTML report a najdeme stejná jména případů. Vedle něj vzniká JUnit XML pro automatické systémy. Obsahuje strojově čitelné výsledky, nikoliv jinou nezávislou sadu testů. Když sdílíte výsledek kolegovi, přidejte informaci o verzi aplikace, rozsahu a konkrétním běhu. Při selhání uchovejte i diagnostické soubory. Další běh může poslední report a výstupní složku přepsat. Důležitý incident proto archivujeme dříve, než spustíme další pokus. Ukážeme si také, jak stejné příkazy zapadají do CI pipeline. Lokální úspěch není potvrzením, že již funguje firemní Azure agent. Tam musíme zvlášť ověřit síť, oprávnění a publikování výsledků. V této ukázce zůstáváme u skutečně provedeného lokálního běhu a jeho doložitelných artefaktů.

## Scéna 11_01

Po skutečném dokončení regrese si otevíráme její HTML report. Ten je určen především člověku, zatímco JUnit XML obvykle zpracovává automatizační nebo CI nástroj. Oba výstupy mají popisovat tentýž konkrétní běh. Zkontrolujte jeho čas, zvolený rozsah a počet případů. Samotné slovo passed nestačí, pokud nevíme, co se spouštělo a proti jaké verzi aplikace. Právě tyto souvislosti umožňují výsledek srozumitelně předat kolegovi.

## Scéna 11_02

Passed znamená splněná očekávání; failed nesplněné očekávání či chybu testu; error problém přípravy/úklidu; skipped neprovedený scénář. Při spouštění jednoho testu mohou být ostatní deselected, tedy nevybrané. To se liší od jejich úspěšného provedení. Parametrizovaný scénář může tvořit více test cases.

## Scéna 11_03

Diagnostické artefakty vznikají při selhání v samostatné výstupní složce. Trace obvykle poskytne více souvislostí než jeden závěrečný screenshot. Diagnostické video přitom zachycuje obsah testovacího prohlížeče, nikoli celou pracovní stanici. Další běh může stejnou výstupní složku obnovit, proto si důležitý incident nejprve archivujeme společně s reportem. U souběžných běhů musí mít každý vlastní cesty pro HTML, JUnit i artefakty; jinak by se důkazy mohly přepsat.

## Scéna 11_04

Připravený Azure DevOps YAML ukazuje, jak mohou stejné projektové příkazy běžet na agentovi a jak se publikují výsledky z JUnit. Jde o ukázku konfigurace, nikoli o tvrzení, že pipeline skutečně proběhla ve vaší organizaci. Před firemním použitím ověříte schváleného agenta, přístup k závislostem a oprávnění k artefaktům. Tajné hodnoty patří do schválené správy tajemství, aby se nedostaly do sdíleného YAML souboru ani do výukových záznamů.

## Scéna 11_05

V jedenáctém úkolu spusťte jeden konkrétní test a vyhledejte ho v JUnit i v HTML reportu. Potom napište krátké hlášení: jakou verzi jste ověřovali, kterým příkazem, v jakém rozsahu a s jakým výsledkem. Přidejte odkaz na příslušné důkazy. Při porovnání s pracovním sešitem si zkontrolujte hlavně přesnost rozsahu. Výsledek jednoho vybraného případu nesmíte popsat jako úspěch celé regrese.

## Scéna 11_06

Když výsledek regrese předáváme dál, měl by z něj jiný člověk poznat, co se skutečně stalo. Nestačí napsat, že všechno prošlo, pokud byl spuštěný jen jeden soubor nebo úzký výběr podle názvu. Souhrn proto spojíme s konkrétním příkazem, verzí projektu a použitým prostředím. V HTML reportu zkontrolujeme jména případů a jejich výsledky. Parametrizovaný test může vytvořit více samostatných řádků, i když ve zdrojích vidíte jedinou funkci. Zároveň mohou některé případy zůstat nevybrané. Nevybraný test neproběhl, takže o jeho správnosti tento běh nic neříká. Stejně opatrně čteme přeskočené případy. Přeskočení může mít legitimní důvod, ale není totéž co úspěšné ověření chování. Pokud sada skončí chybou přípravy, podíváme se nejprve na fixture nebo prostředí. V takové situaci nemuselo být tělo konkrétního testu vůbec provedené. Tato rozlišení nám pomáhají vytvořit přesné hlášení pro tým. JUnit soubor obsahuje podobné výsledky ve strojově čitelné podobě, aby je mohl zpracovat například CI server. Není potřeba jej ručně upravovat. Kdyby se XML a HTML vztahovaly k jiným spuštěním, vznikl by zavádějící důkaz, proto je archivujeme společně. Při závadě přidáme také příslušný trace a screenshot. Další běh může běžnou výstupní složku znovu vytvořit, a tak důležitá diagnostika nesmí zůstat jedinou kopií posledního pokusu. V našem kurzu mají řízená chyba a opravený test oddělené názvy reportů i artefaktů. Díky tomu si je můžete porovnat bez toho, aby nový úspěch přepsal původní chybu. Při pozdějším zapojení do firemního CI budeme navíc řešit dostupnost testovací aplikace, oprávnění agenta a ochranu výsledků. Lokální úspěch tyto podmínky automaticky neprokazuje. Přesto je lokální sada důležitý první krok, protože stejné testovací příkazy už máme ověřené. Až budete psát závěrečnou zprávu, představte si kolegu, který kurz ani váš počítač neviděl. Měl by z ní pochopit rozsah, skutečný výsledek a místo, kde najde další důkazy. Takové předání je pro regresní rozhodování užitečnější než samotný obrázek zeleného terminálu bez souvislostí.

## Scéna 11_07

Při čtení reportu si zkuste vybrat jediný konkrétní případ a dohledat jej od začátku do konce. Nejprve najděte jeho funkci ve zdrojích, potom odpovídající výsledek v HTML a nakonec jeho zápis v JUnit souboru. Ověřte, že všechny informace patří ke stejnému běhu. Pokud test selhal, najděte také jeho vlastní diagnostické artefakty, nikoliv screenshot podobně pojmenovaného případu z jiného pokusu. Tato zdánlivě malá kontrola je velmi užitečná při sdílení výsledků v týmu. Brání tomu, abychom rozhodovali podle neaktuálních nebo zaměněných souborů. V dobře připravené regresi proto není důležitý jen samotný běh, ale i dohledatelnost jeho důkazů. Když víte, co bylo provedeno a kde jsou související výsledky, dokážete je předat dalšímu člověku bez dlouhého ústního vysvětlování.

# 12 · Váš samostatný test

## Scéna 12_00

Teď je řada na vás. Napíšete vlastní test vyhledávání, které nemá žádný výsledek. Nejprve si ručně potvrďte očekávané chování. Potom bez nahlížení do řešení vytvořte nový testovací soubor, přihlaste se připravenou fixture, vyplňte hledání a ověřte prázdný seznam i vysvětlující zprávu. Video si v tuto chvíli můžete zastavit. Když budete hotovi, porovnáme vaši verzi s referenčním řešením a skutečně ji spustíme. Není potřeba, aby se jmenovala úplně stejně. Důležité je, že samostatně provádí požadovanou cestu a má jasná očekávání. Potom ještě ukážeme bezpečný přechod na jinou schválenou aplikaci. Změna základní adresy není automatickým překladem našich demo scénářů do firemního systému. Ten má jiné formuláře, jiná data a jiná oprávnění. Proto začínáme oddělenou sadou a jednoduchou kontrolou dostupnosti. Přihlašovací údaje čteme z lokální konfigurace nebo schválené správy tajemství. Neukládáme je do testovacích souborů, videa ani veřejných reportů. Z kurzu si odneste pracovní postup: popsat chování, napsat kroky, ověřit výsledek, samostatně spustit test a při selhání nejprve hledat důkaz a příčinu. Na tom lze stavět další skutečnou regresní sadu.

## Scéna 12_01

Posledním samostatným úkolem bude vyhledávání bez výsledků. Nejdříve si ho proveďte ručně: přihlaste se a do vyhledávání zadejte text, který neodpovídá názvu žádného požadavku. Očekáváte prázdný seznam i srozumitelnou zprávu. Tyto kroky si nejprve zapište. Potom založte vlastní testovací soubor a postupně je převeďte do Playwrightu. Referenční řešení si ponechte až pro závěrečné porovnání, abyste si ověřili vlastní porozumění.

## Scéna 12_02

V testu můžete využít připravenou přihlášenou stránku, pole najít přes jeho label a doplnit dvě samostatná očekávání. Jedno ověří nulový počet datových řádků a druhé viditelnou zprávu Žádné odpovídající záznamy. Pevnou dvousekundovou pauzu nepotřebujete, protože expect čeká na požadovaný stav. Nejprve spusťte nový test samostatně a potom celou regresi. Až poté si porovnejte řešení dvanácté lekce a vysvětlete případné rozdíly.

## Scéna 12_03

Podívejme se ještě jednou na skutečné chování prázdného vyhledávání v prohlížeči. Začínáme se třemi výchozími požadavky a zadáme text, který žádnému z nich neodpovídá. Datové řádky zmizí a portál zobrazí zprávu Žádné odpovídající záznamy. Právě obě tyto změny má náš samostatný test ověřit. Pouhý nulový počet by totiž mohl doprovázet i chybné načtení stránky. Viditelná očekávaná zpráva nám pomáhá rozlišit správný prázdný výsledek od jiného problému.

## Scéna 12_04

Zkopírujte .env.example na .env, nastavte EXTERNAL_BASE_URL a spusťte python -m pytest tests_external --external projektovým interpreterem. Přihlašovací data čtěte pomocí os.environ["TEST_USERNAME"] a os.environ["TEST_PASSWORD"], nikoliv ze sdíleného souboru v repozitáři. Trace a videa mohou obsahovat i údaje z aplikace; určete jejich přístup a retenci.

## Scéna 12_05

Úkol 12: Nový vyhledávací test napište sami, spusťte jej samostatně i ve skupině a vysvětlete jeho omezení: ověřuje daný filtr, nikoliv celý vyhledávač. Potom absolvujte akceptační walkthrough. Pokud dokážete test napsat, spustit, rozpoznat jeho chybu a opravit ji podle požadavku, zvládli jste celý zamýšlený pracovní postup.

## Scéna 12_06

U samostatného úkolu zkuste odolat pokušení začít okamžitě kopírováním referenčního testu. Nejdříve si krátce popište, co uživatel provede a co po této akci očekává. V našem případě se přihlásí do známého výchozího stavu, vyhledá text, který neodpovídá žádnému požadavku, a dostane prázdný seznam se srozumitelnou zprávou. Už z tohoto popisu jsou vidět dvě různé kontroly. Nulový počet záznamů sám o sobě by mohl být důsledkem chyby načítání. Prázdná zpráva společně se správně dokončeným hledáním nám poskytuje přesnější informaci. Teprve potom vyberte lokátor vstupního pole a způsob ověření výsledku. Využijte to, co jste již viděli: popisek pro pole, konkrétní testovací identifikátor pro datové řádky a text pro prázdný stav. Není nutné přidávat novou abstrakci ani vymýšlet vlastní čekací mechanismus. Po napsání soubor uložte a spusťte samostatně. Když selže, přečtěte první relevantní místo ve svém kódu a ověřte předpoklady. Než začnete měnit několik věcí současně, zkuste jednou větou popsat, co přesně skutečnost nesplnila. Až případ projde, spusťte i širší sadu, abyste ověřili jeho začlenění. Při přechodu na jinou aplikaci uplatníte stejný postup, ale nikoliv stejná demo data a stejné názvy formulářů. Nový systém má vlastní přihlášení, oprávnění i pravidla pro práci se záznamy. Proto nejprve připravíme schválené prostředí a read-only kontrolu dostupnosti v oddělené sadě. Měnící scénáře doplníme až s jasnou strategií syntetických dat a úklidu. Přihlašovací tajemství nesmějí být součástí sdíleného kódu ani výukového videa. Myslete také na to, že screenshot nebo trace mohou zachytit obsah samotné aplikace, nejen vaše příkazy. Na konci kurzu tedy nemáte pouze seznam metod k zapamatování. Máte ověřený pracovní postup a projekt, ve kterém jej můžete opakovat. Dokážete popsat očekávání, najít prvek, provést akci, přečíst výsledek a při chybě hledat konkrétní důkaz. Právě tuto návaznost si ponechte i při rozšiřování vlastní regresní sady. Každý nový test by měl mít jasný důvod, známý výchozí stav a výsledek, který umíte srozumitelně vysvětlit dalšímu člověku.

## Scéna 12_07

Pokud jste samostatný vyhledávací test dokončili, zkuste jej ještě vysvětlit vlastními slovy bez pohledu do řešení. Měli byste umět pojmenovat výchozí stav, vybraný ovládací prvek, provedenou akci i obě důležité kontroly výsledku. Potom si představte jednoduchou změnu: vyhledávání vrátí jeden odpovídající požadavek. Kterou část vstupu upravíte a jaké nové očekávání bude dávat smysl? Taková otázka pomůže ověřit porozumění lépe než další opisování hotového souboru. Stejný způsob můžete použít při postupném rozšiřování sady o vlastní scénáře. Začněte známou cestou, změňte jeden významný předpoklad a vědomě určete její očekávaný výsledek. Díky tomu bude váš projekt růst po malých ověřených krocích a jednotlivé testy zůstanou srozumitelné i kolegovi, který je uvidí poprvé.
