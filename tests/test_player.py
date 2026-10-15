from player import Player


def test_player_shoot(player):

    player.shoot(True)

    assert player.shots == 1
    assert player.made == 1


def test_player_miss(player):

    player.shoot(False)

    assert player.shots == 1
    assert player.made == 0


def test_player_training(player):

    player.shoot(True)
    player.shoot(True)
    player.shoot(False)

    assert player.shots == 3
    assert player.made == 2


def test_get_history_summary(player):

    player.training_history = [
        {"percentage": 80.0},
        {"percentage": 60.0}
    ]

    training_count, average_percentage = player.get_history_summary()

    assert training_count == 2
    assert average_percentage == 70.0


def test_get_history_summary_empty(player):

    player.training_history = []

    training_count, average_percentage = player.get_history_summary()

    assert training_count == 0
    assert average_percentage == 0


def test_recent_effective_training_days_acceptance_normal_calculation(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 6, "shots": 10},
        {"date": "2026-06-05", "made": 8, "shots": 10},
        {"date": "2026-06-02", "made": 6, "shots": 10},
        {"date": "2026-06-04", "made": 7, "shots": 10},
        {"date": "2026-06-03", "made": 4, "shots": 5}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert summary["has_data"] is True
    assert summary["training_days"] == 5
    assert summary["made"] == 31
    assert summary["shots"] == 45
    assert summary["percentage"] == 68.9
    assert summary["is_reference_only"] is False
    assert [day["date"] for day in summary["days"]] == [
        "2026-06-05",
        "2026-06-04",
        "2026-06-03",
        "2026-06-02",
        "2026-06-01"
    ]


def test_best_recent_effective_training_day_returns_highest_percentage(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 6, "shots": 10},
        {"date": "2026-06-02", "made": 8, "shots": 10},
        {"date": "2026-06-03", "made": 7, "shots": 10}
    ]

    best_training_day = player.get_best_recent_effective_training_day()

    assert best_training_day == {
        "date": "2026-06-02",
        "shots": 10,
        "made": 8,
        "percentage": 80.0
    }


def test_best_recent_effective_training_day_returns_newer_day_when_tied(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 4, "shots": 5},
        {"date": "2026-06-03", "made": 8, "shots": 10},
        {"date": "2026-06-02", "made": 3, "shots": 5}
    ]

    best_training_day = player.get_best_recent_effective_training_day()

    assert best_training_day["date"] == "2026-06-03"
    assert best_training_day["percentage"] == 80.0


def test_best_recent_effective_training_day_returns_none_without_effective_days(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 2, "shots": 4}
    ]

    assert player.get_best_recent_effective_training_day() is None


def test_recent_effective_training_days_acceptance_insufficient_data(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 3, "shots": 5},
        {"date": "2026-06-02", "made": 4, "shots": 5}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert summary["training_days"] == 2
    assert summary["made"] == 7
    assert summary["shots"] == 10
    assert summary["percentage"] == 70.0
    assert summary["is_reference_only"] is True
    assert any("有效训练日不足 5 个" in message for message in summary["messages"])
    assert any("结果仅供参考" in message for message in summary["messages"])


def test_recent_effective_training_days_acceptance_missing_date_warning(player):

    player.training_history = [
        {"made": 5, "shots": 10},
        {"date": "2026-06-01", "made": 3, "shots": 5},
        {"date": "2026-06-02", "made": 4, "shots": 5}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert summary["made"] == 7
    assert summary["shots"] == 10
    assert summary["percentage"] == 70.0
    assert any("缺失日期" in warning for warning in summary["warnings"])


def test_recent_effective_training_days_acceptance_same_day_merge(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 6, "shots": 10},
        {"date": "2026-06-01", "made": 5, "shots": 10}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert summary["training_days"] == 1
    assert summary["made"] == 11
    assert summary["shots"] == 20
    assert summary["percentage"] == 55.0
    assert summary["days"] == [
        {
            "date": "2026-06-01",
            "shots": 20,
            "made": 11,
            "percentage": 55.0
        }
    ]


def test_recent_effective_training_days_merge_before_filter(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 1, "shots": 2},
        {"date": "2026-06-01", "made": 2, "shots": 3}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert summary["has_data"] is True
    assert summary["training_days"] == 1
    assert summary["shots"] == 5
    assert summary["made"] == 3
    assert summary["percentage"] == 60.0
    assert summary["days"] == [
        {
            "date": "2026-06-01",
            "shots": 5,
            "made": 3,
            "percentage": 60.0
        }
    ]


def test_recent_effective_training_days_returns_latest_five_only(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 5, "shots": 10},
        {"date": "2026-06-02", "made": 5, "shots": 10},
        {"date": "2026-06-03", "made": 5, "shots": 10},
        {"date": "2026-06-04", "made": 5, "shots": 10},
        {"date": "2026-06-05", "made": 5, "shots": 10},
        {"date": "2026-06-06", "made": 8, "shots": 10}
    ]

    recent_days = player.get_recent_effective_training_days()
    summary = player.get_recent_effective_training_days_summary()

    assert [day["date"] for day in recent_days] == [
        "2026-06-06",
        "2026-06-05",
        "2026-06-04",
        "2026-06-03",
        "2026-06-02"
    ]
    assert summary["made"] == 28
    assert summary["shots"] == 50
    assert summary["percentage"] == 56.0


def test_recent_effective_training_days_excludes_dates_below_minimum_after_merge(player):

    player.training_history = [
        {"date": "2026-06-01", "made": 2, "shots": 3},
        {"date": "2026-06-01", "made": 1, "shots": 1},
        {"date": "2026-06-02", "made": 5, "shots": 5}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert [day["date"] for day in summary["days"]] == ["2026-06-02"]
    assert any("2026-06-01" in notice for notice in summary["notices"])
    assert any("少于 5 次" in notice for notice in summary["notices"])


def test_recent_effective_training_days_excludes_illegal_shooting_data(player):

    player.training_history = [
        {"date": "2026-06-01", "made": -1, "shots": 5},
        {"date": "2026-06-02", "made": 6, "shots": 5},
        {"date": "2026-06-03", "made": 3, "shots": -5},
        {"date": "2026-06-04", "made": "abc", "shots": 5},
        {"date": "2026-06-05", "made": 4, "shots": 5}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert [day["date"] for day in summary["days"]] == ["2026-06-05"]
    assert summary["made"] == 4
    assert summary["shots"] == 5
    assert len(summary["warnings"]) == 4
    assert any("不能为负数" in warning for warning in summary["warnings"])
    assert any("命中数不能大于投篮数" in warning for warning in summary["warnings"])
    assert any("不是整数" in warning for warning in summary["warnings"])


def test_recent_effective_training_days_handles_invalid_dates(player):

    player.training_history = [
        {"date": "not-a-date", "made": 5, "shots": 10},
        {"date": "2026-13-01", "made": 5, "shots": 10},
        {"date": "2026-06-01", "made": 4, "shots": 5}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert [day["date"] for day in summary["days"]] == ["2026-06-01"]
    assert summary["percentage"] == 80.0
    assert len(summary["warnings"]) == 2
    assert all("日期无效" in warning for warning in summary["warnings"])


def test_recent_effective_training_days_handles_no_valid_data(player):

    player.training_history = [
        {"made": 5, "shots": 10},
        {"date": "bad-date", "made": 5, "shots": 10},
        {"date": "2026-06-01", "made": 2, "shots": 4}
    ]

    summary = player.get_recent_effective_training_days_summary()

    assert summary["has_data"] is False
    assert summary["training_days"] == 0
    assert summary["made"] == 0
    assert summary["shots"] == 0
    assert summary["percentage"] == 0
    assert summary["days"] == []
    assert any("暂无有效训练数据" in message for message in summary["messages"])


def test_show_recent_effective_training_days_prints_user_messages(player, capsys):

    player.training_history = [
        {"made": 5, "shots": 10},
        {"date": "2026-06-01", "made": 3, "shots": 5},
        {"date": "2026-06-02", "made": 4, "shots": 5}
    ]

    player.show_recent_effective_training_days()

    output = capsys.readouterr().out

    assert "缺失日期" in output
    assert "有效训练日不足 5 个" in output
    assert "结果仅供参考" in output
    assert "总体命中率" in output
