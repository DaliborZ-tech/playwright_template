"""Meaning-driven camera paths and annotations, measured later against rendered frames."""


def cue_time(section, phrase, shot):
    position = section["paragraph"].index(phrase)
    return (
        next(w["start"] for w in section["words"] if w["left"] <= position < w["right"])
        - shot["start"]
    )


def design(shot, section, action_end, maximum, fx, fy):
    duration = shot["duration"]
    action = shot["on_screen_action"]
    notes = []
    subject = shot["expected_visible_state"]
    if action == "type_function":
        at = cue_time(section, "Tento argument", shot)
        maximum = 1.38
        notes = [
            (at, "page: Page · fixture připraví kartu prohlížeče"),
            (
                cue_time(section, "Za definicí", shot),
                "Dvojtečka ukončí definici; příští příkazy odsadíme",
            ),
        ]
        subject = "Argument page: Page uvnitř celé definice funkce"
    elif action == "type_heading":
        at = cue_time(section, "Použiji get_by_role", shot)
        maximum = 1.38
        notes = [
            (at, 'get_by_role("heading", name="Přihlášení", exact=True)'),
            (
                cue_time(section, "Za lokátor", shot),
                "to_be_visible() · skutečné očekávání viditelnosti",
            ),
        ]
        subject = "Od navigace page.goto k roli, názvu a očekávání nadpisu"
    elif action == "inspect_heading":
        at = cue_time(section, "Prvek h2", shot)
        maximum = 1.62
        notes = [
            (cue_time(section, "Ve skutečném DOM", shot), "Vybraný skutečný h2 · text Přihlášení"),
            (at, "h2 → role heading · přístupný název je text nadpisu"),
            (cue_time(section, "Nepotřebujeme", shot), "Role + název místo dlouhé CSS cesty"),
        ]
        subject = "Vybraný h2 v DOM a odpovídající nadpis živého formuláře"
    else:
        at = 1.0
    at = min(max(0.4, at), max(0.4, duration - 5.4))
    end_in = min(at + 2.4, duration - 2.6)
    start_out = max(end_in, duration - 2.6)
    path = [
        {"t": 0, "zoom": 1.0},
        {"t": at, "zoom": 1.0},
        {"t": end_in, "zoom": maximum},
        {"t": start_out, "zoom": maximum},
        {"t": min(duration - 0.1, start_out + 2.4), "zoom": 1.0},
    ]
    if duration < 5.5 or action.startswith("cg_"):
        path = [{"t": 0, "zoom": maximum}]
    return {
        "path": path,
        "notes": notes,
        "subject": subject,
        "fx": fx,
        "fy": fy,
        "zoom_in_interval": [at, end_in],
        "return_interval": [start_out, min(duration - 0.1, start_out + 2.4)],
    }


def expression(path):
    result = str(path[0]["zoom"])
    for a, b in zip(path, path[1:], strict=False):
        delta = b["zoom"] - a["zoom"]
        if not delta:
            continue
        progress = f"min(max((on/25-{a['t']:.6f})/{max(0.001, b['t'] - a['t']):.6f},0),1)"
        result += f"+({delta:.6f})*({progress})*({progress})*(3-2*({progress}))"
    return result
