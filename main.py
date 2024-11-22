import streamlit as st
import cv2
from simple_facerec import SimpleFacerec
from Attendance import AttendanceSystem
import numpy as np
import pandas as pd
import time
import tempfile
import os

def draw_emoji(frame, x1, y1, x2, y2, emoji_type):
    # Use the same emoji drawing logic from the original script
    emoji_size = min(x2 - x1, y2 - y1) // 2
    emoji_x = x1 + (x2 - x1) // 2 - emoji_size // 2
    emoji_y = y1 - emoji_size - 10

    if emoji_type == 'success':
        cv2.line(frame, (emoji_x, emoji_y + emoji_size // 2), 
                 (emoji_x + emoji_size // 3, emoji_y + emoji_size), 
                 (0, 255, 0), 3)
        cv2.line(frame, (emoji_x + emoji_size // 3, emoji_y + emoji_size), 
                 (emoji_x + emoji_size, emoji_y), 
                 (0, 255, 0), 3)
    elif emoji_type == 'waiting':
        cv2.rectangle(frame, (emoji_x, emoji_y), 
                      (emoji_x + emoji_size, emoji_y + emoji_size), 
                      (0, 255, 255), 2)
        cv2.line(frame, (emoji_x, emoji_y), 
                 (emoji_x + emoji_size, emoji_y + emoji_size), 
                 (0, 255, 255), 2)

def main():
    st.title("🔍 Face Recognition Attendance System")
    st.sidebar.header("System Configuration")

    # Sidebar for configurations
    image_path = st.sidebar.text_input("Path to Face Images", 
                                       "/Users/mahmoudahmed/Desktop/face_recognition/images")
    camera_index = st.sidebar.selectbox("Select Camera", [0, 1, 2], index=0)
    attendance_interval = st.sidebar.slider("Attendance Interval (seconds)", 
                                            min_value=10, max_value=120, value=30)

    # Buttons
    start_camera = st.sidebar.button("Start Attendance")
    stop_camera = st.sidebar.button("Stop Attendance")

    # Placeholder for video stream and attendance
    frame_placeholder = st.empty()
    attendance_placeholder = st.empty()

    # Session state for tracking
    if 'attendance_system' not in st.session_state:
        st.session_state.attendance_system = AttendanceSystem()
        st.session_state.attendance_status = {}

    if start_camera:
        # Initialize face recognition
        sfr = SimpleFacerec()
        sfr.load_encoding_images(image_path)

        # Open camera
        cap = cv2.VideoCapture(camera_index)

        while start_camera and not stop_camera:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture frame")
                break

            current_time = time.time()
            face_locations, face_names = sfr.detect_known_faces(frame)

            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

                # Initialize attendance status for new faces
                if name not in st.session_state.attendance_status:
                    st.session_state.attendance_status[name] = {
                        "marked": False,
                        "last_time": 0,
                        "wait_start": 0
                    }
                
                time_since_last = current_time - st.session_state.attendance_status[name]["last_time"]
                time_since_mark = current_time - st.session_state.attendance_status[name]["wait_start"]
                
                # Mark attendance logic
                should_mark = (not st.session_state.attendance_status[name]["marked"] or 
                               time_since_last >= attendance_interval)
                
                if should_mark and name != "Unknown":
                    st.session_state.attendance_system.mark_attendance(name)
                    st.session_state.attendance_status[name]["marked"] = True
                    st.session_state.attendance_status[name]["last_time"] = current_time
                    st.session_state.attendance_status[name]["wait_start"] = current_time

                # Determine color and emoji
                if name == "Unknown":
                    color = (0, 0, 255)  # Red
                    emoji_type = None
                elif time_since_mark < 2:  # 2-second wait time
                    color = (0, 255, 0)  # Green
                    emoji_type = 'success'
                    draw_emoji(frame, x1, y1, x2, y2, 'success')
                else:
                    color = (255, 255, 255)  # White
                    emoji_type = None
                
                # Draw name and rectangle
                cv2.putText(frame, name, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, color, 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)

            # Display the frame
            frame_placeholder.image(frame, channels="BGR", use_column_width=True)

            # Optional: Display current attendance
            if st.session_state.attendance_system.attendance_data:
                attendance_df = pd.DataFrame(st.session_state.attendance_system.attendance_data)
                attendance_placeholder.dataframe(attendance_df)

        # Release camera
        if 'cap' in locals():
            cap.release()

    # Download button for attendance CSV
    if st.sidebar.button("Download Attendance CSV"):
        attendance_data = st.session_state.attendance_system.attendance_data
        if attendance_data:
            df = pd.DataFrame(attendance_data)
            csv = df.to_csv(index=False)
            st.sidebar.download_button(
                label="Click to Download Attendance",
                data=csv,
                file_name="attendance_record.csv",
                mime="text/csv",
            )
        else:
            st.sidebar.warning("No attendance data available")

if __name__ == "__main__":
    main()