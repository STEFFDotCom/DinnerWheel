import random
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # declare a base directory that is the same folder as our py script
LOG_FILE = os.path.join(BASE_DIR, "dinner_log.txt") # make dinner_log.txt use the base directory
DINNER_LIST_FILE = os.path.join(BASE_DIR, "aftensmad retter til hjul.txt")

SPIN = "SPIN"
RESPIN = "RESPIN"
FINAL = "FINAL"
STEFFEN = "Steffen"
SABRINA = "Sabrina"
NOPERSON = "None"

def load_dinners_from_file(file_path):

    if not os.path.exists(file_path):
        return []

    dinners_from_file = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            item = line.strip()
            if item:
                dinners_from_file.append(item)

    return dinners_from_file

dinners = load_dinners_from_file(DINNER_LIST_FILE) # our dinner list

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

def has_person_used_respin_today(person_name):

    log_lines = read_dinner_log()

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")
    
    for line in log_lines:
        if line[0] == todaysDate and line[1] == RESPIN and line[2] == person_name:
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
        if len(line) == 4 and line[1] == FINAL:
            last_5_dinners.append((line[0], line[3]))

    return last_5_dinners[-n:]

def get_most_recent_final_dinner():

    log_file = read_dinner_log()

    for line in reversed(log_file):
        if line[1] == FINAL:
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

def get_session_events_for_date(date_str):

    log_file = read_dinner_log()

    events = []

    for line in log_file:
        if len(line) == 4 and line[0] == date_str:
            events.append((line[1], line[2], line[3]))

    return events

def get_current_dinner_for_date(date_str):

    todays_events = get_session_events_for_date(date_str)

    for line in reversed(todays_events):
        if line[0] == FINAL:
            return line[2]
        elif line[0] == SPIN or line[0] == RESPIN:
            return line[2]
    
    return None

def get_final_dinner_for_date(date_str): 
    log_lines = read_dinner_log() 
    
    for line in log_lines: 
        if line[0] == date_str and line[1] == FINAL: 
            return line[3] 
        
    return None

def action_spin():

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    todays_events = get_session_events_for_date(todaysDate)

    final_dinner = get_final_dinner_for_date(todaysDate)

    if final_dinner:
        return (False, f"Dinner is already finalized today: {final_dinner}", final_dinner)
    
    for line in todays_events:
        if line[0] == SPIN:
            return (False, f"Initial spin already done today", None)

    theSpin = do_spin(SPIN, NOPERSON)

    if theSpin is None:
        return (False, "There was no dinners left to choose from.", None)
    else:
        return (True, "Spin was successful", theSpin)
    
def action_respin(person):
    
    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    todays_events = get_session_events_for_date(todaysDate)

    final_dinner = get_final_dinner_for_date(todaysDate)

    spin_found = False

    if person != STEFFEN and person != SABRINA:
        return (False, "Only Steffen or Sabrina is allowed to spin.", None)
    
    if final_dinner:
        return (False, f"Dinner is already finalized today: {final_dinner}", final_dinner)
    
    for line in todays_events:
        if line[0] == SPIN:
            spin_found = True
    
    if spin_found == False:
        return (False, "You must do an initial spin first.", None)
    
    if has_person_used_respin_today(person):
        return (False, f"{person} has already used their respin today", None)
    
    do_respin = do_spin(RESPIN, person)

    if do_respin is None:
        return (False, "Could not do respin.", None)
    else:
        return (True, "Respin successful", do_respin)
    
def action_finalize():

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    final_dinner = get_final_dinner_for_date(todaysDate)

    current_dinner = get_current_dinner_for_date(todaysDate)

    if final_dinner:
        return (False, f"Dinner is already finalized today: {final_dinner}", final_dinner)
    
    if current_dinner is None:
        return (False, "You must first spin.", None)
    else:
        log_event(FINAL, NOPERSON, current_dinner)
        return (True, "Final dinner has been chosen.", current_dinner)
    
def maybe_auto_finalize_today():

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")
    current_dinner = get_current_dinner_for_date(todaysDate)
    final_dinner = get_final_dinner_for_date(todaysDate)

    if final_dinner:
        return (False, "Already finalized", final_dinner)
    
    if has_person_used_respin_today(SABRINA) and has_person_used_respin_today(STEFFEN):
        if current_dinner is not None:
            success, message, dinner = action_finalize()
            return (True, "Auto-finalized", dinner)
    else:
        return (False, "", None)

# -----------------
# MAIN PROGRAM FLOW
# -----------------

def main():

    print_last_n_final_dinner(5)
    print() # blank line

    while True:

        todaysDate = datetime.date.today().strftime("%d-%m-%Y")
        current_dinner = get_current_dinner_for_date(todaysDate)
        final_dinner = get_final_dinner_for_date(todaysDate)
        session_events = get_session_events_for_date(todaysDate)

        print("") # print blank

        print(f"---{todaysDate}---")

        if final_dinner:
            print(f"Final dinner: {final_dinner}")
        else:
            print(f"Final dinner: Not Finalized")

        if current_dinner:
            print(f"Current dinner: {current_dinner}")
        else:
            print(f"Current dinner: None")

        if len(session_events) == 0:
            print("No events yet.")
        else:
            for event_type, person, dinner in session_events:
                if event_type == SPIN:
                    print(f"- {event_type}: {dinner}")
                elif event_type == RESPIN:
                    print(f"- {event_type} ({person}): {dinner}")
                elif event_type == FINAL:
                    print(f"- {event_type}: {dinner}")

        print("") # print blank

        choice = input("Press 1 to spin, 2 for Steffen respin, 3 for Sabrina respin, 4 to finalize dinner or 0 to exit: ")

        if choice == "1":
            success, message, dinner = action_spin()
            print(message)
            if success:
                print(f"Todays dinner is: {dinner}")
                did_finalize, auto_msg, final_dinner = maybe_auto_finalize_today()
                if did_finalize:
                    print(f"{auto_msg}: {final_dinner}")
                    break
        elif choice == "2":
            success, message, dinner = action_respin(STEFFEN)
            print(message)
            if success:
                print(f"Steffen used his respin and dinner is now: {dinner}")
                did_finalize, auto_msg, final_dinner = maybe_auto_finalize_today()
                if did_finalize:
                    print(f"{auto_msg}: {final_dinner}")
                    break
        elif choice == "3":
            success, message, dinner = action_respin(SABRINA)
            print(message)
            if success:
                print(f"Sabrina used her respin and dinner is now: {dinner}")
                did_finalize, auto_msg, final_dinner = maybe_auto_finalize_today()
                if did_finalize:
                    print(f"{auto_msg}: {final_dinner}")
                    break
        elif choice == "4":
            success, message, dinner = action_finalize()
            print(message)
            if success:
                print(f"Dinner has been finalized: {dinner}")
                break
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choise - please enter 0, 1, 2, 3 or 4.")
        
        


# this starts the program
if __name__ == "__main__":
    main()