from datetime import datetime
import csv
import os
import pandas as pd

class AttendanceSystem:
    def __init__(self, attendance_file="attendance.csv"):
        self.attendance_file = attendance_file
        self.attendance_data = []  # Added for Streamlit compatibility
        self.initialize_attendance_file()

    def initialize_attendance_file(self):
        """Ensure attendance file exists with proper headers"""
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Date', 'Time', 'Timestamp'])
    
    def person_exists_today(self, name):
        """Check if person already exists in today's records"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            df = pd.read_csv(self.attendance_file)
            existing = df[(df['Name'] == name) & (df['Date'] == current_date)]
            return not existing.empty
        except pd.errors.EmptyDataError:
            return False
        except Exception as e:
            print(f"Error checking person existence: {e}")
            return False

    def mark_attendance(self, name):
        """Mark attendance with more robust error handling"""
        if not name or name == "Unknown":
            return False

        try:
            current_datetime = datetime.now()
            current_date = current_datetime.strftime("%Y-%m-%d")
            current_time = current_datetime.strftime("%H:%M:%S")
            timestamp = current_datetime.timestamp()

            # Avoid duplicate attendance on the same day
            if not self.person_exists_today(name):
                with open(self.attendance_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([name, current_date, current_time, timestamp])
                
                # Update attendance_data for Streamlit
                record = {
                    'Name': name, 
                    'Date': current_date, 
                    'Time': current_time,
                    'Timestamp': timestamp
                }
                self.attendance_data.append(record)
                return True
            return False
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False

    def get_attendance_summary(self):
        """Generate attendance summary"""
        try:
            df = pd.read_csv(self.attendance_file)
            summary = df.groupby(['Date', 'Name']).size().reset_index(name='Attendance_Count')
            return summary
        except Exception as e:
            print(f"Error generating summary: {e}")
            return pd.DataFrame()

    def clear_attendance_file(self):
        """Clear all attendance records"""
        try:
            os.remove(self.attendance_file)
            self.initialize_attendance_file()
            self.attendance_data = []
        except Exception as e:
            print(f"Error clearing attendance file: {e}")