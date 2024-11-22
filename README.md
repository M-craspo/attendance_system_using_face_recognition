# # Face Recognition Attendance System 🔍

A modern, real-time attendance tracking system using facial recognition technology, built with Streamlit and OpenCV. This system allows for automated attendance marking through webcam face detection and recognition.

## 🌟 Features

- Real-time face detection and recognition
- Automatic attendance marking with customizable intervals
- Visual feedback with emoji indicators
- Downloadable attendance records in CSV format
- Support for multiple camera inputs
- User-friendly interface with Streamlit
- Configurable attendance marking intervals
- Status indicators for successful recognition

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/attendance_system_using_face_recognition.git
cd attendance_system_using_face_recognition
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required system packages (Linux/Ubuntu):
```bash
sudo apt-get update
sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgl1-mesa-glx
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

```
attendance_system_using_face_recognition/
├── app.py                     # Main Streamlit application
├── simple_facerec.py         # Face recognition utility class
├── Attendance.py             # Attendance system class
├── requirements.txt          # Python dependencies
├── images/                   # Directory for face images
│   └── known_faces/         # Store known face images here
└── README.md                # Project documentation
```

## 🚀 Usage

1. Add face images:
   - Create an `images` directory in the project root
   - Add clear, front-facing photos of individuals
   - Name the images with the person's name (e.g., `john_doe.jpg`)

2. Run the application:
```bash
streamlit run app.py
```

3. In the application:
   - Set the path to your images directory
   - Select your camera device
   - Set the attendance interval
   - Click "Start Attendance" to begin recognition
   - Download attendance records using the "Download Attendance CSV" button

## ⚙️ Configuration

The system offers several configurable parameters through the Streamlit sidebar:

- **Image Path**: Directory containing face images
- **Camera Selection**: Choose between available cameras (0, 1, 2)
- **Attendance Interval**: Set the time between attendance marks (10-120 seconds)

## 📊 Attendance Records

The system generates attendance records with the following information:
- Name of the person
- Timestamp of recognition
- Attendance status
- Download option in CSV format

## 🌈 Status Indicators

The system uses visual indicators to show recognition status:
- 🟢 Green: Successful recognition and attendance marked
- ⚪ White: Known face, waiting for interval
- 🔴 Red: Unknown face

## 🔧 Dependencies

Main requirements:
```
streamlit
opencv-python
numpy
pandas
face-recognition
dlib
```

See `requirements.txt` for complete list.

## 🐛 Troubleshooting

Common issues and solutions:

1. **Camera not working:**
   - Check camera index (try 0, 1, or 2)
   - Verify camera permissions

2. **Face not recognized:**
   - Ensure good lighting
   - Use clear, front-facing photos
   - Check image path configuration

3. **Installation issues:**
   - Install system dependencies first
   - Use virtual environment
   - Check Python version compatibility

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenCV team for computer vision capabilities
- Streamlit team for the amazing web framework
- Face Recognition library developers


