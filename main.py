import random
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Declare a base directory that is the same folder as our py script
LOG_FILE = os.path.join(BASE_DIR, "dinner_log.txt") # Make dinner_log.txt use the base directory

dinners = ["Steak", "Pasta", "Lasagna", "Chicken", "Meatballs", "Tacos", "Sandwich"] # Our dinner list

def choose_dinner(dinner_options): # function to return random dinner
    return random.choice(dinner_options)

def log_event(event_type, person, dinner): # function to save dinner to our file

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    log_file_line = f"{todaysDate},{event_type},{person},{dinner}\n"

    with open(LOG_FILE, "a") as file:
        file.write(log_file_line)

def read_dinner_log(): # function to read dinner log and clean it

    cleaned_lines = []

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        cleaned_line = line.strip()
        cleaned_lines.append(cleaned_line)

    return cleaned_lines

print(read_dinner_log()) # cleaned dinner log as a list

def dinner_already_chosen_today(): # check if todays dinner was already choosen
    
    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    if not os.path.exists(LOG_FILE):
        return False # No File = no dinner yet
    
    with open(LOG_FILE, "r") as file:
        for line in file:
            stripped_line = line.strip()
            split_line = stripped_line.split(",")

            if len(split_line) == 4 and split_line[0] == todaysDate:
                return True
    
    return False

def get_used_dinners_today():

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    used_dinners = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            for line in file:
                stripped_line = line.strip()
                split_line = stripped_line.split(",")

                if len(split_line) == 4 and split_line[0] == todaysDate:
                    used_dinners.append(split_line[3])
                else:
                    continue
    else:
        return []
    
    unique_used_dinners = set(used_dinners) # remove duplicates

    return list(unique_used_dinners)

if dinner_already_chosen_today():
    print("Dinner has already been chosen today 🍽️")
else:
    result = choose_dinner(dinners)
    print(result)
    log_event("event_type", "person", result)



