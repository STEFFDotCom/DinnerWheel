import random

dinners = ["Steak", "Pasta", "Lasagna"]

def choose_dinner(dinner_options):
    return random.choice(dinner_options)

result = choose_dinner(dinners)
print(result)

def save_dinner_to_file(dinner_to_save):
    with open("dinner_log.txt", "a") as file:
        file.write(f"Tonights Dinner: {dinner_to_save}" + "\n")

save_dinner_to_file(result)