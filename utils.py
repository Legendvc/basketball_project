def calculate_percentage(made, shots):
    if shots == 0:
        return 0

    return made / shots * 100

def evaluate_shooting(percentage):
    if percentage >= 90:
        return "NBA级别"

    elif percentage >= 80:
        return "优秀"

    elif percentage >= 60:
        return "良好"

    else:
        return "继续训练"