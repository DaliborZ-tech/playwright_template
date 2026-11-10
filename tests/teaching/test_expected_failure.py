import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.teaching_failure


def test_wrong_heading(page: Page) -> None:
    """Spouští se pouze explicitně. Oprava: Neexistující nadpis → Přihlášení."""
    page.goto("/login")
    expect(page.get_by_role("heading", name="Neexistující nadpis", exact=True)).to_be_visible(
        timeout=1500
    )
