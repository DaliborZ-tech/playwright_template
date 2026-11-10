"""R2 reference chapter: authored narration, semantic actions and approval gate."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).resolve().parent

SECTIONS = [
    (
        "01",
        "Nejdřív si ověříme zadání",
        "manual",
        "Naším cílem je první samostatný test přihlašovacího formuláře. "
        "Nejdříve otevřu skutečnou aplikaci a společně si pojmenujeme očekávaný výsledek. "
        "Na stránce má být nadpis Přihlášení a tlačítko Přihlásit se. "
        "Do e-mailového pole teď napíšu náš veřejný testovací účet. "
        "Potom vyplním syntetické heslo a oba údaje zase odstraním. "
        "Samotné přihlášení dnes ještě automatizovat nebudeme. "
        "Náš první test zkontroluje zobrazení stránky a obou uvedených prvků.",
        [
            ("open", "Nejdříve otevřu", "browser", "open_login", "Přihlášení je viditelné"),
            (
                "email",
                "Do e-mailového",
                "browser",
                "fill_email",
                "Ve formuláři je syntetický e-mail",
            ),
            (
                "password",
                "Potom vyplním",
                "browser",
                "fill_clear",
                "Vyplněné pole, následně prázdný formulář",
            ),
        ],
    ),
    (
        "02",
        "Test vzniká od prázdného souboru",
        "editor",
        "V editoru teď otevřu prázdný soubor pro náš příklad. "
        "Jmenuje se test_video_created.py a leží ve složce tests, examples. "
        "Začátek názvu test je důležitý, protože podle něj pytest soubor najde. "
        "Nejprve napíšu import objektu Page a funkce expect. "
        "Page nám umožní ovládat kartu prohlížeče a expect zapisuje očekávání. "
        "Pod importem založím vlastní testovací funkci s argumentem page. "
        "Tento argument připraví naše existující fixture, nemusíme vytvářet prohlížeč ručně. "
        "Za definicí musí být dvojtečka. Příkazy, které za chvíli přidáme, odsadíme. "
        "Odsazené příkazy budou patřit do právě napsaného testu, nikoli mimo něj.",
        [
            ("blank", "V editoru teď", "editor", "blank", "Nový prázdný soubor v editoru"),
            (
                "import",
                "Nejprve napíšu",
                "editor",
                "type_import",
                "Import skutečně přibývá v souboru",
            ),
            (
                "function",
                "Pod importem",
                "editor",
                "type_function",
                "Funkce test_video_login_form(page: Page)",
            ),
        ],
    ),
    (
        "03",
        "Navigace a skutečný DOM",
        "browser",
        "Do těla funkce přidám první skutečný krok, page.goto s cestou login. "
        "Relativní adresu doplní připravený testovací server našeho Starter Kitu. "
        "Soubor teď uložím a vrátím se do prohlížeče. "
        "Chci ukázat, podle čeho poznáme správný nadpis. "
        "Otevřu vývojářské nástroje a vyberu přímo nadpis Přihlášení. "
        "Ve skutečném DOM je vidět prvek h2 a jeho text. "
        "Prvek h2 má roli heading; názvem rozlišíme konkrétní nadpis. "
        "Nepotřebujeme kopírovat dlouhou cestu přes vnořené kontejnery ani náhodné CSS třídy. "
        "Výběr prvku teď spojujeme s tím, co má uživatel skutečně poznat na stránce.",
        [
            ("goto", "Do těla funkce", "editor", "type_goto", "Přibyl page.goto('/login')"),
            ("save", "Soubor teď uložím", "editor", "save", "Uložený skutečný Python soubor"),
            (
                "dom",
                "Otevřu vývojářské",
                "browser",
                "inspect_heading",
                "Živý DOM a vybraný h2 s textem Přihlášení",
            ),
        ],
    ),
    (
        "04",
        "Z nalezeného prvku vzniká očekávání",
        "editor",
        "Zpátky v editoru napíšu očekávání pro právě prohlédnutý nadpis. "
        "Použiji get_by_role s rolí heading a přesným názvem Přihlášení. "
        "Volba exact vyžaduje shodu celého názvu, nikoli jen jeho části. "
        "Za lokátor připojím to_be_visible, protože chceme nadpis opravdu vidět. "
        "Potom přidám druhé očekávání pro tlačítko Přihlásit se. "
        "Tady je rolí button a názvem text našeho tlačítka. "
        "Vrátím se ještě k živému prvku v prohlížeči a vyberu tlačítko v DOM. "
        "Obě kontroly tak mají oporu ve skutečné aplikaci. "
        "Pouhé otevření adresy by nám ještě nepotvrdilo, že se formulář správně zobrazil.",
        [
            (
                "heading",
                "Zpátky v editoru",
                "editor",
                "type_heading",
                "Přibyl locator heading a očekávání viditelnosti",
            ),
            (
                "button",
                "Potom přidám",
                "editor",
                "type_button",
                "Přibyl locator button a druhé očekávání",
            ),
            (
                "button_dom",
                "Vrátím se ještě",
                "browser",
                "inspect_button",
                "Živý DOM vybraného tlačítka",
            ),
        ],
    ),
    (
        "05",
        "Nejdřív ověříme, že test umí selhat",
        "red",
        "Než budeme věřit zelenému výsledku, vyzkoušíme kontrolovanou chybu. "
        "V prvním očekávání teď změním pouze hledaný text na Neexistující nadpis. "
        "Ostatní kroky i jméno testu nechám stejné a soubor uložím. "
        "V terminálu spustím právě tento jeden test. "
        "Přepínač headed zpřístupní skutečný prohlížeč a slowmo zpomalí ukázku. "
        "Zpomalení je pomůcka pro sledování, nikoli řešení nestabilních testů. "
        "V nahrávce prohlížeče z tohoto běhu se přihlašovací stránka opravdu načetla. "
        "Test ale marně hledá text, který jsme si vymysleli. "
        "Teď už terminál ukazuje selhání a návratový kód je jedna. "
        "To je očekávaný výsledek našeho záměrně chybného zadání.",
        [
            (
                "wrong",
                "V prvním očekávání teď",
                "editor",
                "make_red",
                "Stejný test, pouze chybný očekávaný text",
            ),
            (
                "red_command",
                "V terminálu spustím",
                "terminal",
                "red_command",
                "Skutečný příkaz pro stejný nodeid",
            ),
            (
                "red_run",
                "Přepínač headed",
                "terminal",
                "red_run",
                "Skutečný pytest běh a jeho RED výsledek",
            ),
            (
                "red_browser",
                "V nahrávce prohlížeče",
                "test_video",
                "red_video",
                "Skutečný záznam browseru právě tohoto běhu",
            ),
            (
                "red_result",
                "Teď už terminál",
                "terminal",
                "red_result",
                "1 failed, skutečný exit1 a JUnit bez infrastrukturních errors",
            ),
        ],
    ),
    (
        "06",
        "Chybu vysvětlíme a opravíme tentýž test",
        "green",
        "V chybovém výpisu najdu assertion a hledaný Neexistující nadpis. "
        "Stránka má přitom stále správný nadpis Přihlášení. "
        "Příčina je tedy v očekávání testu, nikoli v přihlašovacím formuláři. "
        "V editoru teď opravím jen tuto jednu hodnotu na Přihlášení. "
        "Kontrolu nemažu, nepřidávám xfail a nezvyšuji bez důvodu časový limit. "
        "Soubor znovu uložím a stejný test spustím podruhé. "
        "Mění se pouze složka s reportem, aby nám původní chyba zůstala jako důkaz. "
        "Také druhý záznam browseru pochází ze skutečného běhu. "
        "Nyní obě očekávání odpovídají stránce a terminál ukazuje jeden úspěšný test. "
        "Zelené číslo už umíme vysvětlit konkrétní opravou.",
        [
            (
                "failure_detail",
                "V chybovém výpisu",
                "terminal",
                "red_detail",
                "Výpis konkrétního assertionu a hledaného textu",
            ),
            (
                "fix",
                "V editoru teď opravím",
                "editor",
                "make_green",
                "Oprava jediného očekávaného textu",
            ),
            (
                "green_command",
                "Soubor znovu uložím",
                "terminal",
                "green_command",
                "Tentýž nodeid; jiný cílový report",
            ),
            ("green_run", "Mění se pouze složka", "terminal", "green_run", "Skutečný GREEN běh"),
            (
                "green_browser",
                "Také druhý záznam",
                "test_video",
                "green_video",
                "Video z druhého běhu téhož testu",
            ),
            (
                "green_result",
                "Nyní obě očekávání",
                "terminal",
                "green_result",
                "1 passed, skutečný exit0 a JUnit",
            ),
        ],
    ),
    (
        "07",
        "Výsledek dohledáme a test zopakujeme",
        "report",
        "Nakonec otevřu skutečný HTML report druhého běhu. "
        "V přehledu je jeden úspěšný případ a dohledáme jeho název. "
        "Rozbalím podrobnosti, abychom výsledek spojili s právě napsaným souborem. "
        "Report neříká, že jsme prověřili celé přihlašování nebo celou aplikaci. "
        "Potvrzuje pouze naše dva viditelné prvky na přihlašovací stránce. "
        "V editoru si teď ještě jednou projdeme výsledný krátký test. "
        "Má import, vlastní funkci, navigaci a dvě jasná očekávání. "
        "Pro samostatné procvičení přidejte kontrolu přítomnosti e-mailového pole "
        "a test znovu spusťte. "
        "Nejdřív si vlastnost ověřte ručně a potom vysvětlete, "
        "co zelený výsledek skutečně dokazuje.",
        [
            (
                "report",
                "Nakonec otevřu",
                "browser",
                "open_report",
                "Čerstvý GREEN report, jeden skutečný případ",
            ),
            (
                "details",
                "Rozbalím podrobnosti",
                "browser",
                "report_details",
                "Viditelný název a detaily právě běžícího testu",
            ),
            (
                "final_code",
                "V editoru si teď",
                "editor",
                "final_code",
                "Výsledný soubor shodný se zmrazenou verzí",
            ),
            (
                "exercise",
                "Pro samostatné procvičení",
                "browser",
                "exercise",
                "Živě vybrané e-mailové pole pro samostatný úkol",
            ),
        ],
    ),
]


def main():
    sections = []
    for number, title, stage, paragraph, shots in SECTIONS:
        sections.append(
            {
                "id": f"r2_{number}",
                "title": title,
                "paragraph": paragraph,
                "voice": "cs-CZ-VlastaNeural",
                "stage": stage,
                "shots": [
                    {
                        "id": f"{number}_{key}",
                        "voice_cue": cue,
                        "on_screen_action": action,
                        "view": view,
                        "camera_focus": "Semantic subject, actual app geometry",
                        "expected_visible_state": state,
                        "proof": "Actual source/DOM/run state plus extracted frames",
                    }
                    for key, cue, view, action, state in shots
                ],
            }
        )
    plan = {
        "revision": "R2",
        "status": "CHANGES_REQUIRED",
        "approval_gate": "HUMAN_REFERENCE_CHAPTER_APPROVAL_REQUIRED",
        "full_course_build_authorized": False,
        "title": "První vlastní test: od prázdného souboru k RED a GREEN",
        "learning_outcome": (
            "Účastník napíše a vysvětlí test formuláře, spustí jej, "
            "opraví chybné očekávání a dohledá výsledek."
        ),
        "test_nodeid": "tests/examples/test_video_created.py::test_video_login_form",
        "sections": sections,
    }
    (DEST / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        {
            "sections": len(sections),
            "shots": sum(len(s["shots"]) for s in sections),
            "words": sum(len(s["paragraph"].split()) for s in sections),
        }
    )


if __name__ == "__main__":
    main()
