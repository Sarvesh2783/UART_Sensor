import csv
import os
from datetime import datetime
import threading
import queue

class DataLogger:
    """Handles CSV logging and data persistence"""
    
    def __init__(self, log_dir="logs", filename_prefix="temperature_log"):
        self.log_dir = log_dir
        self.filename_prefix = filename_prefix
        self.current_file = None
        self.csv_writer = None
        self.file_handle = None
        self.data_queue = queue.Queue()
        self.logging_thread = None
        self.stop_logging = threading.Event()
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Start logging thread
        self.start_logging_thread()
    
    def start_logging_thread(self):
        """Start the background logging thread"""
        self.logging_thread = threading.Thread(target=self._logging_worker, daemon=True)
        self.logging_thread.start()
    
    def _logging_worker(self):
        """Background thread worker for writing log data"""
        while not self.stop_logging.is_set():
            try:
                # Wait for data with timeout
                data = self.data_queue.get(timeout=1.0)
                if data is None:  # Poison pill to stop thread
                    break
                self._write_to_csv(data)
                self.data_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Logging error: {e}")
    
    def _get_log_filename(self):
        """Generate log filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"{self.filename_prefix}_{timestamp}.csv")
    
    def _ensure_csv_open(self):
        """Ensure CSV file is open and ready for writing"""
        if self.file_handle is None:
            self.current_file = self._get_log_filename()
            self.file_handle = open(self.current_file, 'w', newline='')
            self.csv_writer = csv.writer(self.file_handle)
            
            # Write header
            header = ['timestamp', 'sensor_id', 'sequence', 'temperature', 'raw_data']
            self.csv_writer.writerow(header)
            self.file_handle.flush()
            print(f"Created log file: {self.current_file}")
    
    def _write_to_csv(self, data):
        """Write data to CSV file"""
        try:
            self._ensure_csv_open()
            
            # Extract data fields
            timestamp = data.get('timestamp', datetime.now().isoformat())
            sensor_id = data.get('sensor_id', 'N/A')
            sequence = data.get('sequence', 0)
            temperature = data.get('temperature', 0.0)
            raw_data = data.get('raw_data', '')
            
            # Write row
            row = [timestamp, sensor_id, sequence, temperature, raw_data]
            self.csv_writer.writerow(row)
            self.file_handle.flush()
            
        except Exception as e:
            print(f"CSV write error: {e}")
    
    def log_data(self, data):
        """Add data to logging queue (thread-safe)"""
        try:
            self.data_queue.put(data, block=False)
        except queue.Full:
            print("Warning: Logging queue full, dropping data")
    
    def log_temperature(self, sensor_id, sequence, temperature, raw_data=""):
        """Convenience method to log temperature data"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'sensor_id': sensor_id,
            'sequence': sequence,
            'temperature': temperature,
            'raw_data': raw_data
        }
        self.log_data(data)
    
    def get_current_file(self):
        """Get current log file path"""
        return self.current_file
    
    def get_log_stats(self):
        """Get logging statistics"""
        stats = {
            'current_file': self.current_file,
            'queue_size': self.data_queue.qsize(),
            'logging_active': self.logging_thread.is_alive() if self.logging_thread else False
        }
        
        # Get file size if file exists
        if self.current_file and os.path.exists(self.current_file):
            stats['file_size'] = os.path.getsize(self.current_file)
        
        return stats
    
    def close(self):
        """Close logger and cleanup resources"""
        # Stop logging thread
        self.stop_logging.set()
        self.data_queue.put(None)  # Poison pill
        
        if self.logging_thread:
            self.logging_thread.join(timeout=2.0)
        
        # Close file handle
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.csv_writer = None
            print(f"Closed log file: {self.current_file}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.close()

class LogAnalyzer:
    """Analyze logged temperature data"""
    
    @staticmethod
    def read_log_file(filepath):
        """Read and parse CSV log file"""
        data = []
        try:
            with open(filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        row['temperature'] = float(row['temperature'])
                        row['sequence'] = int(row['sequence'])
                        data.append(row)
                    except (ValueError, KeyError) as e:
                        print(f"Skipping invalid row: {e}")
        except FileNotFoundError:
            print(f"Log file not found: {filepath}")
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return data
    
    @staticmethod
    def analyze_data(data):
        """Perform basic statistical analysis on temperature data"""
        if not data:
            return {}
        
        temperatures = [row['temperature'] for row in data]
        
        analysis = {
            'count': len(temperatures),
            'min': min(temperatures),
            'max': max(temperatures),
            'average': sum(temperatures) / len(temperatures),
            'range': max(temperatures) - min(temperatures)
        }
        
        # Calculate standard deviation
        if len(temperatures) > 1:
            variance = sum((t - analysis['average']) ** 2 for t in temperatures) / (len(temperatures) - 1)
            analysis['std_dev'] = variance ** 0.5
        else:
            analysis['std_dev'] = 0.0
        
        return analysis
    
    @staticmethod
    def get_recent_logs(log_dir="logs", count=5):
        """Get list of recent log files"""
        try:
            files = [f for f in os.listdir(log_dir) if f.endswith('.csv')]
            files.sort(key=lambda x: os.path.getctime(os.path.join(log_dir, x)), reverse=True)
            return files[:count]
        except Exception as e:
            print(f"Error getting recent logs: {e}")
            return []

# Example usage and testing
if __name__ == "__main__":
    import time
    import random
    
    # Test the logger
    logger = DataLogger()
    
    print("Testing DataLogger...")
    
    # Log some test data
    for i in range(10):
        temp = 20 + random.uniform(-5, 5)
        logger.log_temperature("TEMP01", i, temp, f"test_data_{i}")
        time.sleep(0.1)
    
    # Show stats
    stats = logger.get_log_stats()
    print(f"Logger stats: {stats}")
    
    # Wait for logging to complete
    time.sleep(1)
    
    # Test analyzer
    if stats['current_file']:
        data = LogAnalyzer.read_log_file(stats['current_file'])
        analysis = LogAnalyzer.analyze_data(data)
        print(f"Data analysis: {analysis}")
    
    # Cleanup
    logger.close()
    
    print("DataLogger test completed!")