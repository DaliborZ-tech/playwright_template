from playwright.sync_api import Page, expect


def test_login_page(page: Page) -> None:
    # page je připravená karta prohlížeče; expect ověří očekávaný výsledek.
    page.goto("/login")
    expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()
