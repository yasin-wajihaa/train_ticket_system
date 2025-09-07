import json
import os
from datetime import datetime
import random

current_timestamp = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_data(file_path):
    
    try:
        with open(file_path, "r") as f:
            trains_info=json.load(f)
        return trains_info    
    except FileNotFoundError:
        return []             #file does not exist
    except json.JSONDecodeError:
        return []             #file is empty or corrupted
    

def save_data(data, file_path):
    
    try:
        temp_file=file_path+ ".tmp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=4)
            os.replace(temp_file, file_path)
    except PermissionError:
        print("Error: Permission denied.")
    except TypeError:
        print("Error: Data is not serializable.")    
    except OSError:
        print("Error: Could not write to file.")    


def search_trains(source, destination, date, trains):
    """
    Find trains running on the given date that pass through both source and destination stations,
    with source before destination in the route.
    Returns a list of matching train details.
    """

    results=[]

    # convert date string --> weekday (e.g., "Fri")
    travel_date = datetime.strptime(date, "%Y-%m-%d")
    day_name = travel_date.strftime("%a")

    for train in trains:
        # check if train runs on given day
        if day_name not in train.get("days_of_operation", []):
            continue

        # extract station names from route
        route=train.get("route", [])
        stations=[stop["station"] for stop in route]

        # check if both source and destination are in the route and in correct order.
        if source in stations and destination in stations:
            src_idx = stations.index(source)
            dst_idx = stations.index(destination)
            if src_idx < dst_idx:
                src_stop = route[src_idx]
                dst_stop = route[dst_idx]

                results.append({
                    "train_number": train["train_number"],
                    "train_name": train["train_name"],
                    "from": source,
                    "departure": src_stop.get("departure"),
                    "to": destination,
                    "arrival": dst_stop.get("arrival"),
                    "day": day_name
                })

    return results
    

def check_seat_avaibility(train_number, class_type, trains):
    for train in trains:
        if train["train_number"]==train_number:
            seats=train.get("classes", {}).get(class_type)
            return seats
    return None   


def calculate_fare(train_number, class_type, trains, source, destination):
    for train in trains:
        if train["train_number"]==train_number:
            route=train.get("route", [])
            stations=[stop["station"] for stop in route]

        # check if both source and destination are in the route and in correct order.
        if source in stations and destination in stations:
            src_idx = stations.index(source)
            dst_idx = stations.index(destination)

            if src_idx < dst_idx:
                distance_segments = train.get("distance_per_segment", {})
                total_distance=0
                 
                # sum distances of all segments between src and dest 
                for i in range(src_idx, dst_idx):
                    segment_key=f"{stations[i]}-{stations[i+1]}"
                    segment_distance=distance_segments.get(segment_key, 0)
                    if segment_distance is None:
                        return None  # missing segment distance
                    total_distance += segment_distance
                
                #get fare per km for class                                                                                                               #  )
                fare_rate = train.get("fare_per_km", {}).get(class_type)
                if fare_rate is None:
                    return None  # invalid class
            
                fare = total_distance * fare_rate
                return round(fare, 2)
    
    return None  # train not found or invalid route


def generate_pnr(train, date):
    
    try:
        with open("bookings.json", "r") as f:
            bookings=json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bookings = []

    existing_pnrs={b["pnr"] for b in bookings}
    while True:
        unique_pnr=train["train_number"] + "-" + date + "-" + str(random.randint(1000,9999))
        if unique_pnr not in existing_pnrs:
            return unique_pnr
        

def book_tickets(trains, date, class_type, source, destination, train_number=None):
    selected_trains = search_trains(source, destination, date, trains)
    if not selected_trains:
        print("No trains available for this route/date")
        return None

    # If train_number is provided, select that train; else pick the first available
    if train_number:
        selected_train = next((t for t in selected_trains if t["train_number"] == train_number), None)
        if not selected_train:
            print("Train number not found in available trains.")
            return None
    else:
        selected_train = selected_trains[0]

    train_number = selected_train["train_number"]

    seats = check_seat_avaibility(train_number, class_type, trains)
    if seats is None or seats <= 0:
        print("No seats available")
        return None

    fare = calculate_fare(train_number, class_type, trains, source, destination)
    if fare is None:
        print("Error calculating fare")
        return None

    pnr = generate_pnr(selected_train, date)

    # Update seat count only for the selected train
    for train in trains:
        if train["train_number"] == train_number:
            train["classes"][class_type] -= 1
            break
    save_data(trains, "trains.json")

    booking_record = load_data("bookings.json")
    booking_record.append({
        "pnr": pnr,
        "train_number": train_number,
        "date": date,
        "class": class_type,
        "from": source,
        "to": destination,
        "fare": fare,
        "status": "Booked",
        "booking_time": current_timestamp()
    })
    save_data(booking_record, "bookings.json")

    print(f"Booking successful! PNR: {pnr}, Fare: {fare}")
    return pnr
    

def print_ticket(pnr):
    
    bookings= load_data("bookings.json")
    trains= load_data("trains.json")
    
    #search for the booking by pnr
    booking_found = None
    for booking in bookings:
        if booking["pnr"] == pnr:
            booking_found = booking
            break

    if not booking_found:
        print("Booking not found")
        return

    #extract booking info
    train_number = booking_found["train_number"]
    class_type = booking_found["class"]
    source = booking_found["from"]
    destination = booking_found["to"]
    fare = booking_found["fare"]
    booking_time = booking_found["booking_time"]
    status = booking_found.get("status", "Booked")  

    #fetch train_name from trains.json
    train_name = "" 
    for train in trains:
        if train["train_number"] == train_number:
            train_name = train["train_name"]
            break

    
    print("==========TICKET================")
    print(f"PNR: {pnr}")
    print(f"Train: {train_number} - {train_name} ")           
    print(f"Class: {class_type}")           
    print(f"From: {source}")           
    print(f"To: {destination}")           
    print(f"Fare: {fare}")           
    print(f"Booking Time: {booking_time}")      
    print(f"Status: {status}")  
    print("================================")   


def cancel_ticket(pnr, bookings, trains):
    booking_found = None

    for booking in bookings:
        if booking["pnr"] == pnr:
            booking_found = booking
            break

    if not booking_found:
        print("Booking not found or already cancelled")
        return
    
    if booking_found["status"].lower() == "cancelled":
        print("Booking already cancelled")
        return
    
    booking_found["status"] = "Cancelled"

    train_number = booking_found["train_number"]
    class_type = booking_found["class"]

    for train in trains:
        if train["train_number"] == train_number:
            train["classes"][class_type] += 1
            break

    save_data(bookings, "bookings.json")
    save_data(trains, "trains.json")

    print(f"Booking {pnr} cancelled successfully.")    
           

def main_menu():
    
    print("=== Train Ticket Booking System ===")
    print("1. Search Trains")
    print("2. Book Ticket")
    print("3. Print Ticket")
    print("4. Cancel Ticket")
    print("5. Exit")
    try:
        choice = int(input("Enter your choice: "))
        return choice
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 5.")
    except Exception as e:
        print(f"An error occurred: {e}")


def handle_commands():
    while True:
        trains = load_data("trains.json")
        bookings = load_data("bookings.json")
        choice = main_menu()

        if choice == 1:
            source = input("Enter source station: ").strip()
            destination = input("Enter destination station: ").strip()
            date = input("Enter travel date (YYYY-MM-DD): ").strip()
            results = search_trains(source, destination, date, trains)
            if results:
                print("Available trains:")
                for train in results:
                    print(f"{train['train_number']} - {train['train_name']} | "
                          f"From: {train['from']} ({train['departure']}) "
                          f"To: {train['to']} ({train['arrival']})")
            else:
                print("No trains found for the given route/date.")

        elif choice == 2:
            train_number = input("Enter train number: ").strip()
            date = input("Enter travel date (YYYY-MM-DD): ").strip()
            class_type = input("Enter class (e.g., 1A, 2A, SL): ").strip()
            source = input("Enter source station: ").strip()
            destination = input("Enter destination station: ").strip()
            pnr = book_tickets(trains, date, class_type, source, destination, train_number)

        elif choice == 3:
            pnr = input("Enter PNR number: ").strip()
            print_ticket(pnr)

        elif choice == 4:
            pnr = input("Enter PNR number to cancel: ").strip()
            cancel_ticket(pnr, bookings, trains)

        elif choice == 5:
            print("Exiting the system. Goodbye!")
            break

        else:
            print("Invalid choice. Please select a valid option.")
