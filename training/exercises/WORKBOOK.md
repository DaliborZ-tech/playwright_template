# Pracovní sešit a kontrola výsledků

Nejprve napište očekávaný výsledek vlastními slovy. Potom napište test. Řešení
otevřete až při porovnání; cílem není naučit se řádky zpaměti.

| Úkol | Samostatná práce | Jak poznáte správné řešení |
|---|---|---|
| 01 | Napište manuální test otevření přihlášení | Předpoklad server, akce otevření /login, výsledek viditelný nadpis |
| 02 | Nainstalujte projekt a spusťte jeden login test | Správný interpreter 3.12, výsledek v HTML, nikoliv jen otevřený browser |
| 03 | Upravte dvě syntetická jména a funkci normalize | Mezery se odstraní, prázdný text vrátí Bez názvu, všechny tři asserts projdou |
| 04 | Napište test od prázdného souboru | Import, funkce test_*, fixture page, navigace a dvě ověření |
| 05 | Najděte pole podle labelů a spočítejte záznamy | Tři record-row, čtyři role row včetně hlavičky |
| 06 | Vytvořte prioritní požadavek | Zaškrtnutý checkbox a text Vysoká v konkrétním uloženém řádku |
| 07 | Přidejte parametr chybného hesla | Vzroste počet provedených případů, každý dostane novou relaci |
| 08 | Vytvořte, dokončete a smažte Petrův úkol | Řádek nese Petra, pak Hotový, po potvrzení dialogu zmizí |
| 09 | Použijte Codegen a upravte draft | Relativní URL, pytest fixture, syntetická data, nadpis a počet řádků |
| 10 | Vyvolejte chybu a opravte očekávání | Reálný exit 1, screenshot a trace; opravený test exit 0 |
| 11 | Najděte jeden případ v HTML a XML | Shodný název a výsledek, hlášení přesně popisuje spuštěný rozsah |
| 12 | Napište prázdné vyhledávání sami | Nula datových řádků i viditelná prázdná zpráva, test funguje samostatně |

Řešení 01–12 jsou ve vedlejší složce `solutions`. Příkaz pro jednotlivý úkol:
`.\.venv\Scripts\python.exe -m pytest training/solutions/test_12_search.py -v`.
Změňte název podle úkolu. Úlohy s browserem používají stejné fixtures jako sada.

## Rozbor řešení 10

Screenshot i DOM v trace obsahují Přihlášení. Test požaduje Neexistující nadpis.
Podle platného zadání je chyba v očekávání testu. Opravená verze zamění pouze
jméno nadpisu, neodebírá assertion a nezvyšuje bez důvodu timeout. Červený test
zůstává zachovaný v explicitně zapínané teaching složce jako výukový materiál.

## Vzor hlášení k úloze 11

„V lokálním demu verze 1.0.0 jsem spustil konkrétní soubor
training/solutions/test_11_report.py v Chromiu projektovým Pythonem 3.12.
Vybraný případ prošel. HTML a JUnit jsou v reports. Ostatní regresní scénáře
tento příkaz nespouštěl.“ Doplňte skutečný čas a skutečný výsledek svého běhu.

## Cvičení navíc

Zamítněte mazací dialog a ověřte zachování řádku i po reloadu. Pak otevřete
dva oddělené browser contexts a ověřte soukromý reset. Referenční řešení
jsou v `tests/regression/test_isolation.py`; oba testy jsou součástí regrese.

