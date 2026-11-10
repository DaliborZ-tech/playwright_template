"""Výsledek souboru vytvořeného od prázdné stránky během videokurzu."""

from playwright.sync_api import Page, expect


def test_video_login_form(page: Page) -> None:
    page.goto("/login")
    expect(page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Přihlásit se")).to_be_visible()
