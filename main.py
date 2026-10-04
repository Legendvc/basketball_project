from player import Player


player = Player.load()


while True:

    print()
    print("===== 篮球训练系统 =====")
    print("1. 查看球员信息")
    print("2. 记录一次命中")
    print("3. 记录一次未命中")
    print("4. 保存本次训练")
    print("5. 查看训练历史")
    print("6. 查看训练汇总")
    print("7. 重置训练数据")
    print("8  请输入性别")
    print("9. 保存并退出")

    choice = input("请选择：")


    if choice == "1":
        player.show_info()

    elif choice == "2":
        player.shoot(True)
        print("已记录：命中")

    elif choice == "3":
        player.shoot(False)
        print("已记录：未命中")

    elif choice == "4":
        player.save_training()
        print("本次训练已加入历史记录")

    elif choice == "5":
        player.show_training_history()

    elif choice == "6":
         player.show_history_summary()

    elif choice == "7":
        player.reset_stats()
        print("训练数据已重置")

    elif choice == "8":
         player.save_sex()
         print("性别已更新")

    elif choice == "9":
         player.save()
         print("数据已保存")
    break