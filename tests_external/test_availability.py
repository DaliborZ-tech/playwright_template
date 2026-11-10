from playwright.sync_api import Page, expect


def test_approved_application_opens(page: Page) -> None:
    """Nejprve nahraďte / a obecnou kontrolu konkrétním schváleným scénářem."""
    response = page.goto("/")
    assert response is not None and response.ok
    expect(page.locator("body")).to_be_visible()
