"""Ručně upravený vzor: neoznačujeme jej za skutečný export Codegenu."""

from playwright.sync_api import Page, expect

from test_data.users import DEMO_EMAIL, DEMO_PASSWORD


def test_refined_recording(page: Page) -> None:
    # Absolutní nahraná URL se změnila na relativní cestu automatického dema.
    page.goto("/login")
    page.get_by_label("E-mail", exact=True).fill(DEMO_EMAIL)
    page.get_by_label("Heslo", exact=True).fill(DEMO_PASSWORD)
    page.get_by_role("button", name="Přihlásit se").click()
    page.get_by_role("link", name="Záznamy").click()
    expect(page.get_by_role("heading", name="Záznamy", exact=True)).to_be_visible()
    expect(page.get_by_test_id("record-row")).to_have_count(3)
