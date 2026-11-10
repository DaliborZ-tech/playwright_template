"""Meaning-linked live actions for the complete course, never random visual movement."""

import argparse
import re

from prepare import HERE, ROOT, audio

PRACTICE = {
    1: [
        ("Když zadáte přihlašovací", "login", "Přihlášení syntetickým účtem a skutečný Dashboard"),
        (
            "Právě proto v naší první",
            "code:tests/smoke/test_login.py:Dashboard",
            "Výslovné očekávání nadpisu přehledu",
        ),
        (
            "Kdyby po kliknutí",
            "bad_login",
            "Samotné kliknutí nestačí: nesprávné heslo zobrazí chybu",
        ),
        ("Podobně je potřeba", "login_reset", "Známý výchozí stav, tři datové řádky"),
        ("Pokud si ručně vytvoříte", "create", "Ruční relace má nový čtvrtý požadavek"),
        (
            "Ruční prohlížeč má svá data",
            "code:tests/conftest.py:logged_in_page",
            "Fixture připraví vlastní přihlášenou stránku",
        ),
        (
            "Když jeden test záznam",
            "new_session",
            "Nová skutečná relace znovu obsahuje tři seed záznamy",
        ),
        (
            "Při výběru regresních",
            "code:tests/smoke/test_login.py:def test_01",
            "Krátký smoke případ s jasným očekáváním",
        ),
        ("Krátký úspěšný test", "run:smoke", "Skutečná smoke sada, čerstvý JUnit a exit code"),
        ("Současně si necháme", "search", "Ruční průzkum: vyhledání skutečného požadavku"),
        (
            "Až budete po kurzu",
            "code:training/exercises/WORKBOOK.md:01",
            "Vlastní úkol: předpoklad, akce, očekávání",
        ),
    ],
    2: [
        ("Kontrola verze", "run:version", "Skutečná verze projektového Pythonu"),
        ("Nejprve zvolíme správný", "interpreter", "Skutečná volba interpreteru VS Code"),
        ("Potom se podíváme", "code:requirements.lock:playwright", "Přesně uzamčené knihovny"),
        ("Složka s názvem", "run:pip_version", "pip patří do projektového .venv"),
        ("Přesné verze potřebných", "run:pip_check", "Skutečná kontrola konzistence závislostí"),
        ("Třetí částí", "run:playwright_version", "Verze Playwrightu a jeho browseru"),
        (
            "Doplníme pouze odpovídající",
            "run:browser_install",
            "Idempotentní instalace připraveného Chromia",
        ),
        (
            "Podobně postupujeme",
            "code:training/troubleshooting/windows.md:proxy",
            "Ověřený postup při potížích se sítí",
        ),
        ("V editoru pak", "interpreter", "Editor i terminál používají skutečné .venv"),
        ("Jakmile malá smoke", "run:smoke", "Skutečný smoke výsledek po kontrole prostředí"),
    ],
    3: [
        (
            "V ukázce máme",
            "write:training/solutions/test_03_python.py:return cleaned",
            "Funkce normalize skutečně vzniká v editoru",
        ),
        ("Původní hodnota", "run:python_values", "Skutečná vstupní a očištěná hodnota"),
        (
            "Funkce pak rozhodne",
            "code:training/solutions/test_03_python.py:if not",
            "Podmínka pro prázdný text",
        ),
        ("Pokud je text prázdný", "run:python_empty", "Prázdný vstup vrátí Bez názvu"),
        ("Pokud prázdný není", "run:python_values", "Neprázdný vstup vrátí očištěný název"),
        ("Když funkci zavoláme třikrát", "run:python_three", "Tři skutečné návratové hodnoty"),
        (
            "Všimněte si rozdílu",
            "write:training/solutions/test_03_python.py:test_synthetic_titles",
            "Definice a skutečné volání funkce",
        ),
        (
            "Najde je a zavolá pytest",
            "run:python",
            "pytest skutečně vyhledá a provede testovací funkci",
        ),
        (
            "Import na začátku",
            "code:tests/smoke/test_login.py:import",
            "Import připravuje jméno; není browser akcí",
        ),
        (
            "Dvojtečka za definicí",
            "code:training/solutions/test_03_python.py:def normalize",
            "Dvojtečka a skutečné odsazení těla",
        ),
        ("Pokud odsazení odstraníte", "syntax_break", "Skutečná změna odsazení v pracovní kopii"),
        ("Proto má smysl", "run:compile_bad", "Skutečný IndentationError před spuštěním browseru"),
        ("V běžném testu", "restore_python", "Opravené odsazení, zachovaný původní příklad"),
        ("Jakmile to dokážete", "run:python", "Opravený soubor opět skutečně projde"),
    ],
    5: [
        ("V prvním je jen", "login_form", "Skutečný přihlašovací formulář"),
        ("Pole mají jasné", "inspect_email", "Nativní DevTools ukazují skutečné pole E-mail"),
        ("Ve druhém rozhraní", "login_reset", "Tabulka a její skutečná tlačítka Upravit"),
        ("Test musí nejprve", "scope_row", "Výběr konkrétního datového řádku"),
        ("Lokátor není jednou", "reload", "Překreslení stránky a znovuvyhodnocený lokátor"),
        ("Kdyby názvy dvou", "duplicate_record", "Dva syntetické názvy obsahují stejný podřetězec"),
        ("V takové situaci", "scope_exact", "Zpřesnění oblasti na konkrétní požadavek"),
        ("U počítání položek", "login_reset", "Tři výchozí datové řádky"),
        ("Pozor také na hlavičku", "inspect_header", "Skutečná hlavička má také roli row"),
        (
            "Právě proto máme",
            "write:training/solutions/test_05_locators.py:to_have_count(3)",
            "Test ID vybírá jen datové řádky",
        ),
        ("Při hledání vhodného", "inspect_row", "Skutečný datový řádek v DevTools"),
        ("Stabilita neznamená", "run:locators", "Lokátory projdou nad skutečnou aplikací"),
    ],
    6: [
        ("Nejprve se musí", "new_form", "Zpřístupněný skutečný formulář"),
        ("Potom do něj", "fill_record", "Zadaný název, Petr a vysoká priorita"),
        ("Následně může browser", "save_record", "Skutečně uložený čtvrtý řádek"),
        (
            "U našeho nového",
            "code:tests/regression/test_records.py:def test_05",
            "Test nekončí samotným kliknutím",
        ),
        ("Pokud má být řešitelem", "scope_created", "Skutečný uložený Petr a vysoká priorita"),
        (
            "Kontrola skutečného řádku",
            "write:tests/regression/test_records.py:to_have_count(4)",
            "Očekávání se vážou na vytvořený řádek",
        ),
        ("Podobně u úpravy", "update_reload", "Hotový stav přetrvá i po načtení stránky"),
        (
            "Rozdíl je také",
            "code:tests/regression/test_records.py:to_contain_text",
            "Částečná shoda obsahu konkrétního řádku",
        ),
        ("U chybových scénářů", "invalid_form", "Neplatný formulář zobrazí chybu a nic nevytvoří"),
        ("Není potřeba odhadovat", "api_error", "Skutečná chyba API a cílené očekávání alertu"),
        ("Pokud neprojde", "recover", "Načíst znovu obnoví seznam i bez sleep"),
    ],
    7: [
        ("Browser context představuje", "new_session", "Nová skutečná browser relace a seed data"),
        (
            "Fixture přihlášené",
            "code:tests/conftest.py:def logged_in_page",
            "Přihlášení je příprava pro konkrétní testy",
        ),
        (
            "Test samotného přihlašovacího",
            "code:tests/smoke/test_login.py:def test_01",
            "Nepřihlášená fixture page v testu formuláře",
        ),
        ("Příprava má také", "code:tests/conftest.py:yield", "yield a skutečný úklid serveru"),
        (
            "Podobně pracujeme",
            "code:test_data/users.py:DEMO_EMAIL",
            "Jediné místo veřejných syntetických dat",
        ),
        (
            "Parametrizace pak pomáhá",
            "write:training/solutions/test_07_parametrize.py:parametrize",
            "Tři smysluplné vstupy se skutečně zapisují",
        ),
        ("Každé chybné heslo", "run:parametrize", "Tři samostatné skutečné výsledky"),
        (
            "Také při zavádění Page Objectu",
            "code:pages/login_page.py:class LoginPage",
            "Opakované lokátory v jednoduché třídě",
        ),
        ("Jestli ale soustředí", "code:pages/login_page.py:def login", "Pojmenované kroky stránky"),
    ],
    8: [
        ("Po vytvoření proto", "create", "Existující nový požadavek a výchozí stav"),
        ("Po úpravě ověříme", "update_reload", "Stejný záznam se stavem Hotový"),
        ("Teprve potom", "delete_record", "Potvrzené smazání konkrétního záznamu"),
        (
            "Náš syntetický název",
            "code:tests/regression/test_records.py:Regresní požadavek",
            "Stálý název v izolovaném testu",
        ),
        ("Potvrzovací dialog", "create", "Příprava skutečného záznamu pro dialog"),
        ("Nativní potvrzení", "cancel_delete", "Skutečné zamítnutí browser dialogu zachová řádek"),
        ("U komplexní cesty", "delete_record", "Skutečné potvrzení stejného browser dialogu"),
        ("Na konci nezapomeneme", "logout", "Odhlášení a skutečně nepřístupná chráněná stránka"),
        (
            "Až si budete vytvářet",
            "code:tests/regression/test_records.py:def test_12",
            "Propojená regresní cesta ve skutečném kódu",
        ),
        ("Výsledkem bude sada", "run:journey", "Čerstvý skutečný výsledek celé cesty"),
    ],
    9: [
        (
            "Nejprve se podíváme na navigaci",
            "codegen_source",
            "Skutečně vygenerovaná navigace má konkrétní port",
        ),
        (
            "Potom projdeme vstupní",
            "code:test_data/users.py:DEMO_EMAIL",
            "Veřejný účet je ve společném modulu",
        ),
        (
            "Následují lokátory",
            "write:training/solutions/test_09_codegen_refined.py:get_by_label",
            "Čitelný lokátor v upraveném testu",
        ),
        (
            "Nakonec se vrátíme",
            "write:training/solutions/test_09_codegen_refined.py:expect",
            "Vlastní očekávání nejsou pouhý záznam klikání",
        ),
        (
            "Všimněte si také",
            "code:training/solutions/test_09_codegen_refined.py:def test",
            "Skutečný pytest styl s fixture page",
        ),
        ("Původní draft uchováme", "codegen_source", "Originální export se zachovaným SHA"),
        ("Posledním krokem", "run:refined", "Skutečný samostatný běh upraveného testu"),
    ],
    10: [
        (
            "Ve výukové závadě",
            "code:tests/teaching/test_expected_failure.py:Neexistující",
            "Chybné jméno nadpisu v konkrétní assertion",
        ),
        (
            "Screenshot přitom",
            "failure_screenshot",
            "Skutečný screenshot zachovaný z červeného běhu",
        ),
        ("Call log obsahuje", "trace", "Skutečný neúspěšný expect v Trace Vieweru"),
        ("V Trace Vieweru", "trace", "Historický snapshot skutečné chyby"),
        ("Vybereme navigaci", "trace_navigation", "Navigace skutečného záznamu trace"),
        ("Je užitečné rozlišovat", "trace_snapshot", "Snapshot před a po skutečné akci"),
        (
            "Naše řízená chyba",
            "write:training/solutions/test_10_fixed.py:Přihlášení",
            "Opravené očekávání podle zadání",
        ),
        ("Po opravě spustíme", "run:fixed", "Skutečný GREEN vedle zachovaného RED"),
        ("Starý červený výsledek", "report_failure", "Oddělený skutečný červený HTML report"),
        ("Inspector může pomoci", "debug", "Nativní Inspector a skutečný uživatelský kód"),
    ],
    11: [
        (
            "Souhrn proto spojíme",
            "code:docs/azure-pipelines.yml:pytest",
            "Stejný ověřený příkaz v budoucím CI",
        ),
        ("V HTML reportu", "report", "Čerstvý report posledního skutečného běhu"),
        ("Parametrizovaný test", "run:parametrize", "Tři výsledky z jediné funkce"),
        ("Zároveň mohou", "run:selected", "Výběr pouze jednoho konkrétního testu"),
        ("JUnit soubor obsahuje", "junit", "Skutečný JUnit stejného běhu"),
        ("Kdyby se XML", "report", "HTML a JUnit pocházejí ze stejné složky běhu"),
        ("V našem kurzu", "report_failure", "Zachovaný RED se nepřepisuje GREEN během"),
        (
            "Při pozdějším zapojení",
            "code:docs/azure-pipelines.yml:PublishTestResults",
            "Ukázka publikace JUnit v YAML",
        ),
        ("Až budete psát závěrečnou", "run:regression", "Čerstvý přehled skutečně vybrané regrese"),
    ],
    12: [
        (
            "Nejdříve si krátce",
            "code:training/exercises/WORKBOOK.md:12",
            "Samostatné zadání je vidět před řešením",
        ),
        ("V našem případě", "empty_search", "Skutečné prázdné vyhledávání"),
        ("Už z tohoto", "scope_empty", "Nula datových řádků a viditelná prázdná zpráva"),
        (
            "Teprve potom",
            "write:training/solutions/test_12_search.py:fill",
            "Vlastní test vzniká ze známého předpokladu",
        ),
        (
            "Využijte to",
            "write:training/solutions/test_12_search.py:to_be_visible",
            "Dvě konkrétní očekávání",
        ),
        ("Po napsání soubor", "run:search", "Skutečný samostatný běh uloženého testu"),
        ("Až případ projde", "run:regression", "Skutečná širší sada po cíleném ověření"),
        (
            "Při přechodu na jinou",
            "code:.env.example:EXTERNAL",
            "Oddělená firemní konfigurace s prázdnými tajemstvími",
        ),
        (
            "Proto nejprve připravíme",
            "code:tests_external/test_availability.py:def test",
            "Read-only kontrola v oddělené sadě",
        ),
        (
            "Na konci kurzu",
            "code:training/cheatsheets/playwright-python.md:expect",
            "Souhrn skutečně použitého pracovního postupu",
        ),
    ],
}

SCENES = {
    "01_07": [
        (
            "Na obrazovce se ještě jednou",
            "code:tests/smoke/test_login.py:def test",
            "Funkce odpovídá jednomu manuálnímu případu",
        ),
        (
            "Otevření stránky",
            "code:tests/smoke/test_login.py:page.goto(",
            "Manuální akce → page.goto",
        ),
        (
            "Kdybychom tento poslední",
            "code:tests/smoke/test_login.py:expect(",
            "Očekávání nadpisu je důkazem správné stránky",
        ),
        ("Zelený výsledek", "report", "Čerstvý výsledek se vztahuje ke konkrétním očekáváním"),
        (
            "Při automatizaci obvykle",
            "case_note:expected",
            "Předpoklad → akce → očekávaný výsledek",
        ),
        (
            "Zápis v Pythonu",
            "code:tests/smoke/test_login.py:expect(",
            "Stejné očekávání převedené do Pythonu",
        ),
        (
            "Díky tomu budete",
            "code:tests/smoke/test_login.py:to_be_visible",
            "Viditelný nadpis: konkrétní důkaz splněného požadavku",
        ),
    ],
    "01_00": [
        ("Vítejte", "login_form", "Živý lokální portál a cíl kurzu"),
        ("Nejdříve se přihlásíme", "login", "Ukázka cílové cesty: skutečné přihlášení"),
        ("pak vytvoříme záznam", "create", "Ukázka cílové cesty: vznikl skutečný záznam"),
        ("změníme stav", "update_reload", "Ukázka cílové cesty: uložená změna stavu"),
        ("záznam odstraníme", "delete_record", "Ukázka cílové cesty: potvrzené smazání"),
        (
            "Když narazíte na nový pojem",
            "code:tests/smoke/test_login.py:goto",
            "Krok a konkrétní očekávání ve skutečném testu",
        ),
        ("Na obrazovce používáme", "login_form", "Skutečný lokální formulář a syntetická data"),
        ("Podívejte se na připravený", "login_reset", "Tři výchozí požadavky, řešitelé a stavy"),
        (
            "Za chvíli stejný",
            "code:tests/conftest.py:def logged_in_page",
            "Stejný přehled otevírá také připravená fixture",
        ),
        ("Když člověk klikne", "create", "Uložení a skutečný nový řádek"),
        (
            "Tuto kontrolu mu napíšeme",
            "code:tests/regression/test_records.py:to_have_count(4)",
            "Očekávání výslovně kontroluje čtvrtý řádek",
        ),
    ],
    "01_03": [
        (
            "Při ručním průzkumu",
            "code:scripts/start_demo.cmd:demo",
            "Skutečný spouštěč lokální aplikace",
        ),
        ("V prohlížeči otevřeme", "login", "Ruční přihlášení do spuštěného portálu"),
        ("Na stránce Záznamy", "create", "Ruční relace má vlastní nový požadavek"),
        ("Automatickou sadu potom", "run:regression", "Skutečné spuštění regresní sady"),
        (
            "Ta si připraví vlastní",
            "code:tests/conftest.py:make_server",
            "Automatický server a relace jsou oddělené",
        ),
    ],
    "01_05": [
        ("Teď si video", "case_note:precondition", "Předpoklad vlastního manuálního případu"),
        ("Potom v zobrazeném", "case_note:action", "Konkrétní akce otevření stránky"),
        ("Pro porovnání", "case_note:expected", "Očekávaný viditelný nadpis"),
        (
            "Úkol je hotový",
            "code:training/solutions/test_01_open.py:expect",
            "Porovnání s příkladem až po zadání úkolu",
        ),
    ],
    "02_00": [
        ("Teď si připravíme", "run:version", "Skutečná verze projektového Pythonu"),
        (
            "Projekt si můžete",
            "code:docs/INSTALL_WINDOWS.md:venv",
            "Instalační postup a oddělené prostředí",
        ),
        ("V připraveném instalačním", "run:setup", "Skutečný idempotentní instalační spouštěč"),
        ("Objeví se až", "run:pip_check", "Kontrola skutečně nainstalovaných závislostí"),
        (
            "Při prvním vzniká",
            "code:scripts/bootstrap.py:venv",
            "Vytvoření a opětovné použití prostředí",
        ),
        (
            "Při použití firemní",
            "code:training/troubleshooting/windows.md:proxy",
            "Doporučený postup při potížích s proxy",
        ),
        ("Jakmile instalace projde", "run:smoke", "Skutečný malý test po instalaci"),
    ],
    "02_04": [
        ("Po instalaci", "run:smoke", "Skutečný smoke běh"),
        ("Pokud chceme kroky", "run:visible", "Skutečný headed běh se slowmo"),
        (
            "Parametr slowmo",
            "code:scripts/manage.py:slowmo",
            "Zpomalení pro sledování nenahrazuje očekávání",
        ),
    ],
    "05_00": [
        ("Test už umí", "login_form", "Otevřený skutečný přihlašovací formulář"),
        ("Tomuto popisu říkáme", "inspect_email", "Lokátor a skutečný HTML prvek v DevTools"),
        (
            "Proto začínáme významem",
            "code:training/solutions/test_05_locators.py:get_by_role",
            "Role a přístupný název",
        ),
        ("U formulářového pole", "inspect_email", "Popisek skutečně odpovídá poli E-mail"),
        ("Ukážeme si přihlášení", "login_reset", "Tabulka po skutečném přihlášení"),
        ("Tester potřebuje určit", "scope_row", "Vymezený konkrétní požadavek"),
        (
            "Když popis odpovídá",
            "duplicate_record",
            "Skutečný druhý záznam se společným podřetězcem",
        ),
        ("U počtu řádků", "login_reset", "Návrat ke třem výchozím datovým řádkům"),
        ("Stejný lokátor tedy", "inspect_header", "Hlavička a datové řádky mají odlišný účel"),
    ],
    "05_03": [
        ("Pokud lokátor", "scope_row", "Oblast konkrétního záznamu"),
        ("Nejprve omezte oblast", "scope_exact", "Přesný výběr namísto náhodné první shody"),
        (
            "to_have_count",
            "code:training/solutions/test_05_locators.py:to_have_count",
            "Počet pracuje s více prvky záměrně",
        ),
    ],
    "06_00": [
        ("Teď už umíme", "login_reset", "Známý výchozí stav"),
        ("Otevřeme nový požadavek", "new_form", "Skutečný otevřený formulář"),
        ("vyplníme název", "fill_record", "Vyplněný název, řešitel Petr a priorita"),
        ("Potom formulář uložíme", "save_record", "Nový záznam skutečně přibyl"),
        ("Proto po kliknutí", "scope_created", "Konkrétní uložený řádek a jeho údaje"),
        (
            "Očekávání musí vycházet",
            "code:tests/regression/test_records.py:to_contain_text",
            "Konkrétní očekávání podle scénáře",
        ),
        ("Ukážeme si i neplatný", "invalid_form", "Skutečná validace neplatného názvu"),
        ("Zde je správným výsledkem", "api_error", "Očekávané upozornění při chybě API"),
        (
            "Červený výsledek",
            "code:tests/regression/test_records.py:503",
            "Chybový stav aplikace může být úspěšný test",
        ),
    ],
    "06_03": [
        ("Teď v prohlížeči", "api_error", "Skutečná simulace API 503"),
        (
            "V testu proto",
            "code:tests/regression/test_records.py:to_have_text",
            "Kontrola skutečného obsahu alertu",
        ),
        ("Stejný princip", "recover", "Skutečné obnovení seznamu"),
    ],
    "08_00": [
        ("V předchozích", "login_form", "Začátek propojené regresní cesty"),
        ("Začínáme přihlášením", "login_reset", "Skutečný Dashboard a seed data"),
        ("Vytvoříme nový syntetický", "create", "Vznikl skutečný regresní požadavek"),
        ("Změníme stav na Hotový", "update_reload", "Uložený Hotový stav stejného záznamu"),
        ("Nakonec požadavek smažeme", "delete_record", "Skutečný potvrzovací dialog a odstranění"),
        ("Potom se odhlásíme", "logout", "Ochrana záznamů po odhlášení"),
        (
            "Všimněte si, že celá",
            "code:tests/regression/test_records.py:def test_12",
            "Propojené kroky v jedné funkci",
        ),
        (
            "Současně máme i menší",
            "code:tests/regression/test_records.py:def test_05",
            "Samostatný test vytvoření",
        ),
        (
            "Zvláštní pozornost",
            "code:tests/regression/test_records.py:page.once",
            "Obsluha dialogu před akcí",
        ),
        (
            "Poslední kontrola přístupu",
            'code:tests/regression/test_records.py:page.goto("/records")',
            "Ověření chráněné cesty po odhlášení",
        ),
    ],
    "09_00": [
        ("Teď znáte", "codegen_record", "Skutečný Codegen a nahrané přihlášení"),
        (
            "V druhém okně",
            "codegen_inspect",
            "Nativní Inspector ukazuje skutečně vzniklý Python kód",
        ),
        ("Codegen umí přidat", "codegen_inspect", "Nástroje pro očekávání v nativním Inspectoru"),
        ("Po záznamu proto", "codegen_source", "Skutečný originální export"),
        (
            "Použijeme projektová data",
            "code:training/solutions/test_09_codegen_refined.py:DEMO_EMAIL",
            "Upravený pytest příklad a veřejná data",
        ),
        ("Upravený test nakonec", "run:refined", "Skutečný samostatný běh upraveného testu"),
    ],
    "10_00": [
        ("Přichází část", "run:failure", "Skutečné řízené selhání"),
        (
            "Místo toho",
            "code:tests/teaching/test_expected_failure.py:Neexistující",
            "Co test opravdu hledal",
        ),
        (
            "Nejprve použijeme screenshot",
            "failure_screenshot",
            "Skutečný screenshot právě tohoto selhání",
        ),
        ("Potom otevřeme trace", "trace", "Skutečná navigace a failed expect v Trace Vieweru"),
        (
            "V našem výukovém",
            "code:tests/teaching/test_expected_failure.py:expect",
            "Nesprávný expected vedle platného zadání",
        ),
        (
            "Opravíme je",
            "code:training/solutions/test_10_fixed.py:Přihlášení",
            "Opravená verze očekávání",
        ),
        ("Pro ladění si ještě", "debug", "Skutečný Inspector a uživatelský kód"),
    ],
    "11_00": [
        ("Jednotlivý test", "run:regression", "Skutečná vybraná regresní sada"),
        ("Potom otevřeme HTML", "report", "HTML právě dokončeného běhu"),
        ("Vedle něj vzniká JUnit", "junit", "JUnit stejného skutečného běhu"),
        ("Při selhání uchovejte", "report_failure", "Archivovaný červený výsledek"),
        ("Ukážeme si také", "code:docs/azure-pipelines.yml:pytest", "Stejný příkaz v příkladu CI"),
        ("V této ukázce", "report", "Doložitelný lokální report"),
    ],
    "12_00": [
        (
            "Teď je řada",
            "code:training/exercises/WORKBOOK.md:| 12 |",
            "Zadání vlastního testu bez otevření řešení",
        ),
        ("Nejprve si ručně", "empty_search", "Ruční ověření skutečného prázdného stavu"),
        ("Potom bez nahlížení", "case_note:precondition", "Samostatně formulovaný předpoklad"),
        ("Video si v tuto", "case_note:action", "Samostatný krok vyhledávání"),
        ("Když budete hotovi", "case_note:expected", "Dvě konkrétní podmínky výsledku"),
        (
            "Potom ještě ukážeme",
            "code:.env.example:EXTERNAL",
            "Oddělená konfigurace pro jinou aplikaci",
        ),
        (
            "Proto začínáme oddělenou",
            "code:tests_external/test_availability.py:def test",
            "Read-only kontrola v samostatné sadě",
        ),
        (
            "Z kurzu si odneste",
            "code:training/exercises/WORKBOOK.md:| 12 |",
            "Vlastní pracovní postup a kontrola výsledku",
        ),
    ],
}


def phrase_time(section, phrase):
    position = section["paragraph"].index(phrase)
    return next(w["start"] for w in section["words"] if w["left"] <= position < w["right"])


def auto_action(section):
    screen = section["screen"]
    kind, act = screen["kind"], screen.get("action")
    if kind == "terminal":
        return "run:" + {"versions": "version", "setup": "setup", "first": "first"}.get(act, act)
    if kind == "browser":
        return {
            "overview": "login_reset",
            "login": "login",
            "create": "create",
            "journey": "create",
            "api_error": "api_error",
            "empty": "empty_search",
            "search": "search",
            "report": "report",
        }[act]
    if kind == "codegen":
        return "codegen_record" if act == "record" else "codegen_inspect"
    if kind == "trace":
        return "trace"
    if kind == "inspector":
        return "debug"
    if act == "select_interpreter":
        return "interpreter"
    if screen["source"].endswith("codegen_draft.py"):
        return "codegen_source"
    if screen["source"] == "reports/junit.xml":
        return "junit"
    return semantic_code(section, section["paragraph"])


def semantic_code(section, text):
    source = section["screen"]["source"]
    lowered = text.lower()
    if "neexistující nadpis" in lowered:
        return "code:tests/teaching/test_expected_failure.py:Neexistující nadpis"
    content = (ROOT / source).read_text(encoding="utf-8") if (ROOT / source).exists() else ""
    if "base_url" in lowered and "server = make_server" in content:
        return f"code:{source}:server = make_server"
    if "vysoká" in lowered:
        priority = next(
            (
                line.strip()
                for line in content.splitlines()
                if "expect(" in line and '"Vysoká"' in line
            ),
            None,
        )
        if priority:
            return f"code:{source}:{priority}"
    rules = [
        (r"import", "import"),
        (r"dvojtečk|definic", "def "),
        (r"návratov|vrátí|return", "return"),
        (r"prázdn|podmínk", "if not"),
        (r"seznam|titles", "titles ="),
        (r"parametriz", "parametrize"),
        (r"fixture|příprav", "def logged_in_page"),
        (r"nadpis", "heading"),
        (r"navigac|goto|adres", "goto"),
        (r"počet|řádk|identifikátor", "record-row"),
        (r"hesl", "password"),
        (r"popisk|pole|label", "get_by_label"),
        (r"očekáv|assert|ověř", "expect"),
        (r"přihláš", "DEMO_EMAIL"),
        (r"funkc", "def test"),
    ]
    for pattern, target in rules:
        if re.search(pattern, lowered) and target in content:
            return f"code:{source}:{target}"
    if source.startswith("reports/"):
        return "junit"
    if "codegen_draft" in source:
        return "codegen_source"
    if source.endswith("INSTALL_WINDOWS.md"):
        for phrase, target in [
            ("interpret", "Python: Select Interpreter"),
            ("instal", "setup_windows"),
            ("spušt", "pytest"),
            ("python", "Python"),
        ]:
            if phrase in lowered and target in content:
                return f"code:{source}:{target}"
    if source.endswith("azure-pipelines.yml"):
        for phrase, target in [
            ("junit", "PublishTestResults"),
            ("report", "PublishPipelineArtifact"),
            ("instal", "pip install"),
            ("test", "pytest"),
        ]:
            if phrase in lowered and target in content:
                return f"code:{source}:{target}"
    if "fixture" in lowered and "@pytest.fixture" in content:
        return f"code:{source}:@pytest.fixture"
    if source.endswith("conftest.py"):
        if (
            re.search(r"context|prohlížeč|viewport", lowered)
            and "def browser_context_args" in content
        ):
            return f"code:{source}:def browser_context_args"
        if "def logged_in_page" in content:
            return f"code:{source}:def logged_in_page"
        if "@pytest.fixture" in content:
            return f"code:{source}:@pytest.fixture"
    if source.endswith("login_page.py") and "class LoginPage" in content:
        return f"code:{source}:class LoginPage"
    return f"code:{source}:" + ("def test" if "def test" in content else "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapters", type=int, nargs="+", default=list(range(1, 13)))
    args = parser.parse_args()
    for chapter in args.chapters:
        if chapter == 4:
            continue
        path = HERE / "chapters" / f"{chapter:02}" / "timeline.json"
        plan = audio.read(path)
        for section in plan["sections"]:
            events = [
                {
                    "time": section["start"] + 0.35,
                    "voice_cue": section["paragraph"].split(".")[0],
                    "action": auto_action(section),
                    "expected_visible_state": section["title"],
                }
            ]
            index = int(section["id"].split("_")[1])
            is_practice = index == (7 if chapter == 7 else 6)
            if is_practice or section["id"] in SCENES:
                events = []
                authored = PRACTICE[chapter] if is_practice else SCENES[section["id"]]
                for phrase, action, expected in authored:
                    if phrase not in section["paragraph"]:
                        raise ValueError(f"Unknown native speech anchor {section['id']}: {phrase}")
                    events.append(
                        {
                            "time": phrase_time(section, phrase),
                            "voice_cue": phrase,
                            "action": action,
                            "expected_visible_state": expected,
                        }
                    )
            else:
                group, last_event = [], events[0]["time"]
                for word in section["words"]:
                    group.append(word)
                    if not re.search(r"[.!?]$", word["text"]):
                        continue
                    text = " ".join(w["text"] for w in group)
                    at = group[0]["start"]
                    if at - last_event >= 7 and section["screen"]["kind"] == "editor":
                        events.append(
                            {
                                "time": at,
                                "voice_cue": text,
                                "action": semantic_code(section, text),
                                "expected_visible_state": text,
                            }
                        )
                        last_event = at
                    group = []
            section["narration_action_cues"] = sorted(events, key=lambda e: e["time"])
        audio.save(path, plan)
        count = sum(len(s["narration_action_cues"]) for s in plan["sections"])
        print(
            f"Chapter {chapter}: {count} semantic actions",
            flush=True,
        )


if __name__ == "__main__":
    main()
