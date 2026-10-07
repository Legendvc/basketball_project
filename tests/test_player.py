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