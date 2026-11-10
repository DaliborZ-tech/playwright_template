from playwright.sync_api import Page, expect


def test_report_case(logged_in_page: Page) -> None:
    # Název této funkce najděte jako testcase v HTML i JUnit XML.
    expect(logged_in_page.get_by_test_id("record-row")).to_have_count(3)
