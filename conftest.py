"""Společné přepínače; demo fixtures jsou oddělené od tests_external."""

from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=False)


def pytest_addoption(parser):
    parser.addoption("--teaching-failure", action="store_true", help="Zahrnout řízené selhání")
    parser.addoption("--external", action="store_true", help="Výslovný běh testů cizí aplikace")
    parser.addoption("--reverse-order", action="store_true", help="Ověřit opačné pořadí testů")


def pytest_ignore_collect(collection_path: Path, config):
    if collection_path.name == "teaching" and not config.getoption("--teaching-failure"):
        return True
    return None


def pytest_collection_modifyitems(config, items):
    external = config.getoption("--external")
    for item in items:
        is_external = "tests_external" in Path(str(item.path)).parts
        if is_external != external:
            raise pytest.UsageError(
                "Demo a firemní testy nelze míchat. Pro vlastní web použijte "
                "pytest tests_external --external; pro demo pytest bez --external."
            )
    if config.getoption("--reverse-order"):
        items.reverse()
