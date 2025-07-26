# API Documentation

This document provides comprehensive API documentation for both the Arduino embedded system and Python host application components of the UART Temperature Logger.

## 🔧 Arduino API

### Core Functions

#### `setup()`
**Description**: Initialize the Arduino system, configure UART communication, and set up hardware peripherals.

**Parameters**: None

**Returns**: void

**Usage**:
```c
void setup() {
    Serial.begin(BAUD_RATE);
    pinMode(STATUS_LED_PIN, OUTPUT);
    init_temperature_simulation();
}
```

#### `loop()`
**Description**: Main execution loop that handles temperature reading, data transmission, and command processing.

**Parameters**: None

**Returns**: void

**Execution Flow**:
1. Check for incoming commands
2. Read/simulate temperature data
3. Format and transmit data packet
4. Update status indicators
5. Manage timing intervals

---

### Temperature Simulation Functions

#### `init_temperature_simulation()`
**Description**: Initialize temperature simulation parameters including base temperature, amplitude, and noise characteristics.

**Parameters**: None

**Returns**: void

**Configuration**:
```c
base_temperature = 23.0;    // Base temperature in Celsius
amplitude = 5.0;            // Sine wave amplitude
noise_factor = 0.5;         // Random noise level
```

#### `simulate_temperature()`
**Description**: Generate realistic temperature data using sine wave patterns and random noise.

**Parameters**: None

**Returns**: `float` - Simulated temperature value in Celsius

**Algorithm**:
```c
float simulate_temperature() {
    unsigned long current_time = millis();
    float sine_component = sin(current_time * 0.001 * 0.1) * amplitude;
    float noise = (random(-100, 100) / 100.0) * noise_factor;
    return base_temperature + sine_component + noise;
}
```

**Range**: -40.0°C to +125.0°C (sensor typical range)

---

### Data Transmission Functions

#### `format_data_packet(float temperature, char* buffer, size_t buffer_size)`
**Description**: Format temperature data into protocol-compliant packet string.

**Parameters**:
- `temperature`: Temperature value to transmit
- `buffer`: Output buffer for formatted packet
- `buffer_size`: Maximum buffer size

**Returns**: `bool` - Success/failure status

**Packet Format**: `START|SENSOR_ID|SEQUENCE|TIMESTAMP|TEMPERATURE|CHECKSUM|END`

**Example**:
```c
char packet_buffer[PACKET_BUFFER_SIZE];
bool success = format_data_packet(23.45, packet_buffer, sizeof(packet_buffer));
```

#### `calculate_checksum(const char* data)`
**Description**: Calculate simple sum checksum for data integrity verification.

**Parameters**:
- `data`: Null-terminated string containing data fields

**Returns**: `uint16_t` - Calculated checksum value

**Algorithm**:
```c
uint16_t calculate_checksum(const char* data) {
    uint16_t sum = 0;
    while (*data) {
        sum += (uint8_t)*data++;
    }
    return sum % 65536;
}
```

#### `transmit_packet(const char* packet)`
**Description**: Transmit formatted packet via UART with error handling.

**Parameters**:
- `packet`: Formatted packet string to transmit

**Returns**: `bool` - Transmission success status

**Implementation**:
```c
bool transmit_packet(const char* packet) {
    Serial.println(packet);
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(50);
    digitalWrite(STATUS_LED_PIN, LOW);
    return true;
}
```

---

### Command Processing Functions

#### `process_commands()`
**Description**: Check for and process incoming commands from host PC.

**Parameters**: None

**Returns**: void

**Supported Commands**:
- `STATUS`: Return current system status
- `RESET`: Reset sequence counter and statistics
- `CONFIG`: Modify configuration parameters

**Implementation**:
```c
void process_commands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command == "STATUS") {
            send_status_response();
        } else if (command == "RESET") {
            reset_system();
        }
    }
}
```

---

### Utility Functions

#### `blink_status_led(int count, int delay_ms)`
**Description**: Provide visual feedback through LED blinking patterns.

**Parameters**:
- `count`: Number of blinks
- `delay_ms`: Delay between blinks in milliseconds

**Returns**: void

#### `get_free_memory()`
**Description**: Return available RAM for debugging purposes.

**Parameters**: None

**Returns**: `int` - Free memory in bytes

---

## 🐍 Python Host API

### Core Classes

#### `class UARTLogger`
**Description**: Main class for UART communication, data logging, and visualization.

**Constructor**:
```python
def __init__(self, port=None, baud_rate=9600, buffer_size=100):
    """
    Initialize UART logger
    
    Args:
        port (str): Serial port name (auto-detect if None)
        baud_rate (int): Communication speed
        buffer_size (int): Circular buffer size
    """
```

**Key Attributes**:
- `serial_connection`: PySerial connection object
- `data_buffer`: Circular buffer for temperature data
- `logger`: Python logging instance
- `statistics`: Data collection statistics

---

### Connection Management

#### `connect()`
**Description**: Establish serial connection with Arduino device.

**Parameters**: None

**Returns**: `bool` - Connection success status

**Features**:
- Automatic port detection
- Connection validation
- Error recovery mechanisms

**Example**:
```python
logger = UARTLogger()
if logger.connect():
    print("Connected successfully")
    logger.start_logging()
```

#### `disconnect()`
**Description**: Safely close serial connection and cleanup resources.

**Parameters**: None

**Returns**: void

#### `auto_detect_port()`
**Description**: Automatically detect Arduino connection port.

**Parameters**: None

**Returns**: `str` - Detected port name or None

**Implementation**:
```python
def auto_detect_port(self):
    """Scan available ports for Arduino device"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'CH340' in port.description:
            return port.device
    return None
```

---

### Data Collection

#### `start_logging()`
**Description**: Begin continuous data collection in separate thread.

**Parameters**: None

**Returns**: void

**Features**:
- Non-blocking operation
- Automatic error recovery
- Real-time data validation

#### `stop_logging()`
**Description**: Stop data collection and cleanup threads.

**Parameters**: None

**Returns**: void

#### `read_packet()`
**Description**: Read and validate single data packet from Arduino.

**Parameters**: None

**Returns**: `dict` - Parsed packet data or None if invalid

**Return Format**:
```python
{
    'sensor_id': int,
    'sequence': int,
    'timestamp': int,
    'temperature': float,
    'checksum_valid': bool,
    'received_time': datetime
}
```

#### `validate_packet(packet_string)`
**Description**: Validate packet format and checksum integrity.

**Parameters**:
- `packet_string`: Raw packet string from Arduino

**Returns**: `dict` - Validated packet data or None

**Validation Steps**:
1. Check packet format and delimiters
2. Verify field count and types
3. Calculate and verify checksum
4. Range check temperature value

---

### Data Storage

#### `class CircularBuffer`
**Description**: Efficient circular buffer implementation for continuous data streams.

**Constructor**:
```python
def __init__(self, size):
    """
    Initialize circular buffer
    
    Args:
        size (int): Maximum buffer size
    """
```

**Methods**:

##### `append(data)`
**Parameters**: `data` - Data item to add
**Returns**: void
**Description**: Add new data item, overwrites oldest if buffer full

##### `get_data(count=None)`
**Parameters**: `count` - Number of recent items to retrieve
**Returns**: `list` - Requested data items
**Description**: Retrieve data items from buffer

##### `is_full()`
**Parameters**: None
**Returns**: `bool` - True if buffer is at capacity

##### `clear()`
**Parameters**: None
**Returns**: void
**Description**: Clear all data from buffer

---

### Data Logging

#### `log_to_csv(filename=None)`
**Description**: Export collected data to CSV file format.

**Parameters**:
- `filename`: Custom filename (auto-generated if None)

**Returns**: `str` - Path to created log file

**CSV Format**:
```csv
timestamp,datetime,sensor_id,sequence,temperature,checksum_valid
1609459200,2021-01-01 00:00:00,1,0,23.45,True
1609459205,2021-01-01 00:00:05,1,1,23.67,True
```

#### `get_statistics()`
**Description**: Calculate and return data collection statistics.

**Parameters**: None

**Returns**: `dict` - Statistical summary

**Statistics Included**:
```python
{
    'total_packets': int,
    'valid_packets': int,
    'error_rate': float,
    'avg_temperature': float,
    'min_temperature': float,
    'max_temperature': float,
    'data_rate': float,  # packets per second
    'uptime': float      # seconds
}
```

---

### Visualization

#### `class RealTimePlotter`
**Description**: Real-time matplotlib visualization for temperature data.

**Constructor**:
```python
def __init__(self, buffer_size=100, update_interval=0.5):
    """
    Initialize real-time plotter
    
    Args:
        buffer_size (int): Data points to display
        update_interval (float): Update frequency in seconds
    """
```

#### `start_plotting()`
**Description**: Begin real-time visualization in separate thread.

**Parameters**: None

**Returns**: void

**Features**:
- Live temperature trend plotting
- Statistics display overlay
- Configurable update rates
- Error status indicators

#### `update_plot(frame)`
**Description**: Update plot with latest data (called by matplotlib animation).

**Parameters**:
- `frame`: Animation frame number

**Returns**: `list` - Updated plot elements

#### `stop_plotting()`
**Description**: Stop visualization and cleanup matplotlib resources.

**Parameters**: None

**Returns**: void

---

### Configuration

#### `class Config`
**Description**: Configuration management for logger settings.

**Default Configuration**:
```python
DEFAULT_CONFIG = {
    'serial': {
        'baud_rate': 9600,
        'timeout': 1.0,
        'port': None  # Auto-detect
    },
    'logging': {
        'buffer_size': 100,
        'log_level': 'INFO',
        'csv_output': True
    },
    'visualization': {
        'update_interval': 0.5,
        'window_size': 100,
        'auto_scale': True
    }
}
```

#### `load_config(filename)`
**Description**: Load configuration from JSON file.

**Parameters**:
- `filename`: Path to configuration file

**Returns**: `dict` - Loaded configuration

#### `save_config(config, filename)`
**Description**: Save configuration to JSON file.

**Parameters**:
- `config`: Configuration dictionary
- `filename`: Output file path

**Returns**: `bool` - Save success status

---

### Error Handling

#### `class UARTLoggerError(Exception)`
**Description**: Custom exception class for UART logger errors.

**Error Types**:
- `ConnectionError`: Serial communication failures
- `DataValidationError`: Invalid packet data
- `ConfigurationError`: Invalid configuration settings

#### `handle_communication_error(error)`
**Description**: Handle serial communication errors with recovery attempts.

**Parameters**:
- `error`: Exception object

**Returns**: `bool` - Recovery success status

**Recovery Strategies**:
1. Reconnection attempts
2. Buffer clearing
3. Baud rate adjustment
4. Port re-detection

---

### Command Line Interface

#### `main(args)`
**Description**: Command-line entry point with argument parsing.

**Parameters**:
- `args`: Command line arguments

**Returns**: `int` - Exit code

**Available Arguments**:
```bash
python uart_logger.py [options]

Options:
  --port PORT           Serial port name
  --baud RATE          Baud rate (default: 9600)
  --buffer-size SIZE   Circular buffer size (default: 100)
  --update-interval SEC Update interval (default: 0.5)
  --log-file PATH      Custom log file path
  --config FILE        Configuration file path
  --debug              Enable debug output
  --no-gui             Disable visualization (logging only)
```

---

### Usage Examples

#### Basic Usage
```python
from uart_logger import UARTLogger

# Create logger instance
logger = UARTLogger(baud_rate=9600, buffer_size=200)

# Connect and start logging
if logger.connect():
    logger.start_logging()
    
    # Run for 60 seconds
    time.sleep(60)
    
    # Get statistics and save data
    stats = logger.get_statistics()
    log_file = logger.log_to_csv()
    
    logger.stop_logging()
    logger.disconnect()
```

#### Advanced Configuration
```python
# Custom configuration
config = {
    'serial': {'baud_rate': 115200, 'timeout': 2.0},
    'logging': {'buffer_size': 500},
    'visualization': {'update_interval': 0.1}
}

logger = UARTLogger()
logger.load_config_dict(config)
logger.connect()
logger.start_logging()
logger.start_plotting()
```

#### Error Handling
```python
try:
    logger = UARTLogger()
    logger.connect()
    logger.start_logging()
    
    while True:
        time.sleep(1)
        
except UARTLoggerError as e:
    print(f"Logger error: {e}")
    
except KeyboardInterrupt:
    print("Stopping logger...")
    
finally:
    logger.stop_logging()
    logger.disconnect()
```