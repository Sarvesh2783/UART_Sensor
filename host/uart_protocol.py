import re
from datetime import datetime
from typing import Optional, Dict, Any

class UARTProtocol:
    """Handles UART protocol parsing and validation"""
    
    # Protocol constants
    START_MARKER = "START"
    END_MARKER = "END"
    FIELD_SEPARATOR = "|"
    
    # Expected packet format: START|SENSOR_ID|SEQUENCE|TIMESTAMP|TEMPERATURE|CHECKSUM|END
    PACKET_FIELDS = ['start', 'sensor_id', 'sequence', 'timestamp', 'temperature', 'checksum', 'end']
    EXPECTED_FIELD_COUNT = len(PACKET_FIELDS)
    
    def __init__(self):
        self.stats = {
            'packets_received': 0,
            'packets_valid': 0,
            'packets_invalid': 0,
            'checksum_errors': 0,
            'format_errors': 0,
            'last_sequence': {}  # Track sequence per sensor
        }
    
    def parse_packet(self, raw_data: str) -> Optional[Dict[str, Any]]:
        """
        Parse incoming UART packet
        
        Args:
            raw_data: Raw string data from UART
            
        Returns:
            Dictionary with parsed data if valid, None if invalid
        """
        self.stats['packets_received'] += 1
        
        try:
            # Clean the data
            raw_data = raw_data.strip()
            
            # Split by field separator
            fields = raw_data.split(self.FIELD_SEPARATOR)
            
            # Validate field count
            if len(fields) != self.EXPECTED_FIELD_COUNT:
                self.stats['format_errors'] += 1
                self.stats['packets_invalid'] += 1
                return None
            
            # Validate start and end markers
            if fields[0] != self.START_MARKER or fields[-1] != self.END_MARKER:
                self.stats['format_errors'] += 1
                self.stats['packets_invalid'] += 1
                return None
            
            # Extract fields
            packet_data = {
                'start': fields[0],
                'sensor_id': fields[1],
                'sequence': int(fields[2]),
                'timestamp': int(fields[3]),
                'temperature': float(fields[4]),
                'checksum': int(fields[5]),
                'end': fields[6],
                'raw_data': raw_data,
                'receive_time': datetime.now()
            }
            
            # Validate checksum
            if not self._validate_checksum(packet_data):
                self.stats['checksum_errors'] += 1
                self.stats['packets_invalid'] += 1
                return None
            
            # Check sequence number
            self._check_sequence(packet_data)
            
            # Convert timestamp to readable format
            packet_data['timestamp_readable'] = datetime.fromtimestamp(packet_data['timestamp'] / 1000.0)
            
            self.stats['packets_valid'] += 1
            return packet_data
            
        except (ValueError, IndexError) as e:
            self.stats['format_errors'] += 1
            self.stats['packets_invalid'] += 1
            return None
    
    def _validate_checksum(self, packet_data: Dict) -> bool:
        """Validate packet checksum"""
        try:
            # Calculate expected checksum (sum of sensor_id chars + sequence + temperature)
            sensor_sum = sum(ord(c) for c in packet_data['sensor_id'])
            expected_checksum = (sensor_sum + packet_data['sequence'] + int(packet_data['temperature'])) % 256
            
            return packet_data['checksum'] == expected_checksum
        except:
            return False
    
    def _check_sequence(self, packet_data: Dict):
        """Check for missing sequence numbers"""
        sensor_id = packet_data['sensor_id']
        current_seq = packet_data['sequence']
        
        if sensor_id in self.stats['last_sequence']:
            last_seq = self.stats['last_sequence'][sensor_id]
            if current_seq != last_seq + 1:
                missing_count = current_seq - last_seq - 1
                if missing_count > 0:
                    packet_data['missing_packets'] = missing_count
        
        self.stats['last_sequence'][sensor_id] = current_seq
    
    def create_packet(self, sensor_id: str, sequence: int, temperature: float) -> str:
        """
        Create a UART packet (for testing purposes)
        
        Args:
            sensor_id: Sensor identifier
            sequence: Sequence number
            temperature: Temperature value
            
        Returns:
            Formatted packet string
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        
        # Calculate checksum
        sensor_sum = sum(ord(c) for c in sensor_id)
        checksum = (sensor_sum + sequence + int(temperature)) % 256
        
        # Build packet
        packet = f"{self.START_MARKER}{self.FIELD_SEPARATOR}"
        packet += f"{sensor_id}{self.FIELD_SEPARATOR}"
        packet += f"{sequence}{self.FIELD_SEPARATOR}"
        packet += f"{timestamp}{self.FIELD_SEPARATOR}"
        packet += f"{temperature:.2f}{self.FIELD_SEPARATOR}"
        packet += f"{checksum}{self.FIELD_SEPARATOR}"
        packet += f"{self.END_MARKER}"
        
        return packet
    
    def get_stats(self) -> Dict:
        """Get protocol statistics"""
        stats = self.stats.copy()
        
        # Calculate success rate
        if stats['packets_received'] > 0:
            stats['success_rate'] = (stats['packets_valid'] / stats['packets_received']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset protocol statistics"""
        self.stats = {
            'packets_received': 0,
            'packets_valid': 0,
            'packets_invalid': 0,
            'checksum_errors': 0,
            'format_errors': 0,
            'last_sequence': {}
        }

class UARTBuffer:
    """Handles buffering of incomplete UART data"""
    
    def __init__(self, max_buffer_size: int = 1024):
        self.buffer = ""
        self.max_buffer_size = max_buffer_size
        self.packet_pattern = re.compile(r'START\|[^|]+\|\d+\|\d+\|[\d.-]+\|\d+\|END')
    
    def add_data(self, data: str) -> list:
        """
        Add new data to buffer and extract complete packets
        
        Args:
            data: New data from UART
            
        Returns:
            List of complete packets
        """
        self.buffer += data
        
        # Prevent buffer overflow
        if len(self.buffer) > self.max_buffer_size:
            # Keep only the last half of the buffer
            self.buffer = self.buffer[self.max_buffer_size // 2:]
        
        # Extract complete packets
        packets = []
        matches = self.packet_pattern.findall(self.buffer)
        
        for match in matches:
            packets.append(match)
            # Remove processed packet from buffer
            self.buffer = self.buffer.replace(match, '', 1)
        
        return packets
    
    def clear_buffer(self):
        """Clear the internal buffer"""
        self.buffer = ""
    
    def get_buffer_size(self) -> int:
        """Get current buffer size"""
        return len(self.buffer)

class CommandProcessor:
    """Handles command processing for UART communication"""
    
    def __init__(self):
        self.commands = {
            'STATUS': self._handle_status,
            'RESET': self._handle_reset,
            'CONFIG': self._handle_config,
            'START': self._handle_start,
            'STOP': self._handle_stop
        }
    
    def process_command(self, command: str, args: list = None) -> str:
        """
        Process incoming command
        
        Args:
            command: Command string
            args: Command arguments
            
        Returns:
            Response string
        """
        command = command.upper().strip()
        
        if command in self.commands:
            return self.commands[command](args or [])
        else:
            return f"ERROR: Unknown command '{command}'"
    
    def _handle_status(self, args: list) -> str:
        """Handle STATUS command"""
        return "OK: System operational"
    
    def _handle_reset(self, args: list) -> str:
        """Handle RESET command"""
        return "OK: Reset requested"
    
    def _handle_config(self, args: list) -> str:
        """Handle CONFIG command"""
        if not args:
            return "ERROR: CONFIG requires parameters"
        return f"OK: Config updated with {', '.join(args)}"
    
    def _handle_start(self, args: list) -> str:
        """Handle START command"""
        return "OK: Data transmission started"
    
    def _handle_stop(self, args: list) -> str:
        """Handle STOP command"""
        return "OK: Data transmission stopped"
    
    def get_available_commands(self) -> list:
        """Get list of available commands"""
        return list(self.commands.keys())

# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Test the protocol parser
    protocol = UARTProtocol()
    uart_buffer = UARTBuffer()
    command_processor = CommandProcessor()
    
    print("Testing UART Protocol...")
    
    # Test packet creation and parsing
    test_packet = protocol.create_packet("TEMP01", 123, 25.67)
    print(f"Created packet: {test_packet}")
    
    # Parse the packet
    parsed = protocol.parse_packet(test_packet)
    if parsed:
        print(f"Parsed successfully: {parsed['sensor_id']}, Temp: {parsed['temperature']}°C")
    else:
        print("Parsing failed!")
    
    # Test buffer with partial data
    partial_data1 = "START|TEMP01|124|"
    partial_data2 = "1640995200000|26.43|142|END"
    
    packets1 = uart_buffer.add_data(partial_data1)
    print(f"Packets from partial data 1: {len(packets1)}")
    
    packets2 = uart_buffer.add_data(partial_data2)
    print(f"Packets from partial data 2: {len(packets2)}")
    
    # Test invalid packet
    invalid_packet = "START|TEMP01|125|1640995200000|27.89|999|END"  # Wrong checksum
    parsed_invalid = protocol.parse_packet(invalid_packet)
    print(f"Invalid packet parsed: {parsed_invalid is not None}")
    
    # Test command processor
    commands_to_test = ['STATUS', 'CONFIG interval 1000', 'INVALID']
    for cmd in commands_to_test:
        parts = cmd.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        response = command_processor.process_command(command, args)
        print(f"Command '{cmd}' -> {response}")
    
    # Show statistics
    stats = protocol.get_stats()
    print(f"Protocol stats: {stats}")
    
    print("UART Protocol test completed!")