def calculate_percentage(made, shots):
    if shots == 0:
        return 0

    return made / shots * 100

def evaluate_shooting(percentage):
    if percentage >= 70:
        return "优秀"   
    elif percentage >= 40:
        return "良好"   
    else:
         return "需要改进"