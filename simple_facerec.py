import cv2
import os
import glob
import numpy as np
import face_recognition  # The library for face encoding and recognition


#from face_detection_recognition import FaceDetectionRecognition

class SimpleFacerec:
    def __init__(self, frame_resizing=0.7):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = frame_resizing

    def load_encoding_images(self, images_path):
        """Load known face encodings and names."""
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        print(f"{len(images_path)} encoding images found.")

        for img_path in images_path:
            print(f"Processing image: {img_path}")

            # Read the image
            img = cv2.imread(img_path)

            if img is None:
                print(f"Warning: Could not load image {img_path}")
                continue  # Skip invalid images

            # Convert BGR to RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get face encodings using the face_recognition library
            encodings = face_recognition.face_encodings(rgb_img)

            if encodings:
                # Extract name from file name
                name = os.path.splitext(os.path.basename(img_path))[0]
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(name)
            else:
                print(f"No face detected in {img_path}")

    def detect_known_faces(self, frame):
        """Detect known faces in a frame."""
        # Resize the frame
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)

        # Convert to RGB
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            face_names.append(name)

        # Adjust face locations to the original frame size
        scale = 1 / self.frame_resizing
        face_locations = [(int(y1 * scale), int(x2 * scale), int(y2 * scale), int(x1 * scale)) for (y1, x2, y2, x1) in face_locations]

        return face_locations, face_names
