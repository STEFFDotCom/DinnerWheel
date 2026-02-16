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
    
    spin_count = get_spin_count_today()

    log_lines = read_dinner_log()

    used_dinners = get_used_dinners_today()

    available_dinners = []

    final_dinner = ""

    for line in log_lines: # Check if a final dinner has already been choosen
        if line[0] == todaysDate and line[1] == "FINAL":
            return None
        
    if spin_count < 3:
        for dinner in dinners:
            if dinner not in used_dinners:
                available_dinners.append(dinner)

        if len(available_dinners) == 0:
            return "No dinners left to choose from! Restart the program"

        final_dinner = choose_dinner(available_dinners)
        log_event("SPIN", "None", final_dinner)

        used_dinners = get_used_dinners_today() # update used_dinners

        available_dinners.clear() # clear available_dinners so we dont have duplicates

        for dinner in dinners:
            if dinner not in used_dinners:
                available_dinners.append(dinner)
            
            if len(available_dinners) == 0:
                    return "No dinners left to choose from! Restart the program"

        final_dinner = choose_dinner(available_dinners)
        log_event("SPIN", "None", final_dinner)

        log_event("FINAL", "None", final_dinner)
        return final_dinner

            
        
    

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