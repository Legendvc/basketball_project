import pytest

from player import Player


@pytest.fixture
def player():

    return Player(
        "Richard",
        31,
        "SG"
    )