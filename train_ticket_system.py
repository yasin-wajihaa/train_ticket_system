import json
import os
import tempfile

def load_data(file_path):
    # read json file(trains/bookings)
    # returns python dict/list
    try:
        with open("trains.json", "r") as f:
            trains_info=json.load(f)
        return trains_info    
    except FileNotFoundError:
        return {} or []             #file does not exist
    except json.JSONDecodeError:
        return {} or []             #file is empty or corrupted
    


def save_data(data, file_path):
    # writes dict/list back to json(atomic replace)
    try:
        temp_file=file_path+ ".tmp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=4)
            os.replace(temp_file, "bookings.json")
    except FileNotFoundError:
        print("Error: File not found.")
    except PermissionError:
        print("Error: Permission denied.")
    except TypeError:
        print("Error: Data is not serializable.")        


def search_trains(source, destination, date, trains):
    # find trains that match route+date
    # returns list of matching trains
    data=load_data("trains.json")
    for train in data: pass
        
    pass


def check_seat_avaibility(train, travel_class):
    # returns seats available for a specific class in train
    pass


def calculate_fare(train, travel_class, passengers):
    # compute total cost based on distance. class multiplier, no of passengers etc
    pass


def generate_pnr(train, date, passengers):
    # generate unique pnr number
    pass


def book_tickets(train, date, passengers, travel_class, bookings):
    # decrease seat count, generate pnr, store bookings in bookings.json
    pass


def print_ticket(bookings, pnr):
    # nice format of ticket display
    pass


def cancel_ticket(pnr, bookings, trains):
    # mark booking as cancelled
    # restore seats
    # calculate refund(rules)
    pass


def calculate_refund(booking, trains):
    # based on hours before departure time and rules
    pass


def main_menu():
    # search book cancel exit
    pass


def handle_commands(args):
    # parse arguments and call correct function
    pass


def find_train_by_number(train_number, trains):
    # return train details for a given train number
    pass


def current_timestamp():
    # for booking ?cancellation record
    pass

# WTF

