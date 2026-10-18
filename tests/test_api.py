from fastapi.testclient import TestClient
from api import app
from player import Player

client = TestClient(app)


def test_post_training_invalid_made():
    response = client.post(
        "/training",
        json={
            "training_date": "2026-10-15",
            "shots": 10,
            "made": 12
        }
    )

    assert response.status_code == 422

from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_post_training_invalid_made():
    response = client.post(
        "/training",
        json={
            "training_date": "2026-10-15",
            "shots": 10,
            "made": 12
        }
    )

    assert response.status_code == 422

def test_post_training_success(monkeypatch):
    player = Player("Test", 20, "SG")
    saved = []

    def fake_load():
        return player

    def fake_save(self):
        saved.append(True)

    monkeypatch.setattr(Player, "load_from_json", fake_load)
    monkeypatch.setattr(Player, "save_to_json", fake_save)

    response = client.post(
        "/training",
        json={
            "training_date": "2026-10-15",
            "shots": 10,
            "made": 7
        }
    )

    assert response.status_code == 201
    assert response.json()["training"]["percentage"] == 70.0
    assert len(player.training_history) == 1
    assert saved == [True]

def test_get_training_by_date_no_records(monkeypatch):
    def fake_get_training_by_date(training_date):
        return []

    monkeypatch.setattr(
        "api.get_training_by_date",
        fake_get_training_by_date
    )

    response = client.get(
        "/training-by-date",
        params={"training_date": "2026-10-18"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "training_date": "2026-10-18",
        "records": []
    }
