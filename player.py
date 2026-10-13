from datetime import date
from json import JSONDecodeError

from utils import calculate_percentage, evaluate_shooting
from storage import save_json, load_json

PLAYER_FILE = "player.json"
EFFECTIVE_TRAINING_DAY_MIN_SHOTS = 5
RECENT_EFFECTIVE_TRAINING_DAY_LIMIT = 5


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

    def save_training(self):
        percentage = self.get_percentage()

        training = {
            "date": str(date.today()),
            "shots": self.shots,
            "made": self.made,
            "percentage": percentage
        }

        self.training_history.append(training)

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
        if not date_value:
            return None

        try:
            return date.fromisoformat(str(date_value))
        except ValueError:
            return None

    @staticmethod
    def _parse_training_count(value):
        if isinstance(value, bool):
            raise ValueError("bool is not a valid count")

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            stripped_value = value.strip()

            if stripped_value.startswith("-"):
                number_part = stripped_value[1:]
            else:
                number_part = stripped_value

            if number_part.isdigit():
                return int(stripped_value)

        raise ValueError("count is not an integer")

    @staticmethod
    def _get_training_stats(training, record_number=None):
        record_label = "训练记录"

        if record_number is not None:
            record_label = f"第 {record_number} 条记录"

        if not isinstance(training, dict):
            return None, f"{record_label}格式无效，已跳过"

        if not training.get("date"):
            return None, f"{record_label}缺失日期，已跳过"

        training_date = Player._parse_training_date(training.get("date"))
        if training_date is None:
            return None, f"{record_label}日期无效，已跳过"

        try:
            shots = Player._parse_training_count(training.get("shots", 0))
            made = Player._parse_training_count(training.get("made", 0))
        except ValueError:
            return None, f"{record_label}投篮数据不是整数，已跳过"

        if shots < 0 or made < 0:
            return None, f"{record_label}投篮数据不能为负数，已跳过"

        if made > shots:
            return None, f"{record_label}命中数不能大于投篮数，已跳过"

        return (training_date, shots, made), None

    def _group_training_by_date(self):
        grouped_by_date = {}
        warnings = []

        for index, training in enumerate(self.training_history, start=1):
            training_stats, warning = self._get_training_stats(
                training,
                record_number=index
            )

            if warning:
                warnings.append(warning)
                continue

            training_date, shots, made = training_stats

            if training_date not in grouped_by_date:
                grouped_by_date[training_date] = {
                    "shots": 0,
                    "made": 0
                }

            grouped_by_date[training_date]["shots"] += shots
            grouped_by_date[training_date]["made"] += made

        return grouped_by_date, warnings

    def _get_recent_effective_training_days_with_messages(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT,
            min_shots=EFFECTIVE_TRAINING_DAY_MIN_SHOTS):
        grouped_by_date, warnings = self._group_training_by_date()
        notices = []
        effective_training_days = []

        if limit <= 0:
            return effective_training_days, warnings, notices

        for training_date in sorted(grouped_by_date.keys(), reverse=True):
            shots = grouped_by_date[training_date]["shots"]
            made = grouped_by_date[training_date]["made"]

            if shots < min_shots:
                notices.append(
                    f"{training_date.isoformat()} 合并后投篮次数为 {shots}，"
                    f"少于 {min_shots} 次，不计入有效训练日"
                )
                continue

            effective_training_days.append({
                "date": training_date.isoformat(),
                "shots": shots,
                "made": made,
                "percentage": round(calculate_percentage(made, shots), 1)
            })

        return effective_training_days[:limit], warnings, notices

    def get_recent_effective_training_days(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT,
            min_shots=EFFECTIVE_TRAINING_DAY_MIN_SHOTS):
        recent_training_days, warnings, notices = (
            self._get_recent_effective_training_days_with_messages(
                limit=limit,
                min_shots=min_shots
            )
        )

        return recent_training_days

    def get_recent_effective_training_days_summary(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT):
        recent_training_days, warnings, notices = (
            self._get_recent_effective_training_days_with_messages(
                limit=limit
            )
        )

        total_shots = 0
        total_made = 0

        for training in recent_training_days:
            total_shots += training["shots"]
            total_made += training["made"]

        has_data = total_shots > 0
        is_reference_only = has_data and len(recent_training_days) < limit
        messages = []
        messages.extend(warnings)
        messages.extend(notices)

        if not has_data:
            messages.append("暂无有效训练数据")
        elif is_reference_only:
            messages.append(f"有效训练日不足 {limit} 个，结果仅供参考")

        return {
            "has_data": has_data,
            "training_days": len(recent_training_days),
            "required_training_days": limit,
            "is_reference_only": is_reference_only,
            "shots": total_shots,
            "made": total_made,
            "percentage": round(calculate_percentage(total_made, total_shots), 1),
            "days": recent_training_days,
            "warnings": warnings,
            "notices": notices,
            "messages": messages
        }

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
