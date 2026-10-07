from utils import calculate_percentage, evaluate_shooting


def test_calculate_percentage():

    result = calculate_percentage(7, 10)

    assert result == 70


def test_zero_shots():

    result = calculate_percentage(0, 0)

    assert result == 0

def test_evaluate_excellent():
    result = evaluate_shooting(80)

    assert result == "优秀！"


def test_evaluate_good():
    result = evaluate_shooting(60)

    assert result == "良好！"


def test_evaluate_needs_improvement():
    result = evaluate_shooting(30)

    assert result == "继续训练！"    