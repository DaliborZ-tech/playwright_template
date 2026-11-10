import pytest
from playwright.sync_api import Page, expect

from test_data.users import DEMO_EMAIL


@pytest.mark.parametrize("password", ["spatne", "jine", "dalsi-neplatne"])
def test_invalid_passwords(page: Page, password: str) -> None:
    page.goto("/login")
    page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    page.get_by_label("Heslo", exact=True).fill(password)
    page.get_by_role("button", name="Přihlásit se").click()
    expect(page.get_by_role("alert")).to_have_text("Nesprávný e-mail nebo heslo.")
