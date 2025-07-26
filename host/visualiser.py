import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
from collections import deque
import threading
import time
from datetime import datetime, timedelta

class RealTimeVisualizer:
    """Real-time temperature data visualizer using matplotlib"""
    
    def __init__(self, max_points=100, update_interval=1000):
        self.max_points = max_points
        self.update_interval = update_interval
        
        # Data storage
        self.timestamps = deque(maxlen=max_points)
        self.temperatures = deque(maxlen=max_points)
        self.sensor_data = {}  # Store data for multiple sensors
        
        # Statistics
        self.stats = {
            'min_temp': float('inf'),
            'max_temp': float('-inf'),
            'avg_temp': 0,
            'data_points': 0,
            'last_update': None
        }
        
        # Threading
        self.data_lock = threading.Lock()
        self.running = False
        
        # Matplotlib setup
        self.fig = None
        self.ax = None
        self.line = None
        self.animation = None
        self.paused = False
        
        # UI elements
        self.pause_button = None
        self.clear_button = None
        self.stats_text = None
        
    def setup_plot(self):
        """Initialize the matplotlib plot"""
        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.suptitle('Real-Time Temperature Monitor', fontsize=16)
        
        # Initialize empty line
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='Temperature')
        
        # Setup axis
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Temperature (°C)')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # Set initial axis limits
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(15, 35)  # Reasonable temperature range
        
        # Add statistics text
        self.stats_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes, 
                                      verticalalignment='top', fontfamily='monospace',
                                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Add control buttons
        self.setup_buttons()
        
        # Configure plot layout
        plt.tight_layout()
        
    def setup_buttons(self):
        """Setup control buttons"""
        # Pause/Resume button
        ax_pause = plt.axes([0.7, 0.01, 0.1, 0.05])
        self.pause_button = Button(ax_pause, 'Pause')
        self.pause_button.on_clicked(self.toggle_pause)
        
        # Clear button
        ax_clear = plt.axes([0.81, 0.01, 0.1, 0.05])
        self.clear_button = Button(ax_clear, 'Clear')
        self.clear_button.on_clicked(self.clear_data)
    
    def add_data_point(self, sensor_id, temperature, timestamp=None):
        """Add a new data point (thread-safe)"""
        with self.data_lock:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Store data
            self.timestamps.append(timestamp)
            self.temperatures.append(temperature)
            
            # Store sensor-specific data
            if sensor_id not in self.sensor_data:
                self.sensor_data[sensor_id] = {
                    'timestamps': deque(maxlen=self.max_points),
                    'temperatures': deque(maxlen=self.max_points),
                    'color': self.get_sensor_color(sensor_id)
                }
            
            self.sensor_data[sensor_id]['timestamps'].append(timestamp)
            self.sensor_data[sensor_id]['temperatures'].append(temperature)
            
            # Update statistics
            self.update_stats(temperature)
    
    def get_sensor_color(self, sensor_id):
        """Get color for sensor based on ID"""
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        sensor_hash = hash(sensor_id) % len(colors)
        return colors[sensor_hash]
    
    def update_stats(self, temperature):
        """Update statistics"""
        self.stats['data_points'] += 1
        self.stats['min_temp'] = min(self.stats['min_temp'], temperature)
        self.stats['max_temp'] = max(self.stats['max_temp'], temperature)
        self.stats['last_update'] = datetime.now()
        
        # Calculate running average
        if len(self.temperatures) > 0:
            self.stats['avg_temp'] = sum(self.temperatures) / len(self.temperatures)
    
    def animate(self, frame):
        """Animation function called by matplotlib"""
        if self.paused:
            return self.line,
        
        with self.data_lock:
            if len(self.timestamps) == 0:
                return self.line,
            
            # Convert timestamps to seconds for plotting
            if len(self.timestamps) > 1:
                time_seconds = [(t - self.timestamps[0]).total_seconds() for t in self.timestamps]
            else:
                time_seconds = [0]
            
            # Update main line
            self.line.set_data(time_seconds, list(self.temperatures))
            
            # Update axis limits
            if len(time_seconds) > 0:
                self.ax.set_xlim(min(time_seconds), max(time_seconds) + 1)
            
            if len(self.temperatures) > 0:
                temp_min = min(self.temperatures)
                temp_max = max(self.temperatures)
                temp_range = temp_max - temp_min
                margin = max(temp_range * 0.1, 1)  # 10% margin or 1°C minimum
                self.ax.set_ylim(temp_min - margin, temp_max + margin)
            
            # Update statistics display
            self.update_stats_display()
        
        return self.line,
    
    def update_stats_display(self):
        """Update the statistics text display"""
        if self.stats['data_points'] == 0:
            stats_str = "No data received yet..."
        else:
            stats_str = f"""Statistics:
Points: {self.stats['data_points']}
Min: {self.stats['min_temp']:.1f}°C
Max: {self.stats['max_temp']:.1f}°C
Avg: {self.stats['avg_temp']:.1f}°C
Last: {self.stats['last_update'].strftime('%H:%M:%S') if self.stats['last_update'] else 'N/A'}
Sensors: {len(self.sensor_data)}"""
        
        self.stats_text.set_text(stats_str)
    
    def toggle_pause(self, event):
        """Toggle pause/resume"""
        self.paused = not self.paused
        self.pause_button.label.set_text('Resume' if self.paused else 'Pause')
        plt.draw()
    
    def clear_data(self, event):
        """Clear all data"""
        with self.data_lock:
            self.timestamps.clear()
            self.temperatures.clear()
            self.sensor_data.clear()
            
            # Reset statistics
            self.stats = {
                'min_temp': float('inf'),
                'max_temp': float('-inf'),
                'avg_temp': 0,
                'data_points': 0,
                'last_update': None
            }
        
        plt.draw()
    
    def start_visualization(self):
        """Start the real-time visualization"""
        self.running = True
        self.setup_plot()
        
        # Start animation
        self.animation = animation.FuncAnimation(
            self.fig, self.animate, interval=self.update_interval, 
            blit=False, cache_frame_data=False
        )
        
        plt.show()
    
    def stop_visualization(self):
        """Stop the visualization"""
        self.running = False
        if self.animation:
            self.animation.event_source.stop()
        if self.fig:
            plt.close(self.fig)
    
    def save_plot(self, filename=None):
        """Save current plot to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"temperature_plot_{timestamp}.png"
        
        if self.fig:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {filename}")
            return filename
        return None
    
    def get_data_summary(self):
        """Get summary of current data"""
        with self.data_lock:
            summary = {
                'total_points': len(self.temperatures),
                'sensors': list(self.sensor_data.keys()),
                'time_range': None,
                'temperature_range': None,
                'statistics': self.stats.copy()
            }
            
            if len(self.timestamps) > 1:
                time_span = self.timestamps[-1] - self.timestamps[0]
                summary['time_range'] = str(time_span)
            
            if len(self.temperatures) > 0:
                summary['temperature_range'] = {
                    'min': min(self.temperatures),
                    'max': max(self.temperatures)
                }
            
            return summary

class MultiSensorVisualizer(RealTimeVisualizer):
    """Extended visualizer for multiple sensors"""
    
    def __init__(self, max_points=100, update_interval=1000):
        super().__init__(max_points, update_interval)
        self.sensor_lines = {}
        
    def setup_plot(self):
        """Initialize plot for multiple sensors"""
        super().setup_plot()
        
        # Clear the default line since we'll use sensor-specific lines
        self.line.remove()
        self.line = None
    
    def animate(self, frame):
        """Animation function for multiple sensors"""
        if self.paused:
            return list(self.sensor_lines.values)