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

    session_events = []

    SPIN = "SPIN"
    RESPIN = "RESPIN"
    FINAL = "FINAL"
    STEFFEN = "Steffen"
    SABRINA = "Sabrina"
    NOPERSON = "None"

    for line in log_lines: # Check if a final dinner has already been choosen
        if line[0] == todaysDate and line[1] == FINAL:
            return (False, "Dinner already finalized today.", None, session_events)
        
    current_dinner = do_spin(SPIN, NOPERSON)

    if current_dinner is not None:
        session_events.append((SPIN, NOPERSON, current_dinner))

    if current_dinner is None:
        return (False, "No Dinner is available", None, session_events)

    if not has_person_used_respin_today(STEFFEN):
        spinSteffen = do_spin(RESPIN, STEFFEN)
        if spinSteffen is not None:
            current_dinner = spinSteffen
            session_events.append((RESPIN, STEFFEN, spinSteffen))
        
    if not has_person_used_respin_today(SABRINA):
        spinSabrina = do_spin(RESPIN, SABRINA)
        if spinSabrina is not None:
            current_dinner = spinSabrina
            session_events.append((RESPIN, SABRINA, spinSabrina))
        
    log_event(FINAL, NOPERSON, current_dinner)

    return (True, "Dinner Chosen.", current_dinner, session_events)

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

def print_last_n_final_dinner(n = 5):

    last_5_dinners = get_last_n_final_dinners(n)

    if not last_5_dinners:
        print("No previous FINAL dinners found yet.")
        return
    
    print("Last", n, "dinners:")

    for date, dinner in last_5_dinners:
        print(f"{date}: {dinner}")


# -----------------
# MAIN PROGRAM FLOW
# -----------------

def main():

    print_last_n_final_dinner(5)
    print() # blank line

    success, message, dinner, session_events = run_spin_session()

    print(message)

    # Print the session journey(log)
    if session_events:
        print("\nToday's spins:")
        for event_type, person, spun_dinner in session_events:
            if event_type == "SPIN":
                print(f"- SPIN: {spun_dinner}")
            elif event_type == "RESPIN":
                print(f"- RESPIN ({person}): {spun_dinner}")
            else:
                print(f"- {event_type} ({person}): {spun_dinner}")
    
    if success:
        print(f"Todays Dinner: {dinner}")



# this starts the program
if __name__ == "__main__":
    main()