import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from api_orm_demo import app, get_db
from models import Base, Training, User


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    previous_overrides = app.dependency_overrides.copy()

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            richard = User(id=1, username="Richard")
            alice = User(id=2, username="Alice")

            session.add_all([
                Training(
                    id=101,
                    user=richard,
                    date="2026-10-15",
                    shots=10,
                    made=8,
                ),
                Training(
                    id=102,
                    user=alice,
                    date="2026-10-15",
                    shots=20,
                    made=12,
                ),
            ])
            session.commit()

            def override_get_db():
                with Session(engine) as session:
                    yield session

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


def test_training_by_date_returns_only_requested_user(client):
    response = client.get(
        "/training-by-date",
        params={"training_date": "2026-10-15", "user_id": 1},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "training_date": "2026-10-15",
        "records": [
            {
                "id": 101,
                "date": "2026-10-15",
                "shots": 10,
                "made": 8,
            }
        ],
    }


def test_training_by_date_returns_empty_list(client):
    response = client.get(
        "/training-by-date",
        params={"training_date": "2099-01-01", "user_id": 1},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": 1,
        "training_date": "2099-01-01",
        "records": [],
    }


def test_training_by_date_rejects_invalid_date(client):
    response = client.get(
        "/training-by-date",
        params={"training_date": "abc", "user_id": 1},
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        error["loc"] == ["query", "training_date"]
        for error in errors
    )


def test_training_by_date_rejects_invalid_user_id(client):
    response = client.get(
        "/training-by-date",
        params={"training_date": "2026-10-15", "user_id": 0},
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        error["loc"] == ["query", "user_id"]
        and error["type"] == "greater_than_equal"
        for error in errors
    )

def test_create_training_saves_record(client):
    response = client.post(
        "/training",
        json={
            "user_id": 1,
            "training_date": "2026-11-15",
            "shots": 12,
            "made": 9,
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["id"] > 0
    assert data == {
        "id": data["id"],
        "date": "2026-11-15",
        "shots": 12,
        "made": 9,
    }

    # 再发一次查询请求，确认写入已经提交。
    query_response = client.get(
        "/training-by-date",
        params={
            "training_date": "2026-11-15",
            "user_id": 1,
        },
    )

    assert query_response.status_code == 200
    assert query_response.json()["records"] == [data]
@pytest.mark.parametrize(
    "changes",
    [
        {"made": 11},       # 命中超过投篮次数
        {"shots": -1},      # 投篮次数为负数
        {"made": -1},       # 命中次数为负数
        {"shots": True},    # 布尔值不能充当投篮次数
    ],
)
def test_create_training_rejects_invalid_input(client, changes):
    payload = {
        "user_id": 1,
        "training_date": "2026-11-15",
        "shots": 10,
        "made": 8,
    }
    payload.update(changes)

    response = client.post("/training", json=payload)

    assert response.status_code == 422

    query_response = client.get(
        "/training-by-date",
        params={
            "training_date": "2026-11-15",
            "user_id": 1,
        },
    )

    assert query_response.status_code == 200
    assert query_response.json()["records"] == []


def test_create_training_rejects_unknown_user(client):
    response = client.post(
        "/training",
        json={
            "user_id": 999,
            "training_date": "2026-11-15",
            "shots": 10,
            "made": 8,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "用户不存在"}

    query_response = client.get(
        "/training-by-date",
        params={
            "training_date": "2026-11-15",
            "user_id": 999,
        },
    )

    assert query_response.status_code == 200
    assert query_response.json()["records"] == []


@pytest.mark.parametrize(
    "limit, reference_only, messages",
    [
        (1, False, []),
        (5, True, ["有效训练日不足 5 个，结果仅供参考"]),
    ],
)
def test_training_summary_uses_database_records(
    client,
    limit,
    reference_only,
    messages,
):
    response = client.get(
        "/training-summary",
        params={"user_id": 1, "limit": limit},
    )

    assert response.status_code == 200
    assert response.json() == {
        "has_data": True,
        "training_days": 1,
        "required_training_days": limit,
        "is_reference_only": reference_only,
        "shots": 10,
        "made": 8,
        "percentage": 80.0,
        "days": [
            {
                "date": "2026-10-15",
                "shots": 10,
                "made": 8,
                "percentage": 80.0,
            }
        ],
        "warnings": [],
        "notices": [],
        "messages": messages,
    }


def test_training_summary_rejects_invalid_limit(client):
    response = client.get(
        "/training-summary",
        params={"user_id": 1, "limit": 0},
    )

    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "limit"]
        and error["type"] == "greater_than_equal"
        for error in response.json()["detail"]
    )


def test_training_summary_rejects_unknown_user(client):
    response = client.get(
        "/training-summary",
        params={"user_id": 999},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "用户不存在"}

def test_new_training_updates_query_and_summary(client):
    created = client.post(
        "/training",
        json={
            "user_id": 1,
            "training_date": "2026-10-15",
            "shots": 5,
            "made": 2,
        },
    )
    assert created.status_code == 201
    new_id = created.json()["id"]

    queried = client.get(
        "/training-by-date",
        params={"user_id": 1, "training_date": "2026-10-15"},
    )
    assert queried.status_code == 200
    assert {
        record["id"] for record in queried.json()["records"]
    } == {101, new_id}

    summarized = client.get(
        "/training-summary",
        params={"user_id": 1, "limit": 1},
    )
    assert summarized.status_code == 200

    summary = summarized.json()
    assert summary["training_days"] == 1
    assert summary["shots"] == 15
    assert summary["made"] == 10
    assert summary["percentage"] == 66.7
    assert summary["days"] == [
        {
            "date": "2026-10-15",
            "shots": 15,
            "made": 10,
            "percentage": 66.7,
        }
    ]

@pytest.fixture
def main_client(client):
    from api import app as main_app

    with TestClient(main_app) as test_client:
        yield test_client


def test_main_application_serves_v2_summary(main_client):
    response = main_client.get(
        "/v2/training-summary",
        params={"user_id": 1, "limit": 1},
    )

    assert response.status_code == 200

    summary = response.json()
    assert summary["training_days"] == 1
    assert summary["shots"] == 10
    assert summary["made"] == 8
    assert summary["percentage"] == 80.0

    home = main_client.get("/")
    assert home.status_code == 200
    assert home.json()["project"] == "basketball_project"


def test_main_application_serves_v2_schema(main_client):
    response = main_client.get("/v2/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]
    assert "get" in paths["/training-by-date"]
    assert "post" in paths["/training"]
    assert "get" in paths["/training-summary"]

@pytest.fixture
def main_client(client):
    from api import app as main_app

    with TestClient(main_app) as test_client:
        yield test_client


def test_main_application_serves_v2_summary(main_client):
    response = main_client.get(
        "/v2/training-summary",
        params={"user_id": 1, "limit": 1},
    )

    assert response.status_code == 200

    summary = response.json()
    assert summary["training_days"] == 1
    assert summary["shots"] == 10
    assert summary["made"] == 8
    assert summary["percentage"] == 80.0

    home = main_client.get("/")
    assert home.status_code == 200
    assert home.json()["project"] == "basketball_project"


def test_main_application_serves_v2_schema(main_client):
    response = main_client.get("/v2/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]
    assert "get" in paths["/training-by-date"]
    assert "post" in paths["/training"]
    assert "get" in paths["/training-summary"]