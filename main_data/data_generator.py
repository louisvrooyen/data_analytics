import csv, openpyxl, random
from datetime import datetime, timedelta



from data_imports_project.dictionaries.categories import incident_categories


# --- Constants ---
TRIP_REASONS = {
    1: "Cancelled before Leaving Station",
    2: "Other Service on Scene",
    3: "Service Trip",
}

HEADER = [
    "Incident_Number", "Incident_Date", "Incident_Category", "Incident_Subcategory", "Str_Number",
    "Incident_Save", "Incident_Ack", "Veh_Desp", "Veh_Arrived", "Last_Veh_Home", "Incident_Closed",
    "Incident_Status_ID", "Service_Trip_ID", "Service_Trip_Reason"
]

# Flatten all subcategories
all_subcategories = [s for subs in incident_categories.values() for s in subs]

def get_category(subcategory):
    for category, subs in incident_categories.items():
        if subcategory in subs:
            return category
    return "Unknown"

def format_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def random_datetime(base, offset_sec=0):
    return base + timedelta(seconds=offset_sec)

def simulate_fault(value, fault_type):
    if fault_type == "empty":
        return "1900-01-01 00:00:00"
    elif fault_type == "negative":
        return format_dt(datetime.strptime(value, "%Y-%m-%d %H:%M:%S") - timedelta(minutes=5))
    return value

def generate_record(index, base_time, inject_fault=False):
    incident_number = f"I{base_time.strftime('%Y%m%d')}{str(index+1).zfill(3)}"
    incident_date = format_dt(base_time)  # Always valid
    incident_save = format_dt(random_datetime(base_time, 90))  # Always valid

    subcategory = random.choice(all_subcategories)
    category = get_category(subcategory)

    # Store times in a dict for easier fault injection
    times = {
        "incident_ack": format_dt(random_datetime(base_time, 110)),
        "veh_desp": format_dt(random_datetime(base_time, 170)),
        "veh_arrived": format_dt(random_datetime(base_time, 890)),
        "last_veh_home": format_dt(random_datetime(base_time, 3690)),
        "incident_closed": format_dt(random_datetime(base_time, 4890)),
    }

    # Inject faults into random time fields (but never baseline fields)
    if inject_fault:
        fault_fields = random.sample(list(times.keys()), k=random.randint(1, 3))
        for field in fault_fields:
            times[field] = simulate_fault(times[field], random.choice(["empty", "negative"]))

    str_number = str(random.randint(1, 999))
    status_id = random.randint(1, 5)
    trip_id = random.randint(1, 3)
    trip_reason = TRIP_REASONS[trip_id]

    return [
        incident_number, incident_date, category, subcategory, str_number, incident_save,
        times["incident_ack"], times["veh_desp"], times["veh_arrived"],
        times["last_veh_home"], times["incident_closed"], status_id, trip_id, trip_reason
    ]

def generate_records(start, end, count):
    total_minutes = (end - start).total_seconds() // 60
    spacing = max(1, int(total_minutes // count))
    return [
        generate_record(i, start + timedelta(minutes=i * spacing), inject_fault=(i % 3 == 0))
        for i in range(count)
    ]

def write_csv(records, filename, header=HEADER):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(records)

def write_xlsx(records, filename, header=HEADER):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Incident Records"
    ws.append(header)
    for row in records:
        ws.append(row)
    wb.save(filename)