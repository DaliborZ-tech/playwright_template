from playwright.sync_api import Page, expect


def test_correct_heading(page: Page) -> None:
    page.goto("/login")
    # Platný požadavek říká Přihlášení. Změna očekávání opravuje chybu testu.
    expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()
