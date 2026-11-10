import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.regression
def test_application_opens(page: Page) -> None:
    """První kontrola dostupnosti; přidejte očekávání konkrétní pro svou aplikaci."""
    response = page.goto("/")
    assert response is not None, "Navigace nevrátila HTTP odpověď."
    assert response.ok, f"Aplikace vrátila HTTP {response.status}."
    expect(page.locator("body")).to_be_visible()
