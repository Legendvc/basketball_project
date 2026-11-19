from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from player import Player
from training_repository import create_training, get_trainings_by_user
from utils import calculate_percentage


def get_user_id(session: Session, username: str) -> int:
    user_id = session.scalar(select(User.id).where(User.username == username))
    if user_id is None:
        raise LookupError(f"数据库中找不到球员：{username}")
    return user_id


def save_training(player: Player) -> None:
    with SessionLocal.begin() as session:
        create_training(
            session=session,
            training_date=date.today().isoformat(),
            shots=player.shots,
            made=player.made,
            user_id=get_user_id(session, player.name),
        )


def load_training_history(username: str) -> list[dict]:
    with SessionLocal() as session:
        records = get_trainings_by_user(session, get_user_id(session, username))
        return [
            {
                "date": record.date,
                "shots": record.shots,
                "made": record.made,
                "percentage": calculate_percentage(record.made, record.shots),
            }
            for record in records
        ]


def main() -> None:
    player = Player.load_from_json()

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
        print("8. 请输入性别")
        print("9. 保存并退出")

        choice = input("请选择：")

        if choice == "1":
            player.show_info()
            player.show_level()
        elif choice == "2":
            player.shoot(True)
            print("已记录：命中")
        elif choice == "3":
            player.shoot(False)
            print("已记录：未命中")
        elif choice in {"4", "5", "6"}:
            try:
                if choice == "4":
                    save_training(player)
                    print("本次训练已加入历史记录")
                    continue
                history = load_training_history(player.name)
            except LookupError as error:
                print(error)
                continue
            except SQLAlchemyError:
                print("无法访问训练数据库，请检查数据库配置和迁移状态")
                continue

            if not history:
                print("暂无训练记录")
            elif choice == "5":
                print("===== 训练历史 =====")
                for record in history:
                    player.show_training(record)
            else:
                average = sum(record["percentage"] for record in history) / len(history)
                print("===== 训练汇总 =====")
                print("训练次数：", len(history))
                print("平均命中率：", average, "%")
        elif choice == "7":
            player.reset_stats()
            print("训练数据已重置")
        elif choice == "8":
            player.save_gender()
            print("性别已更新")
        elif choice == "9":
            player.save()
            print("球员资料已保存")
            break


if __name__ == "__main__":
    main()
