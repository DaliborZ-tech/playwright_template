from playwright.sync_api import Page, expect


def test_record_owned_by_petr(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_role("button", name="Nový záznam").click()
    page.get_by_label("Název požadavku").fill("Regresní úkol Petra")
    page.get_by_label("Řešitel", exact=True).select_option(label="Petr")
    page.get_by_role("button", name="Uložit záznam").click()
    row = page.get_by_role("row").filter(has_text="Regresní úkol Petra")
    expect(row).to_contain_text("Petr")
    row.get_by_role("button", name="Upravit Regresní úkol Petra", exact=True).click()
    page.get_by_label("Stav", exact=True).select_option(label="Hotový")
    page.get_by_role("button", name="Uložit záznam").click()
    expect(row).to_contain_text("Hotový")
    page.once("dialog", lambda dialog: dialog.accept())
    row.get_by_role("button", name="Smazat Regresní úkol Petra", exact=True).click()
    expect(row).to_have_count(0)
