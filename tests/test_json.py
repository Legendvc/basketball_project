import json


def test_player_json():

    with open(
        "player.json",
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    assert data["name"] == "Richard"
    assert data["position"] == "SG"