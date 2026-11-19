"""Training statistics independent of player profiles, HTTP, and storage."""
from datetime import date

from utils import calculate_percentage

EFFECTIVE_TRAINING_DAY_MIN_SHOTS = 5
RECENT_EFFECTIVE_TRAINING_DAY_LIMIT = 5


class TrainingSummary:
    def __init__(self, training_history):
        self.training_history = training_history

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

        training_date = TrainingSummary._parse_training_date(training.get("date"))
        if training_date is None:
            return None, f"{record_label}日期无效，已跳过"

        try:
            shots = TrainingSummary._parse_training_count(training.get("shots", 0))
            made = TrainingSummary._parse_training_count(training.get("made", 0))
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

    def get_best_recent_effective_training_day(
            self,
            limit=RECENT_EFFECTIVE_TRAINING_DAY_LIMIT):

        recent_training_days = self.get_recent_effective_training_days(
            limit=limit
        )

        if not recent_training_days:
            return None

        return max(
            recent_training_days,
            key=lambda training: (
                training["percentage"],
                training["date"]
        )
    )

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
