UART-Based Temperature Sensor Logger and Visualizer
A complete embedded system solution for temperature monitoring using Arduino and Python. This project demonstrates real-time data acquisition, UART communication, and live visualization with robust error handling and data logging capabilities.
🌡️ Features
Embedded System (Arduino)

Temperature Simulation: Realistic temperature data generation using sine waves and random noise
UART Communication: Structured data packets with checksum verification
Static Memory Management: Safe buffer handling for microcontroller environments
Error Detection: Checksum-based data integrity verification
Visual Feedback: LED indicators for transmission status
Command Processing: Basic command interface for system control

Host System (Python)

Real-time Visualization: Live matplotlib plotting with temperature trends
Data Logging: CSV file output with timestamps and statistics
Circular Buffer: Efficient memory usage for continuous data streams
Auto Port Detection: Automatic Arduino detection and connection
Multi-threading: Separate threads for data collection and visualization
Comprehensive Error Handling: Robust recovery from communication errors

🚀 Quick Start
Prerequisites

Arduino IDE
Python 3.7+
Arduino Uno/Nano or compatible board
USB cable for UART communication

Installation

Clone the repository
bashgit clone <repository-url>
cd uart-temperature-logger

Install Python dependencies
bashpip install -r requirements.txt

Upload Arduino code

Open embedded/arduino_temp_sensor.ino in Arduino IDE
Select your board and port
Upload the code


Run the Python visualizer
bashcd host
python uart_logger.py


📁 Project Structure
uart-temperature-logger/
├── embedded/
│   └── arduino_temp_sensor.ino    # Arduino temperature sensor code
├── host/
│   └── uart_logger.py             # Python data logger and visualizer
├── docs/
│   ├── README.md                  # This file
│   ├── protocol.md                # UART protocol specification
│   └── api.md                     # API documentation

🔧 Usage
Basic Usage
bash# Run with default settings
python uart_logger.py

# Specify custom port and baud rate
python uart_logger.py --port COM3 --baud 115200

# Set custom buffer size and update interval
python uart_logger.py --buffer-size 200 --update-interval 0.1

# Enable debug mode
python uart_logger.py --debug
Command Line Options

--port: Serial port (auto-detected if not specified)
--baud: Baud rate (default: 9600)
--buffer-size: Circular buffer size (default: 100)
--update-interval: Plot update interval in seconds (default: 0.5)
--log-file: Custom log file path
--debug: Enable debug output

📊 Data Output
CSV Log Format
The system generates CSV files with the following columns:

timestamp: Unix timestamp
datetime: Human-readable date/time
sensor_id: Sensor identifier
sequence: Packet sequence number
temperature: Temperature value in Celsius
checksum_valid: Data integrity status

Real-time Statistics

Current temperature
Average temperature
Min/Max values
Data reception rate
Error statistics

🛠️ Hardware Setup
Arduino Connections

LED (optional): Pin 13 (built-in LED used for status indication)
UART: USB connection for data transmission
Power: USB or external 5V supply

Wiring Diagram
Arduino Uno
├── Digital Pin 13 → Built-in LED (Status indicator)
├── USB Port → PC (UART communication)
└── Power → USB or External 5V
📈 Performance

Data Rate: 1 sample every 5 seconds
Buffer Capacity: Configurable circular buffer (default: 100 samples)
Memory Usage: ~2KB RAM on Arduino
Communication: 9600 baud UART (configurable)
Latency: <100ms end-to-end

🔍 Troubleshooting
Common Issues

Arduino not detected

Check USB connection
Verify driver installation
Try different USB port


Data corruption

Check baud rate settings
Verify cable quality
Reduce transmission frequency


Python dependencies

Update pip: pip install --upgrade pip
Install in virtual environment
Check Python version compatibility



Debug Mode
Enable debug mode for detailed logging:
bashpython uart_logger.py --debug
🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/new-feature)
Commit changes (git commit -am 'Add new feature')
Push to branch (git push origin feature/new-feature)
Create Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
👥 Authors

Sarversh -   GitHub username- Sarvesh2783

🙏 Acknowledgments

Arduino community for excellent documentation
PySerial developers for robust serial communication
Matplotlib team for powerful visualization tools

📚 References

Arduino UART Documentation
PySerial Documentation
Matplotlib Documentation