# logger.py
import csv
from datetime import datetime

def log_activity(equipment_id, activity_type, details):
    with open("equipment_log.csv", mode="a", newline="") as log_file:
        log_writer = csv.writer(log_file)
        log_writer.writerow([datetime.now(), equipment_id, activity_type, details])
