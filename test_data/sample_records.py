from copy import deepcopy

SEED_RECORDS = [
    {"id": 1, "title": "Kontrola přihlášení", "owner": "Jana", "status": "Nový", "priority": True},
    {
        "id": 2,
        "title": "Export měsíčního reportu",
        "owner": "Petr",
        "status": "Rozpracovaný",
        "priority": False,
    },
    {
        "id": 3,
        "title": "Oprava vyhledávání",
        "owner": "Jana",
        "status": "Hotový",
        "priority": False,
    },
]


def seed_records() -> list[dict]:
    """Každá relace dostane vlastní kopii, nikoli sdílený seznam."""
    return deepcopy(SEED_RECORDS)
