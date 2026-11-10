## Nejdřív si ověříme zadání

Naším cílem je první samostatný test přihlašovacího formuláře. Nejdříve otevřu skutečnou aplikaci a společně si pojmenujeme očekávaný výsledek. Na stránce má být nadpis Přihlášení a tlačítko Přihlásit se. Do e-mailového pole teď napíšu náš veřejný testovací účet. Potom vyplním syntetické heslo a oba údaje zase odstraním. Samotné přihlášení dnes ještě automatizovat nebudeme. Náš první test zkontroluje zobrazení stránky a obou uvedených prvků.

## Test vzniká od prázdného souboru

V editoru teď otevřu prázdný soubor pro náš příklad. Jmenuje se test_video_created.py a leží ve složce tests, examples. Začátek názvu test je důležitý, protože podle něj pytest soubor najde. Nejprve napíšu import objektu Page a funkce expect. Page nám umožní ovládat kartu prohlížeče a expect zapisuje očekávání. Pod importem založím vlastní testovací funkci s argumentem page. Tento argument připraví naše existující fixture, nemusíme vytvářet prohlížeč ručně. Za definicí musí být dvojtečka. Příkazy, které za chvíli přidáme, odsadíme. Odsazené příkazy budou patřit do právě napsaného testu, nikoli mimo něj.

## Navigace a skutečný DOM

Do těla funkce přidám první skutečný krok, page.goto s cestou login. Relativní adresu doplní připravený testovací server našeho Starter Kitu. Soubor teď uložím a vrátím se do prohlížeče. Chci ukázat, podle čeho poznáme správný nadpis. Otevřu vývojářské nástroje a vyberu přímo nadpis Přihlášení. Ve skutečném DOM je vidět prvek h2 a jeho text. Prvek h2 má roli heading; názvem rozlišíme konkrétní nadpis. Nepotřebujeme kopírovat dlouhou cestu přes vnořené kontejnery ani náhodné CSS třídy. Výběr prvku teď spojujeme s tím, co má uživatel skutečně poznat na stránce.

## Z nalezeného prvku vzniká očekávání

Zpátky v editoru napíšu očekávání pro právě prohlédnutý nadpis. Použiji get_by_role s rolí heading a přesným názvem Přihlášení. Volba exact vyžaduje shodu celého názvu, nikoli jen jeho části. Za lokátor připojím to_be_visible, protože chceme nadpis opravdu vidět. Potom přidám druhé očekávání pro tlačítko Přihlásit se. Tady je rolí button a názvem text našeho tlačítka. Vrátím se ještě k živému prvku v prohlížeči a vyberu tlačítko v DOM. Obě kontroly tak mají oporu ve skutečné aplikaci. Pouhé otevření adresy by nám ještě nepotvrdilo, že se formulář správně zobrazil.

## Nejdřív ověříme, že test umí selhat

Než budeme věřit zelenému výsledku, vyzkoušíme kontrolovanou chybu. V prvním očekávání teď změním pouze hledaný text na Neexistující nadpis. Ostatní kroky i jméno testu nechám stejné a soubor uložím. V terminálu spustím právě tento jeden test. Přepínač headed zpřístupní skutečný prohlížeč a slowmo zpomalí ukázku. Zpomalení je pomůcka pro sledování, nikoli řešení nestabilních testů. V nahrávce prohlížeče z tohoto běhu se přihlašovací stránka opravdu načetla. Test ale marně hledá text, který jsme si vymysleli. Teď už terminál ukazuje selhání a návratový kód je jedna. To je očekávaný výsledek našeho záměrně chybného zadání.

## Chybu vysvětlíme a opravíme tentýž test

V chybovém výpisu najdu assertion a hledaný Neexistující nadpis. Stránka má přitom stále správný nadpis Přihlášení. Příčina je tedy v očekávání testu, nikoli v přihlašovacím formuláři. V editoru teď opravím jen tuto jednu hodnotu na Přihlášení. Kontrolu nemažu, nepřidávám xfail a nezvyšuji bez důvodu časový limit. Soubor znovu uložím a stejný test spustím podruhé. Mění se pouze složka s reportem, aby nám původní chyba zůstala jako důkaz. Také druhý záznam browseru pochází ze skutečného běhu. Nyní obě očekávání odpovídají stránce a terminál ukazuje jeden úspěšný test. Zelené číslo už umíme vysvětlit konkrétní opravou.

## Výsledek dohledáme a test zopakujeme

Nakonec otevřu skutečný HTML report druhého běhu. V přehledu je jeden úspěšný případ a dohledáme jeho název. Rozbalím podrobnosti, abychom výsledek spojili s právě napsaným souborem. Report neříká, že jsme prověřili celé přihlašování nebo celou aplikaci. Potvrzuje pouze naše dva viditelné prvky na přihlašovací stránce. V editoru si teď ještě jednou projdeme výsledný krátký test. Má import, vlastní funkci, navigaci a dvě jasná očekávání. Pro samostatné procvičení přidejte kontrolu přítomnosti e-mailového pole a test znovu spusťte. Nejdřív si vlastnost ověřte ručně a potom vysvětlete, co zelený výsledek skutečně dokazuje.