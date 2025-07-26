# 🌡️ UART-Based Temperature Sensor Logger and Visualizer

A complete embedded system for **real-time temperature monitoring** using **Arduino + Python**. This project showcases live data acquisition, UART communication, and real-time plotting with robust error handling and data logging.

---

## 🔧 Key Features

### 🛠 Embedded System (Arduino)

* **Simulated Temperature Generation**: Realistic sensor behavior using sine waves and noise.
* **UART Communication**: Structured packet format with checksum verification.
* **Memory-Safe Buffering**: Static buffer for safe data transmission.
* **Error Detection**: Checksums ensure data integrity.
* **LED Indicators**: Visual status feedback on data transmission.
* **Command Support**: Basic serial command interface for manual control.

### 🖥 Host System (Python)

* **Live Visualization**: Real-time temperature plotting using `matplotlib`.
* **Data Logging**: CSV file generation with timestamped data.
* **Circular Buffer**: Efficient memory use for continuous streams.
* **Auto Port Detection**: Automatically connects to Arduino.
* **Multi-threaded**: Separate threads for data reading and plotting.
* **Robust Error Handling**: Recovers from common UART issues gracefully.

---

## 🚀 Quick Start

### 📦 Prerequisites

* Arduino IDE
* Python 3.7+
* Arduino Uno/Nano
* USB cable

### 🔌 Installation

```bash
git clone <repository-url>
cd uart-temperature-logger
pip install -r requirements.txt
```

### 🔄 Upload Arduino Code

1. Open `embedded/arduino_temp_sensor.ino` in Arduino IDE
2. Select your board and port
3. Upload the sketch

### 📈 Run the Python Logger

```bash
cd host
python uart_logger.py
```

---

## 📁 Project Structure

```
uart-temperature-logger/
├── embedded/
│   └── sensor.ino     # Arduino temperature simulation code
├── host/
│   ├── uart_logger.py                  
│   ├── uart_protocol.py                 
│   └── visuliser.py
├── docs/
│   ├── README.md                   # Project documentation
│   ├── protocol.md                 # UART packet structure
│   └── api.md                      # Command line interface doc
```

---

## ⚙️ Usage

### 🧪 Basic Run

```bash
python uart_logger.py
```

### 🔧 Custom Configuration

```bash
python uart_logger.py --port COM3 --baud 115200 --buffer-size 200 --update-interval 0.1 --debug
```

### 📋 Command Line Options

* `--port`: Serial port (auto-detected if not specified)
* `--baud`: Baud rate (default: 9600)
* `--buffer-size`: Circular buffer size (default: 100)
* `--update-interval`: Plot refresh interval (default: 0.5s)
* `--log-file`: Custom output CSV path
* `--debug`: Verbose debug logging

---

## 📊 Output Format

### 🗃 CSV Columns

* `timestamp`: Unix time
* `datetime`: ISO 8601 format
* `sensor_id`: ID or label
* `sequence`: Packet sequence number
* `temperature`: Celsius reading
* `checksum_valid`: Boolean

### 📈 Live Stats

* Current temperature
* Min/Max/Avg
* Data rate (samples/sec)
* Error count and loss rate

---

## 🔌 Hardware Setup

### 🧰 Connections

* LED: Pin 13 (on-board)
* UART: USB (TX/RX over serial)
* Power: USB or external 5V

### 🖼️ Wiring Diagram

```
Arduino Uno
├── Pin 13         → Built-in LED
├── USB Port       → PC (UART Comm)
└── 5V             → Power
```

---

## ⚙️ Performance

* **Data Rate**: 1 sample every 5 seconds
* **Buffer Size**: 100 samples (configurable)
* **RAM Usage**: \~2KB on Arduino
* **Baud Rate**: 9600 (adjustable)
* **Latency**: <100ms round trip

---

## 🧪 Troubleshooting

### 🛑 Arduino Not Detected

* Check USB cable and port
* Reinstall drivers if needed

### 🛠 Data Corruption

* Ensure baud rates match
* Use quality USB cables
* Lower transmission frequency if needed

### 🐍 Python Issues

* Use virtual environments
* Upgrade pip and reinstall packages
* Confirm Python 3.7+ is used

### 🔍 Debug Mode

```bash
python uart_logger.py --debug
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request 🚀

---

## 📄 License

MIT License – see `LICENSE` file for details.

---

## 👨‍💻 Author

**Sarvesh** – [GitHub: Sarvesh2783](https://github.com/Sarvesh2783)

---

## 🙏 Acknowledgments

* Arduino community
* PySerial developers
* Matplotlib team

---

## 📚 References

* [Arduino UART Docs](https://www.arduino.cc/en/Serial/Begin)
* [PySerial Docs](https://pythonhosted.org/pyserial/)
* [Matplotlib Docs](https://matplotlib.org/stable/index.html)
