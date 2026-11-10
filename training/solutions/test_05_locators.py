from playwright.sync_api import Page, expect

from test_data.users import DEMO_EMAIL, DEMO_PASSWORD


def test_labels_and_rows(page: Page) -> None:
    page.goto("/login")
    page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    page.get_by_label("Heslo", exact=True).fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Přihlásit se").click()
    expect(page.get_by_test_id("record-row")).to_have_count(3)
    # Hlavička tabulky má také roli row, proto celkem čtyři.
    expect(page.get_by_role("row")).to_have_count(4)
