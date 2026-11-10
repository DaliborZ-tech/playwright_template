from playwright.sync_api import Page, expect


def test_priority_record(logged_in_page: Page) -> None:
    page = logged_in_page
    page.get_by_role("button", name="Nový záznam").click()
    page.get_by_label("Název požadavku").fill("Ověření priority")
    page.get_by_label("Prioritní").check()
    expect(page.get_by_label("Prioritní")).to_be_checked()
    page.get_by_role("button", name="Uložit záznam").click()
    row = page.get_by_role("row").filter(has_text="Ověření priority")
    expect(row).to_contain_text("Vysoká")
