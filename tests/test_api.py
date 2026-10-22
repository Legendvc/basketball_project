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


def test_post_training_success(monkeypatch):
    player = Player("Test", 20, "SG")
    saved = []
    db_records = []

    def fake_load():
        return player

    def fake_save(self):
        saved.append(True)

    def fake_save_training_record(training_date, shots, made):
        db_records.append((training_date, shots, made))
        return 123

    monkeypatch.setattr(Player, "load_from_json", fake_load)
    monkeypatch.setattr(Player, "save_to_json", fake_save)
    monkeypatch.setattr(
        "api.save_training_record",
        fake_save_training_record
    )

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
    assert response.json()["record_id"] == 123
    assert len(player.training_history) == 1
    assert saved == [True]
    assert db_records == [("2026-10-15", 10, 7)]


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


def test_get_training_by_date_with_records(monkeypatch):
    def fake_get_training_by_date(training_date):
        return [
            {
                "id": 1,
                "date": "2026-10-15",
                "shots": 10,
                "made": 8
            }
        ]

    monkeypatch.setattr(
        "api.get_training_by_date",
        fake_get_training_by_date
    )

    response = client.get(
        "/training-by-date",
        params={"training_date": "2026-10-15"}
    )

    assert response.status_code == 200
    assert response.json()["records"][0]["made"] == 8


def test_get_training_by_date_invalid_date():
    response = client.get(
        "/training-by-date",
        params={"training_date": "not-a-date"}
    )

    assert response.status_code == 422
    assert "detail" in response.json()

import sqlite3
import db_utils


def test_training_end_to_end(tmp_path, monkeypatch):
    # 1. 创建临时数据库
    db_file = tmp_path / "test_api.db"
    monkeypatch.setattr(db_utils, "DB_FILE", str(db_file))

    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE training (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            shots INTEGER NOT NULL,
            made INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    # 2. 模拟 JSON 读写，保护真实文件
    player = Player("Test", 20, "SG")
    monkeypatch.setattr(
        Player, "load_from_json", lambda: player
    )
    monkeypatch.setattr(
        Player, "save_to_json", lambda self: None
    )

    # 3. POST 保存训练记录
    response = client.post(
        "/training",
        json={
            "training_date": "2026-10-20",
            "shots": 10,
            "made": 8
        }
    )

    assert response.status_code == 201
    record_id = response.json()["record_id"]

    # 4. GET 查询刚保存的记录
    response = client.get(
        "/training-by-date",
        params={"training_date": "2026-10-20"}
    )

    assert response.status_code == 200
    records = response.json()["records"]

    assert len(records) == 1
    assert records[0]["id"] == record_id
    assert records[0]["shots"] == 10
    assert records[0]["made"] == 8

def test_training_summary_limit(monkeypatch):
    player = Player("Test", 20, "SG")
    received_limits = []

    def fake_summary(limit=5):
        received_limits.append(limit)
        return {"limit": limit}

    monkeypatch.setattr(Player, "load_from_json", lambda: player)
    monkeypatch.setattr(
        player,
        "get_recent_effective_training_days_summary",
        fake_summary
    )

    # 指定 limit=3
    response = client.get("/training-summary?limit=3")
    assert response.status_code == 200
    assert response.json()["limit"] == 3

    # 不指定 limit，应该使用默认值 5
    response = client.get("/training-summary")
    assert response.status_code == 200
    assert response.json()["limit"] == 5

    # limit=0 应返回 422
    response = client.get("/training-summary?limit=0")
    assert response.status_code == 422

    # 负数也应返回 422
    response = client.get("/training-summary?limit=-2")
    assert response.status_code == 422

    assert received_limits == [3, 5]