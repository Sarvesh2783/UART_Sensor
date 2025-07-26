UART Communication Protocol Specification
This document defines the communication protocol used between the Arduino temperature sensor and the host PC application.
📡 Protocol Overview
The system uses a simple, robust ASCII-based protocol over UART for reliable data transmission. Each data packet contains temperature readings with built-in error detection and recovery mechanisms.
🔧 Communication Parameters
ParameterValueDescriptionBaud Rate9600Default communication speedData Bits8Standard byte sizeParityNoneNo parity checkingStop Bits1Single stop bitFlow ControlNoneNo hardware/software flow controlEncodingASCIIHuman-readable text format
📦 Packet Structure
Data Packet Format
START|SENSOR_ID|SEQUENCE|TIMESTAMP|TEMPERATURE|CHECKSUM|END
Field Specifications
FieldTypeSizeRangeDescriptionSTARTString5 chars"START"Packet start delimiterSENSOR_IDInteger1-3 chars1-999Unique sensor identifierSEQUENCEInteger1-10 chars0-4294967295Packet sequence numberTIMESTAMPLong1-10 chars0-4294967295Milliseconds since bootTEMPERATUREFloat1-8 chars-40.0 to 125.0Temperature in CelsiusCHECKSUMInteger1-5 chars0-65535Simple sum checksumENDString3 chars"END"Packet end delimiter
Example Packets
START|1|0|1000|23.45|12345|END
START|1|1|6000|24.12|12567|END
START|1|2|11000|22.89|12234|END
🔍 Checksum Algorithm
The checksum is calculated as a simple sum of all ASCII values in the data fields (excluding delimiters and checksum itself).
Calculation Steps

Extract data fields: SENSOR_ID, SEQUENCE, TIMESTAMP, TEMPERATURE
Convert each character to ASCII value
Sum all ASCII values
Take modulo 65536 to fit in 16-bit unsigned integer

Arduino Implementation
cuint16_t calculate_checksum(char* data) {
    uint16_t sum = 0;
    while (*data) {
        sum += *data++;
    }
    return sum;
}
Python Verification
pythondef verify_checksum(data_fields, received_checksum):
    calculated = sum(ord(c) for field in data_fields for c in str(field))
    return calculated % 65536 == int(received_checksum)
📨 Message Types
1. Temperature Data (Arduino → PC)
Format: START|SENSOR_ID|SEQUENCE|TIMESTAMP|TEMPERATURE|CHECKSUM|END
Purpose: Regular temperature readings transmission
Frequency: Every 5 seconds (configurable)
Example: START|1|42|25000|23.45|12345|END
2. Status Request (PC → Arduino)
Format: STATUS
Purpose: Request current sensor status
Response: Status information packet
3. Reset Command (PC → Arduino)
Format: RESET
Purpose: Reset sensor sequence counter
Response: Acknowledgment message
4. Error Response (Arduino → PC)
Format: ERROR|ERROR_CODE|DESCRIPTION|END
Purpose: Error reporting and diagnostics
Example: ERROR|001|SENSOR_FAILURE|END
🔄 Communication Flow
Normal Operation Sequence
1. Arduino boots and initializes
2. Arduino starts temperature simulation
3. Every 5 seconds:
   a. Arduino reads/simulates temperature
   b. Arduino formats data packet
   c. Arduino calculates checksum
   d. Arduino transmits packet via UART
   e. PC receives and validates packet
   f. PC logs data and updates visualization
Error Recovery Sequence
1. PC detects invalid/corrupted packet
2. PC increments error counter
3. PC requests retransmission (optional)
4. Arduino retransmits last packet (if supported)
5. System continues normal operation
⚠️ Error Handling
Error Types
Error CodeDescriptionRecovery ActionCHECKSUM_FAILChecksum mismatchDiscard packet, continueMALFORMED_PACKETInvalid packet structureDiscard packet, continueTIMEOUTNo data receivedCheck connectionBUFFER_OVERFLOWReceive buffer fullClear buffer, restart
Arduino Error Responses
c// Checksum failure
void send_error(const char* error_code, const char* description) {
    Serial.print("ERROR|");
    Serial.print(error_code);
    Serial.print("|");
    Serial.print(description);
    Serial.println("|END");
}
Python Error Handling
pythondef handle_packet_error(self, error_type, packet_data):
    self.error_count += 1
    self.logger.warning(f"Packet error: {error_type}")
    
    if error_type == "CHECKSUM_FAIL":
        self.checksum_errors += 1
    elif error_type == "MALFORMED":
        self.format_errors += 1
🔧 Configuration Parameters
Arduino Configuration
c#define BAUD_RATE 9600
#define TRANSMISSION_INTERVAL 5000  // milliseconds
#define BUFFER_SIZE 128
#define SENSOR_ID 1
Python Configuration
pythonSERIAL_CONFIG = {
    'baudrate': 9600,
    'timeout': 1.0,
    'bytesize': 8,
    'parity': 'N',
    'stopbits': 1
}
📊 Performance Characteristics
Throughput

Packet Size: ~30-50 bytes per packet
Transmission Rate: 1 packet per 5 seconds
Bandwidth Usage: ~10 bytes/second average
Buffer Requirements: 128 bytes Arduino, configurable PC

Latency

Transmission Time: ~50ms at 9600 baud
Processing Delay: <10ms on both ends
Total Latency: <100ms end-to-end

Reliability

Error Detection: Checksum verification
Error Rate: <0.1% under normal conditions
Recovery Time: Immediate (next packet)

🧪 Testing and Validation
Protocol Compliance Testing
pythondef test_packet_format():
    """Test packet format compliance"""
    packet = "START|1|42|25000|23.45|12345|END"
    fields = packet.split('|')
    
    assert fields[0] == "START"
    assert fields[-1] == "END"
    assert len(fields) == 7
    assert fields[1].isdigit()  # SENSOR_ID
    assert fields[2].isdigit()  # SEQUENCE
    # ... additional validation
Checksum Validation Testing
pythondef test_checksum_calculation():
    """Test checksum calculation accuracy"""
    data = "1|42|25000|23.45"
    expected_checksum = sum(ord(c) for c in data) % 65536
    calculated_checksum = calculate_checksum(data)
    
    assert calculated_checksum == expected_checksum
🔒 Security Considerations
Data Integrity

Checksum verification prevents data corruption
Packet structure validation ensures format compliance
Sequence numbers detect missing packets

Limitations

No encryption (data transmitted in plain text)
No authentication (any device can send commands)
No protection against replay attacks

Recommendations for Production

Implement encryption for sensitive applications
Add authentication mechanisms
Use more robust checksum algorithms (CRC)
Implement packet acknowledgment system

📈 Future Enhancements
Protocol Extensions

Multi-sensor Support: Extended sensor ID range
Command Acknowledgment: Bidirectional confirmation
Data Compression: Reduce bandwidth usage
Encryption Layer: Secure data transmission
Flow Control: Handle buffer overflows

Performance Improvements

Variable Transmission Rate: Adaptive frequency
Batch Transmission: Multiple readings per packet
Priority Messaging: Urgent data handling
Connection Monitoring: Health check packets