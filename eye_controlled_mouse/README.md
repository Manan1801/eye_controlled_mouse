# Eye Controlled Mouse Project

This project allows users to control their mouse cursor using eye movements and blink detection. It utilizes computer vision techniques to track eye landmarks and trigger specific applications based on user blinks.

## Project Structure

```
eye_controlled_mouse
├── src
│   ├── eye_controller.py       # Main functionality for controlling the mouse
│   ├── app_launcher.py          # Launches applications based on blink detection
│   └── utils
│       └── eye_detection.py     # Utility functions for eye detection and processing
├── requirements.txt             # Lists project dependencies
└── README.md                    # Documentation for the project
```

## Installation

To set up the project, ensure you have Python installed on your machine. Then, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd eye_controlled_mouse
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Connect a webcam to your computer.
2. Run the eye controller script:
   ```
   python src/eye_controller.py
   ```
3. The application will open a window displaying the video feed from your webcam. 
4. Blink your left eye to open Google Chrome and your right eye to open Telegram.

## Dependencies

This project requires the following Python libraries:

- OpenCV
- Mediapipe
- PyAutoGUI

Make sure to install these libraries using the `requirements.txt` file provided.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.