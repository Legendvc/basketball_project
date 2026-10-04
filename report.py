def generate_report(player):

    print("===== 训练报告 =====")

    print("球员：", player.name)

    print("训练次数：",
          len(player.training_history))

    total = 0

    for training in player.training_history:
        total += training["percentage"]

    if len(player.training_history) > 0:
        average = total / len(player.training_history)
    else:
        average = 0

    print("平均命中率：", average, "%")