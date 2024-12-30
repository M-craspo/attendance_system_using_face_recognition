import streamlit as st
import cv2
from simple_facerec import SimpleFacerec
from Attendance import AttendanceSystem
import numpy as np
import pandas as pd
import time
import tempfile
import os
import face_recognition

class EnhancedFaceRecognition(SimpleFacerec):
    def __init__(self, confidence_threshold=0.6):
        super().__init__()
        self.confidence_threshold = confidence_threshold
    
    def detect_known_faces(self, frame):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        face_names = []
        face_confidences = []
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                confidence = 1 - min(face_distances)  # Convert distance to confidence
                best_match_index = np.argmin(face_distances)
                
                if confidence >= self.confidence_threshold and matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                else:
                    name = "Unknown"
                    
                face_names.append(name)
                face_confidences.append(confidence)
            
        return face_locations, face_names, face_confidences

def draw_face_info(frame, face_loc, name, confidence, time_since_last=None, check_in_count=None):
    y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
    
    # Determine color based on recognition status
    if name == "Unknown":
        color = (0, 0, 255)  # Red
    else:
        # Create a gradient from yellow to green based on confidence
        green = int(255 * min(confidence * 1.5, 1))
        red = int(255 * (1 - confidence))
        color = (0, green, red)
    
    # Draw rectangle around face
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
    
    # Create info text with name, confidence, and status
    if name != "Unknown":
        info_text = f"{name} ({confidence:.1%})"
        if time_since_last is not None:
            info_text += f" | {time_since_last:.0f}s ago"
        if check_in_count is not None:
            info_text += f" | Check-ins: {check_in_count}"
    else:
        info_text = "Unknown"
    
    # Add background for text
    text_size = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
    cv2.rectangle(frame, (x1, y1 - text_size[1] - 10), (x1 + text_size[0], y1), color, -1)
    
    # Draw text
    cv2.putText(frame, info_text, (x1, y1 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

def main():
    st.title("🔍 Enhanced Face Recognition Attendance System")
    st.sidebar.header("System Configuration")
    
    # Enhanced configuration options
    image_path = st.sidebar.text_input("Path to Face Images", r"/Users/mahmoudahmed/Desktop/face_recognition/attendance_system_using_face_recognition/images")
    camera_index = st.sidebar.selectbox("Select Camera", [0, 1, 2], index=0)
    attendance_interval = st.sidebar.slider("Attendance Interval (seconds)", min_value=10, max_value=120, value=30)
    confidence_threshold = st.sidebar.slider("Recognition Confidence Threshold", min_value=0.4, max_value=0.9, value=0.6)
    
    # Initialize system
    if 'attendance_system' not in st.session_state:
        st.session_state.attendance_system = AttendanceSystem()
        st.session_state.last_check_in_times = {}
        st.session_state.check_in_counts = {}
    
    # UI elements
    col1, col2 = st.sidebar.columns(2)
    start_camera = col1.button("Start Attendance")
    stop_camera = col2.button("Stop Attendance")
    
    # Create placeholders for dynamic content
    frame_placeholder = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        attendance_placeholder = st.empty()
    with col2:
        summary_placeholder = st.empty()
    
    if start_camera:
        # Initialize enhanced face recognition
        sfr = EnhancedFaceRecognition(confidence_threshold=confidence_threshold)
        sfr.load_encoding_images(image_path)
        
        cap = cv2.VideoCapture(camera_index)
        
        while start_camera and not stop_camera:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture frame")
                break
            
            current_time = time.time()
            face_locations, face_names, face_confidences = sfr.detect_known_faces(frame)
            
            for face_loc, name, confidence in zip(face_locations, face_names, face_confidences):
                if name != "Unknown":
                    # Initialize tracking for new person
                    if name not in st.session_state.last_check_in_times:
                        st.session_state.last_check_in_times[name] = 0
                        st.session_state.check_in_counts[name] = 0
                    
                    # Check if it's time for a new attendance mark
                    time_since_last = current_time - st.session_state.last_check_in_times[name]
                    
                    if time_since_last >= attendance_interval:
                        st.session_state.attendance_system.mark_attendance(name)
                        st.session_state.last_check_in_times[name] = current_time
                        st.session_state.check_in_counts[name] += 1
                    
                    # Draw face information with status
                    draw_face_info(
                        frame, 
                        face_loc, 
                        name, 
                        confidence,
                        time_since_last,
                        st.session_state.check_in_counts[name]
                    )
                else:
                    draw_face_info(frame, face_loc, name, confidence)
            
            # Display frame and attendance information
            frame_placeholder.image(frame, channels="BGR", use_column_width=True)
            
            # Show today's attendance log
            if st.session_state.attendance_system.attendance_data:
                with attendance_placeholder.container():
                    st.subheader("Today's Attendance Log")
                    attendance_df = pd.DataFrame(st.session_state.attendance_system.attendance_data)
                    st.dataframe(attendance_df, height=300)
                
                # Show attendance summary
                with summary_placeholder.container():
                    st.subheader("Attendance Summary")
                    summary_df = st.session_state.attendance_system.get_attendance_summary()
                    st.dataframe(summary_df, height=300)
        
        if 'cap' in locals():
            cap.release()
    
    # Download attendance data
    if st.sidebar.button("Download Attendance CSV"):
        if st.session_state.attendance_system.attendance_data:
            df = pd.DataFrame(st.session_state.attendance_system.attendance_data)
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
