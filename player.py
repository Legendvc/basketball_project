import json
from datetime import date
from utils import calculate_percentage, evaluate_shooting


class Player:

    def __init__(self, name, age, position):
        self.name = name
        self.age = age
        self.position = position

        self.shots = 0
        self.made = 0

        self.sex = "未知"
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

    def show_level(self):

        percentage = calculate_percentage(
            self.made,
            self.shots
    )

        if   percentage >= 80:
               level = "A"
        elif percentage >= 60:
               level = "B"
        else:
              level = "C"

        print("球员等级：", level)

        
        print("===== 球员资料 =====")
        print("姓名：", self.name)
        print("年龄：", self.age)
        print("位置：", self.position)
        print("投篮次数：", self.shots)
        print("命中次数：", self.made)
        print("命中率：", percentage, "%")
        print("评价：", evaluate_shooting(percentage))
        print("球员身份：篮球运动员")
        print("性别：", self.sex)

    def save_training(self):
        percentage = calculate_percentage(
        self.made,
        self.shots
        )

        training =   {
            "date": str(date.today()),
            "shots": self.shots,
            "made": self.made,
            "percentage": percentage
      
        }

        self.training_history.append(training)

    def save_sex(self):
        self.sex = input("请输入性别：")
        self.save()

        
    def show_training_history(self):

        if len(self.training_history) == 0:
            print("暂无训练记录")
            return

        print("===== 训练历史 =====")

        for training in self.training_history:
            print("日期：", training.get("date", "未知日期"))
            print("投篮次数：", training["shots"])
            print("命中次数：", training["made"])
            print("命中率：", training["percentage"], "%")
            print("--------------------")

    def save(self):
        data = {
            "name": self.name,
            "age": self.age,
            "position": self.position,
            "shots": self.shots,
            "made": self.made,
            "sex": self.sex,
            "training_history": self.training_history
        }

        with open("player.json", "w",encoding="utf-8") as file:
            json.dump(data, file, indent=4,ensure_ascii=False)

    def show_history_summary(self):

        if len(self.training_history) == 0:
            print("暂无训练记录")
            return

        total_percentage = 0

        for training in self.training_history:
            total_percentage += training["percentage"]

        average_percentage = total_percentage / len(self.training_history)

        print("===== 训练汇总 =====")
        print("训练次数：", len(self.training_history))
        print("平均命中率：", average_percentage, "%")

  
    @classmethod
    def load(cls):
        try:
            with open("player.json", "r",encoding="utf-8") as file:
                data = json.load(file)

            player = cls(
            data["name"],
            data["age"],
            data["position"]
            )

            player.shots = data["shots"]
            player.made = data["made"]
            player.sex = data.get("sex", "未知")
            player.training_history = data.get(
               "training_history",
               []
            ) 

            return player

        except (FileNotFoundError, json.JSONDecodeError):
             return cls(
            "Richard",
            31,
            "SG"
        )