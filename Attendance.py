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
                writer.writerow(['Name', 'Date', 'Time', 'Timestamp', 'Check_in_Number'])

    def mark_attendance(self, name):
        """Mark attendance at specified intervals"""
        if not name or name == "Unknown":
            return False

        try:
            current_datetime = datetime.now()
            current_date = current_datetime.strftime("%Y-%m-%d")
            current_time = current_datetime.strftime("%H:%M:%S")
            timestamp = current_datetime.timestamp()

            # Count today's check-ins for this person
            try:
                df = pd.read_csv(self.attendance_file)
                today_entries = df[(df['Name'] == name) & (df['Date'] == current_date)]
                check_in_number = len(today_entries) + 1
            except (pd.errors.EmptyDataError, FileNotFoundError):
                check_in_number = 1

            # Record the attendance
            with open(self.attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([name, current_date, current_time, timestamp, check_in_number])
            
            # Update attendance_data for Streamlit
            record = {
                'Name': name, 
                'Date': current_date, 
                'Time': current_time,
                'Timestamp': timestamp,
                'Check_in_Number': check_in_number
            }
            self.attendance_data.append(record)
            return True

        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False

    def get_attendance_summary(self):
        """Generate detailed attendance summary"""
        try:
            df = pd.read_csv(self.attendance_file)
            
            # Group by date and name to get summary statistics
            summary = df.groupby(['Date', 'Name']).agg({
                'Check_in_Number': 'max',  # Total check-ins
                'Time': ['first', 'last']  # First and last check-in times
            }).reset_index()
            
            # Flatten column names and rename for clarity
            summary.columns = ['Date', 'Name', 'Total_Check_ins', 'First_Check_in', 'Last_Check_in']
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
