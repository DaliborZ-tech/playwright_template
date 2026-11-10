def normalize(title: str) -> str:
    # Parametr title obsahuje předaný text; return vrací upravenou hodnotu.
    cleaned = title.strip()
    if not cleaned:
        return "Bez názvu"
    return cleaned


def test_synthetic_titles() -> None:
    titles = [" Kontrola exportu ", "Kontrola fakturace"]
    assert normalize(titles[0]) == "Kontrola exportu"
    assert normalize(titles[1]) == "Kontrola fakturace"
    assert normalize("   ") == "Bez názvu"
