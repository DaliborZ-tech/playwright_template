# Český praktický manuál

Tento průvodce předpokládá znalost manuálního testování, nikoliv programování.
Připravený test odpovídá známému zápisu: předpoklad, kroky, očekávaný výsledek.
Při automatizaci překládáte tyto tři části do opakovatelného programu.

Začněte [instalací](../docs/INSTALL_WINDOWS.md). Potom postupujte po lekcích.
Po každé lekci zavřete řešení, proveďte úkol sami a až pak porovnejte výsledek.
Úspěch znamená, že umíte vysvětlit, co test ověřuje, nikoliv jen získat zelený řádek.

| Lekce | Téma | Spustitelné řešení |
|---|---|---|
| [01](lessons/01.md) | Regrese a nástroje | `training/solutions/test_01_open.py` |
| [02](lessons/02.md) | Instalace a první běh | `training/solutions/test_02_login.py` |
| [03](lessons/03.md) | Python na příkladech testů | `training/solutions/test_03_python.py` |
| [04](lessons/04.md) | První vlastní test | `training/solutions/test_04_first.py` |
| [05](lessons/05.md) | Lokátory | `training/solutions/test_05_locators.py` |
| [06](lessons/06.md) | Akce a očekávání | `training/solutions/test_06_actions.py` |
| [07](lessons/07.md) | pytest, data, fixtures | `training/solutions/test_07_parametrize.py` |
| [08](lessons/08.md) | Celá regresní cesta | `tests/regression/test_records.py::test_12_complete_regression_journey` |
| [09](lessons/09.md) | Codegen | `training/solutions/test_09_codegen_refined.py` |
| [10](lessons/10.md) | Chyba a její oprava | `training/solutions/test_10_fixed.py` |
| [11](lessons/11.md) | Reporty | `training/solutions/test_11_report.py` |
| [12](lessons/12.md) | Vlastní test | `training/solutions/test_12_search.py` |

Řešení využívají stejný lokální server a izolaci jako Starter Kit.
Z kořene je spusťte příkazem
`.\.venv\Scripts\python.exe -m pytest training/solutions -v`.
Nejdříve zkuste úkoly z [pracovního sešitu](exercises/WORKBOOK.md).

## Jak číst výsledek

`passed` znamená, že naprogramovaná očekávání prošla. Neznamená to, že aplikace
nemá jiné vady. `failed` znamená nesplněné očekávání nebo chybu v těle testu;
`error` obvykle znamená problém přípravy či úklidu. `skipped` označuje test,
který se neprovedl. Počet vybraných testů vždy porovnejte se zamýšleným rozsahem.

Report běžného běhu najdete v `reports/report.html`, strojový výsledek v
`reports/junit.xml`. Report další běh přepíše; před sdílením potřebný výsledek
archivujte do nové složky. Řízená chyba má vlastní `failure.html` a vlastní
artefakty, takže se neztratí při následném úspěšném běhu opravy.

## Když se nedaří

Přečtěte poslední chybu a první místo ve svém souboru, na které traceback
ukazuje. Nespravujte vše najednou. Ověřte URL, stav aplikace, jednoznačnost
lokátoru a správnost očekávání. Potom použijte screenshot nebo trace.
[Troubleshooting](troubleshooting/windows.md) pomůže určit další krok.

Referenci najdete v [cheatsheetu](cheatsheets/playwright-python.md), pojmy ve
[slovníku](GLOSSARY.md). Firemní adaptaci začněte read-only testem dostupnosti
v odděleném `tests_external`; demo scénáře nepřesměrovávejte do firemního systému.

