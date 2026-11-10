# Akceptační scénář začátečníka

Tento dokument popisuje úkol pro skutečného člověka. Automatické spuštění
řešení je pouze **simulovaný walkthrough**, nikoliv uživatelský test.
Skutečný začátečník nebyl během realizace k dispozici. Změřené lidské časy,
porozumění ani poslechová srozumitelnost z toho neplynou.

| Krok | Zadání bez vývojářské pomoci | Důkaz úspěchu |
|---|---|---|
| 1 | Rozbalte projekt a otevřete README | Člověk najde začátek instalace |
| 2 | Nainstalujte profil Python 3.12 a spusťte setup_windows | Návratový kód 0, správný interpreter a lock |
| 3 | Spusťte start_demo a přihlaste se | Vidí Dashboard a tři výchozí požadavky |
| 4 | Spusťte run_smoke | Skutečný výsledek passed |
| 5 | Otevřete HTML report | Najde oba smoke scénáře a jejich výsledek |
| 6 | Napište nový test prázdného hledání | Nový soubor test_*, vlastní pojmenování |
| 7 | Spusťte pouze svůj test | Ověření nula řádků i viditelné prázdné zprávy |
| 8 | Vyvolejte run_failure | Exit 1 a dohledatelný traceback |
| 9 | Otevřete trace | Najde očekávaný lokátor a skutečný nadpis |
| 10 | Opravte chybu a spusťte znovu | Správné očekávání a exit 0 |

Facilitátor nezadává příkazy za účastníka. Zaznamená místo zaváhání, přesnou
chybu, potřebnou nápovědu a zda účastník dokáže vlastními slovy vysvětlit výsledek.
Po každém kroku se ptejte „Co tento výsledek znamená?“ Pozorované neporozumění
je podklad k opravě kurzu, ne vada účastníka.

## Simulace při realizaci

Projektové skripty a řešení se spouštějí automaticky v této existující Windows
stanici; konkrétní výsledky a omezení jsou v `docs/ACCEPTANCE.md` a `evidence/`.
Čistou novou instalaci Windows ani přehrání hotového kurzu tato simulace
neprokazuje. Úkol nového testu je automaticky pokryt referenčním řešením
`training/solutions/test_12_search.py`, nikoliv novým nezávislým lidským výtvorem.
