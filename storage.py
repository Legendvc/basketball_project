import json


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)