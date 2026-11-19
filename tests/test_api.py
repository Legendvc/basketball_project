import pytest
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session

from api import app
from api_orm_demo import app as orm_app, get_db
from models import Base, Training, User
from player import Player


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(
        URL.create("sqlite", database=str(tmp_path / "training.db"))
    )
    player = Player("Richard", 31, "SG")
    monkeypatch.setattr(Player, "load_from_json", lambda: player)

    def fail_on_json_write(self):
        pytest.fail("训练接口应只写入 SQLite")

    monkeypatch.setattr(Player, "save_to_json", fail_on_json_write)

    def override_get_db():
        with Session(engine) as session:
            yield session

    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session, session.begin():
            session.add_all([
                User(id=1, username="Richard"),
                User(id=2, username="Alice"),
            ])
            session.flush()
            session.add_all([
                Training(user_id=1, date="2026-10-15", shots=10, made=8),
                Training(user_id=2, date="2026-10-15", shots=20, made=12),
            ])

        monkeypatch.setitem(app.dependency_overrides, get_db, override_get_db)
        monkeypatch.setitem(orm_app.dependency_overrides, get_db, override_get_db)
        with TestClient(app) as test_client:
            yield test_client
    finally:
        engine.dispose()


def test_post_training_invalid_made(client):
    response = client.post(
        "/training",
        json={"training_date": "2026-10-15", "shots": 10, "made": 12},
    )
    assert response.status_code == 422


def test_post_training_success(client):
    response = client.post(
        "/training",
        json={"training_date": "2026-10-16", "shots": 10, "made": 7},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["record_id"] > 0
    assert body == {
        "message": "训练记录保存成功",
        "training": {
            "date": "2026-10-16",
            "shots": 10,
            "made": 7,
            "percentage": 70.0,
        },
        "record_id": body["record_id"],
    }


def test_get_training_by_date_no_records(client):
    response = client.get(
        "/training-by-date", params={"training_date": "2026-10-18"}
    )
    assert response.status_code == 200
    assert response.json() == {"training_date": "2026-10-18", "records": []}


def test_get_training_by_date_with_records(client):
    response = client.get(
        "/training-by-date", params={"training_date": "2026-10-15"}
    )
    assert response.status_code == 200
    assert response.json()["records"] == [
        {"id": 1, "date": "2026-10-15", "shots": 10, "made": 8}
    ]


def test_get_training_by_date_invalid_date(client):
    response = client.get(
        "/training-by-date", params={"training_date": "not-a-date"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_training_end_to_end(client):
    training_date = "2026-10-15"
    created = client.post(
        "/training",
        json={"training_date": training_date, "shots": 5, "made": 2},
    )
    assert created.status_code == 201
    new_record = {
        "id": created.json()["record_id"],
        "date": training_date,
        "shots": 5,
        "made": 2,
    }

    legacy = client.get(
        "/training-by-date", params={"training_date": training_date}
    )
    v2 = client.get(
        "/v2/training-by-date",
        params={"training_date": training_date, "user_id": 1},
    )
    assert legacy.status_code == v2.status_code == 200
    assert legacy.json()["records"] == v2.json()["records"] == [
        {"id": 1, "date": training_date, "shots": 10, "made": 8},
        new_record,
    ]

    legacy_summary = client.get("/training-summary")
    v2_summary = client.get("/v2/training-summary", params={"user_id": 1})
    assert legacy_summary.status_code == v2_summary.status_code == 200
    summary = legacy_summary.json()
    assert summary == v2_summary.json()
    assert summary["training_days"] == 1
    assert summary["shots"] == 15
    assert summary["made"] == 10
    assert summary["percentage"] == 66.7


def test_training_summary_limit(client):
    explicit = client.get("/training-summary", params={"limit": 3})
    default = client.get("/training-summary")
    assert explicit.status_code == default.status_code == 200
    assert explicit.json()["required_training_days"] == 3
    assert default.json()["required_training_days"] == 5

    for invalid_limit in (0, -2):
        response = client.get("/training-summary", params={"limit": invalid_limit})
        assert response.status_code == 422
