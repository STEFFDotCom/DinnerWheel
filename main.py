import random
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # declare a base directory that is the same folder as our py script
LOG_FILE = os.path.join(BASE_DIR, "dinner_log.txt") # make dinner_log.txt use the base directory

dinners = ["Steak", "Pasta", "Lasagna", "Chicken", "Meatballs", "Tacos", "Sandwich"] # our dinner list

def choose_dinner(dinner_options): # function to return random dinner
    return random.choice(dinner_options)

def log_event(event_type, person, dinner): # function to save dinner to our file

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    log_file_line = f"{todaysDate},{event_type},{person},{dinner}\n"

    with open(LOG_FILE, "a") as file:
        file.write(log_file_line)

def read_dinner_log(): # function to read dinner log and clean it

    if not os.path.exists(LOG_FILE):
        print("FILE DOES NOT EXIST")
        return []

    cleaned_lines = []

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        cleaned_line = line.strip()
        split_lines = cleaned_line.split(",")
        cleaned_lines.append(split_lines)

    return cleaned_lines

def get_available_dinners():
    
    used_dinners = get_used_dinners_today()

    last_used_dinner = get_most_recent_final_dinner()

    available_dinners = []

    for dinner in dinners:
        if dinner not in used_dinners and dinner != last_used_dinner:
            available_dinners.append(dinner)

    return available_dinners

def get_used_dinners_today(): # return used dinners

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    log_file = read_dinner_log()

    used_dinners = []

    for line in log_file:
        if len(line) == 4 and line[0] == todaysDate:
            used_dinners.append(line[3])

    return list(set(used_dinners))

def get_spin_count_today(): # return hows many spins was done today

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    total_spins = 0

    log_lines = read_dinner_log()

    for line in log_lines:
        if line[0] == todaysDate and line[1] == "SPIN":
            total_spins += 1

    return total_spins

def run_spin_session():

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    log_lines = read_dinner_log()

    for line in log_lines: # Check if a final dinner has already been choosen
        if line[0] == todaysDate and line[1] == "FINAL":
            return None
        
    current_dinner = do_spin("SPIN", "None")

    if current_dinner is None:
        return None

    if not has_person_used_respin_today("Steffen"):
        spinSteffen = do_spin("RESPIN", "Steffen")
        if spinSteffen is not None:
            current_dinner = spinSteffen
        
    if not has_person_used_respin_today("Sabrina"):
        spinSabrina = do_spin("RESPIN", "Sabrina")
        if spinSabrina is not None:
            current_dinner = spinSabrina
        
    log_event("FINAL", "None", current_dinner)

    return current_dinner

def has_person_used_respin_today(person_name):

    log_lines = read_dinner_log()

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")
    
    for line in log_lines:
        if line[0] == todaysDate and line[1] == "RESPIN" and line[2] == person_name:
            return True
    
    return False

def do_spin(event_type, person_name):

    available_dinners = get_available_dinners()

    if len(available_dinners) == 0:
        return None

    dinner = choose_dinner(available_dinners)

    log_event(event_type, person_name, dinner)

    return dinner

def get_last_n_final_dinners(n = 5):

    last_5_dinners = []

    log_file = read_dinner_log()

    for line in log_file:
        if len(line) == 4 and line[1] == "FINAL":
            last_5_dinners.append((line[0], line[3]))

    return last_5_dinners[-n:]

def get_most_recent_final_dinner():

    log_file = read_dinner_log()

    for line in reversed(log_file):
        if line[1] == "FINAL":
            return line[3]
        
    return None


# -----------------
# MAIN PROGRAM FLOW
# -----------------

def main():

    used_dinners = get_used_dinners_today()

    available_dinners = []

    for dinner in dinners:
        if dinner not in used_dinners:
            available_dinners.append(dinner)
    
    if len(available_dinners) == 0:
        print("All dinners have been used today 🍽️")
        return

    result = choose_dinner(available_dinners)

    print(f"Tonights dinner: {result}")

    log_event("SPIN", "None", result)

    print(read_dinner_log())

    print(get_spin_count_today())



# this starts the program
if __name__ == "__main__":
    main()






""""
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
"""