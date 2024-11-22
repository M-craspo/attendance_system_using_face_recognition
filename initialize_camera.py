import cv2

def initialize_camera(camera_index):

    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Could not open camera {camera_index}")
            return None
            
        # Try to read a test frame
        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"Could not read from camera {camera_index}")
            cap.release()
            return None
            
        return cap
        
    except Exception as e:
        print(f"Error initializing camera {camera_index}: {str(e)}")
        return None

            
