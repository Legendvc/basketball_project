from datetime import date
from json import JSONDecodeError

from utils import calculate_percentage, evaluate_shooting
from storage import save_json, load_json
from training_summary import (
    EFFECTIVE_TRAINING_DAY_MIN_SHOTS,
    RECENT_EFFECTIVE_TRAINING_DAY_LIMIT,
    TrainingSummary,
)

PLAYER_FILE = "player.json"


class Player:

    def __init__(self, name, age, position):
        self.name = name
        self.age = age
        self.position = position

        self.shots = 0
        self.made = 0

        self.gender = "未知"
        self.training_history = []

    def shoot(self, is_made):
        self.shots += 1

        if is_made:
            self.made += 1

    def reset_stats(self):
        self.shots = 0
        self.made = 0

    def show_info(self):
        percentage = calculate_percentage(
            self.made,
            self.shots
        )

    def show_training(self, training):
        print("日期：", training.get("date", "未知日期"))
        print("投篮次数：", training["shots"])
        print("命中次数：", training["made"])
        print("命中率：", training["percentage"], "%")
        print("--------------------")

    def show_level(self):

        percentage = calculate_percentage(
            self.made,
            self.shots
        )

        if percentage >= 80:
            level = "A"
        elif percentage >= 60:
            level = "B"
        else:
            level = "C"

        print("球员等级：", level)

        print("====== 球员资料 ======")
        print("姓名：", self.name)
        print("年龄：", self.age)
        print("位置：", self.position)
        print("投篮次数：", self.shots)
        print("命中次数：", self.made)
        print("命中率：", percentage, "%")
        print("评价：", evaluate_shooting(percentage))
        print("球员身份：篮球运动员")
        print("性别：", self.gender)

    def get_percentage(self):
        return calculate_percentage(
            self.made,
            self.shots
        )
    def get_level(self):
        percentage = self.get_percentage()

        if percentage >= 80:
            return "A"
        elif percentage >= 60:
            return "B"
        else:
            return "C"

    def save_training(self):
        percentage = self.get_percentage()

        training = {
            "date": str(date.today()),
            "shots": self.shots,
            "made": self.made,
            "percentage": percentage
        }

        self.training_history.append(training)

    def add_training_record(self, training_date, shots, made):
        percentage = calculate_percentage(made, shots)

        training = {
            "date": str(training_date),
            "shots": shots,
            "made": made,
            "percentage": percentage
        }

        self.training_history.append(training)

        return training

    def save_gender(self):
        self.gender = input("请输入性别：")
        self.save_to_json()

    def show_training_history(self):

        if not self.training_history:
            print("暂无训练记录")
            return

        print("===== 训练历史 =====")

        for training in self.training_history:
            self.show_training(training)

    @staticmethod
    def _parse_training_date(date_value):
        return TrainingSummary._parse_training_date(date_value)

    @staticmethod
    def _parse_training_count(value):
        return TrainingSummary._parse_training_count(value)

    @staticmethod
    def _get_training_stats(training, record_number=None):
        return TrainingSummary._get_training_stats(training, record_number=record_number)

    def _group_training_by_date(self):
        return TrainingSummary(self.training_history)._group_training_by_date()

    def _get_recent_effective_training_days_with_messages(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT,
            min_shots=EFFECTIVE_TRAINING_DAY_MIN_SHOTS):
        return TrainingSummary(self.training_history)._get_recent_effective_training_days_with_messages(
            limit=limit,
            min_shots=min_shots,
        )

    def get_recent_effective_training_days(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT,
            min_shots=EFFECTIVE_TRAINING_DAY_MIN_SHOTS):
        return TrainingSummary(self.training_history).get_recent_effective_training_days(
            limit=limit,
            min_shots=min_shots,
        )
    def get_best_recent_effective_training_day(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT):

        return TrainingSummary(self.training_history).get_best_recent_effective_training_day(
            limit=limit,
        )
    def get_recent_effective_training_days_summary(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT):
        return TrainingSummary(self.training_history).get_recent_effective_training_days_summary(
            limit=limit,
        )

    def show_recent_effective_training_days(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT):
        summary = self.get_recent_effective_training_days_summary(limit)
        recent_training_days = summary["days"]

        print(f"===== 最近{limit}个有效训练日总体命中率 =====")

        for message in summary["messages"]:
            print("提示：", message)

        if not summary["has_data"]:
            return

        for training in recent_training_days:
            self.show_training(training)

        print("有效训练日数：", summary["training_days"])
        print("总投篮次数：", summary["shots"])
        print("总命中次数：", summary["made"])
        print("总体命中率：", summary["percentage"], "%")

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "position": self.position,
            "shots": self.shots,
            "made": self.made,
            "gender": self.gender,
            "training_history": self.training_history
        }

    def save_to_json(self):
        save_json(
            PLAYER_FILE,
            self.to_dict()
        )

    def save(self):
        self.save_to_json()

    def get_history_summary(self):

        if not self.training_history:
            return 0, 0

        total_percentage = 0

        for training in self.training_history:
            total_percentage += training["percentage"]

        average_percentage = total_percentage / len(self.training_history)

        return len(self.training_history), average_percentage

    def show_history_summary(self):

        if not self.training_history:
            print("暂无训练记录")
            return

        training_count, average_percentage = self.get_history_summary()

        print("===== 训练汇总 =====")
        print("训练次数：", training_count)
        print("平均命中率：", average_percentage, "%")

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            return cls("Richard", 31, "SG")

        player = cls(
            data.get("name", "Richard"),
            data.get("age", 31),
            data.get("position", "SG")
        )

        player.shots = data.get("shots", 0)
        player.made = data.get("made", 0)
        player.gender = data.get("gender", "未知")
        player.training_history = data.get("training_history", [])

        if not isinstance(player.training_history, list):
            player.training_history = []

        return player

    @classmethod
    def load_from_json(cls):
        try:
            data = load_json(PLAYER_FILE)
        except (FileNotFoundError, JSONDecodeError):
            return cls("Richard", 31, "SG")

        return cls.from_dict(data)
