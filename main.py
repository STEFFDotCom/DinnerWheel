import random
import os
import datetime

today = datetime.date.today()
formatted = today.strftime("%d-%m-%Y")

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Declare a base directory that is the same folder as our py script
LOG_FILE = os.path.join(BASE_DIR, "dinner_log.txt") # Make dinner_log.txt use the base directory

dinners = ["Steak", "Pasta", "Lasagna"] # Our dinner list

def choose_dinner(dinner_options): # function to return random dinner
    return random.choice(dinner_options)

result = choose_dinner(dinners)
print(result)

def save_dinner_to_file(dinner_to_save): # function to save dinner to our file
    with open(LOG_FILE, "a") as file:
        file.write(f"Tonights Dinner: {dinner_to_save}" + "\n")

save_dinner_to_file(result)

def read_dinner_log(): # function to read dinner log and clean it

    cleaned_lines = []

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        cleaned_line = line.strip()
        cleaned_lines.append(cleaned_line)

    return cleaned_lines

print(read_dinner_log()) # cleaned dinner log as a list

print(formatted)