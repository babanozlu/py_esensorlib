#!/usr/bin/env python
"""
Quick launcher for IMU Monitor
Run this from the workspace root directory
"""

import sys
import os

# Add the esensorlib to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py_esensorlib', 'src'))

# Import and run the monitor
from esensorlib.example.imu_monitor import IMUMonitor

if __name__ == "__main__":
    # You can change these parameters as needed
    PORT = 'COM8'      # Change to your COM port (e.g., 'COM8', '/dev/ttyUSB0')
    BAUDRATE = 460800  # Change if your IMU uses different baudrate
    
    print("Starting IMU Monitor...")
    print(f"Port: {PORT}, Baudrate: {BAUDRATE}")
    print("\nTo change port/baudrate, edit run_imu_monitor.py\n")
    
    try:
        monitor = IMUMonitor(port=PORT, speed=BAUDRATE)
        monitor.run()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("  1. The IMU is connected to the correct port")
        print("  2. No other program is using the port")
        print("  3. esensorlib is installed (run: pip install -e py_esensorlib)")
        sys.exit(1)

