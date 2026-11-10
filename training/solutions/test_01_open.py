from playwright.sync_api import Page, expect


def test_open_login(page: Page) -> None:
    # Předpoklad: fixture dodala novou kartu a lokální server.
    page.goto("/login")  # Akce: otevření přihlášení.
    expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()
