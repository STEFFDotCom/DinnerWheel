import random
import os
import datetime # all dinner events use DD-MM-YYYY format for consistency in the log
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # declare a base directory that is the same folder as our py script
DB_FILE = os.path.join(BASE_DIR, "dinner_wheel.db") # make shortcut for database using base directory
DINNER_LIST_FILE = os.path.join(BASE_DIR, "aftensmad retter til hjul.txt") # shortcut for dinner list file

SPIN = "SPIN"
RESPIN = "RESPIN"
FINAL = "FINAL"
STEFFEN = "Steffen"
SABRINA = "Sabrina"
NOPERSON = "None"

def load_dinners_from_file(file_path):

    # if path does not exist return none
    if not os.path.exists(file_path):
        return []

    dinners_from_file = []

    # open dinner file and strip every line from whitespaces
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            item = line.strip()
            if item:
                dinners_from_file.append(item)

    return dinners_from_file

def get_all_dinners_from_db():

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT dinner_name FROM dinners
        """)
        rows = cursor.fetchall()

    dinners = []

    # row[0] = dinner_name
    for row in rows:
        dinners.append(row[0])

    return dinners

def choose_dinner(dinner_options): # function to return random dinner
    return random.choice(dinner_options)

# function to log events to DB
def log_event(event_type, person, dinner):

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO dinner_log (date, event_type, person, dinner)
            VALUES (?,?,?,?)
        """, (todaysDate, event_type, person, dinner))

# function that reads dinner_log from DB and returns it
def read_dinner_log():

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT date, event_type, person, dinner
            FROM dinner_log
        """)
        rows = cursor.fetchall()

    return rows

def get_available_dinners():

    dinners = get_all_dinners_from_db()
    
    used_dinners = get_used_dinners_today()

    last_used_dinner = get_most_recent_final_dinner()

    available_dinners = []

    for dinner in dinners:
        if dinner not in used_dinners and dinner != last_used_dinner:
            available_dinners.append(dinner)

    return available_dinners

def get_used_dinners_today():

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")

    log_rows = read_dinner_log()

    used_dinners = []

    for line in log_rows:

        if len(line) != 4:
            continue

        if line[0] == todaysDate:
            used_dinners.append(line[3])

    # set removes duplicates
    return list(set(used_dinners))

def has_person_used_respin_today(person_name):

    log_lines = read_dinner_log()

    todaysDate = datetime.date.today().strftime("%d-%m-%Y")
    
    for line in log_lines:

        if len(line) != 4:
            continue

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

    log_rows = read_dinner_log()

    for line in log_rows:

        if len(line) != 4:
            continue

        if line[1] == FINAL:
            last_5_dinners.append((line[0], line[3]))

    # start from -5 = last 5 dinners
    return last_5_dinners[-n:]

def get_most_recent_final_dinner():

    log_rows = read_dinner_log()

    for line in reversed(log_rows):

        if len(line) != 4:
            continue

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

    log_rows = read_dinner_log()

    events = []

    for line in log_rows:
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
    
def print_todays_status():
    
    todaysDate = datetime.date.today().strftime("%d-%m-%Y")
    current_dinner = get_current_dinner_for_date(todaysDate)
    final_dinner = get_final_dinner_for_date(todaysDate)
    session_events = get_session_events_for_date(todaysDate)

    print(f"---{todaysDate}---")

    if final_dinner:
        print(f"Final dinner: {final_dinner}")
    else:
        print("Final dinner: Not finalized")
    
    if current_dinner:  
        print(f"Current dinner: {current_dinner}")
    else:
        print("Current dinner: None")
    
    print(f"Events today:")
    
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

def initialize_database():

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()

        # create event log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dinner_log(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       date TEXT,
                       event_type TEXT,
                       person TEXT,
                       dinner TEXT
                       )
        """)


        # create dinner list table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dinners(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       dinner_name TEXT UNIQUE
                       )
        """)

        # load dinners from file
        dinners = load_dinners_from_file(DINNER_LIST_FILE)

        # insert dinners into the table - duplicates are ignored with OR IGNORE code
        for dinner in dinners:
            cursor.execute("""
                INSERT OR IGNORE INTO dinners (dinner_name)
                VALUES (?)
            """, (dinner,))

def get_dinner_statistics():

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT dinner, COUNT(*)
            FROM dinner_log
            WHERE event_type = ?
            GROUP BY dinner
            ORDER BY COUNT(*) DESC
        """, (FINAL,))

        dinner_stats = cursor.fetchall()
    
    return dinner_stats

def print_dinner_statistics():

    dinner_stats = get_dinner_statistics()

    print("Dinner statistics:")
    print("")

    if len(dinner_stats) == 0:
        print("No dinner stats to show.")
        return

    for dinner, count in dinner_stats:
        print(f"{dinner}: {count}")

def show_all_dinners():
    
    dinners = get_all_dinners_from_db()

    print("Available dinners:")
    print("")

    for number, dinner in enumerate(dinners, start = 1):
        print(f"{number}. {dinner}")


def add_dinner_to_list():

    dinners = get_all_dinners_from_db()

    user_input_dinner = input("What dinner would you like to add to the list?")
    user_input_dinner = user_input_dinner.strip()

    if len(user_input_dinner) == 0:
        print("Empty input - please write a dinner.")
        return

    for dinner in dinners:
        if user_input_dinner == dinner:
            print(f"{user_input_dinner} is already in the dinner list.")
            return
    
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO dinners (dinner_name)
            VALUES (?)
        """, (user_input_dinner,))

    print("")
    print(f"{user_input_dinner} has been added to the list.")

def remove_dinner_from_list():

    dinners = get_all_dinners_from_db()

    for number, dinner in enumerate(dinners, start = 1):
        print(f"{number}. {dinner}")
    
    remove_number = int(input("Input the number of what dinner you want to remove: "))
    remove_index = remove_number - 1

    if remove_number < 1 or remove_number > len(dinners):
        print("Invalid number - please enter a number from the list.")
        return

    removed_dinner = dinners[remove_index]

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM dinners
            WHERE dinner_name = ?
        """, (removed_dinner,))

    print(f"{removed_dinner} has been removed from the list.")

# -----------------
# MAIN PROGRAM FLOW
# -----------------

initialize_database()

def main():

    print_last_n_final_dinner(5)
    print() # blank line

    while True:

        print("")
        print_todays_status()
        print("")

        choice = input("Press 1 to spin, 2 for Steffen respin, 3 for Sabrina respin, 4 to finalize dinner, 5 to show dinner statistics, 6 to show all dinners in the list, 7 to add a dinner, 8 to remove a dinner from the list or 0 to exit: ")

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
        elif choice == "5":
            print_dinner_statistics()
        elif choice == "6":
            show_all_dinners()
        elif choice == "7":
            add_dinner_to_list()
        elif choice == "8":
            remove_dinner_from_list()
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choice - please enter 0, 1, 2, 3, 4, 5, 6, 7 or 8.")
        
        


# this starts the program
if __name__ == "__main__":
    main()

#if __name__ == "__main__":
#    add_dinner_to_list()