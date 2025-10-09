# IMU Real-Time Monitor

Real-time monitoring tool for Epson G366-PDG0 IMU sensor.

## Description

This script provides a simple, real-time console display of IMU data including:
- **Heading** (yaw angle in degrees)
- **Heel** (roll angle in degrees)
- **Pitch** (pitch angle in degrees)
- **Roll Period** (time between roll cycles)
- **Roll Amplitude** (maximum roll angles for port and starboard)
- **Surge, Sway, Heave** (linear accelerations)
- **Temperature** (sensor temperature in °C)

## Requirements

- Python 3.7+
- esensorlib package installed
- Epson G366-PDG0 IMU connected via UART

## Installation

1. Install the esensorlib package:
```bash
cd py_esensorlib
pip install -e .
```

## Usage

### Basic Usage

Run the monitor with default settings (COM8 @ 460800 baud):

```bash
python src/esensorlib/example/imu_monitor.py
```

### Custom Port Configuration

To use a different COM port or baud rate, edit the last line in `imu_monitor.py`:

```python
# For Windows
monitor = IMUMonitor(port='COM8', speed=460800)

# For Linux
monitor = IMUMonitor(port='/dev/ttyUSB0', speed=460800)
```

### Running the Monitor

1. Connect your IMU to the specified COM port
2. Run the script
3. Enter the initial heading value when prompted (0-360 degrees)
4. Watch real-time IMU data in the console
5. Press CTRL+C to stop and see session summary

## Example Output

```
================================================================================
  Epson IMU G366-PDG0 Real-Time Monitor
================================================================================

Initializing IMU on COM8 @ 460800 baud...

Device Information:
  Product ID:  G366PDG0
  Version:     0103
  Serial:      W0000001

Configuring IMU...

Enter initial heading (0-360 degrees): 45

Configuration complete!
Starting data acquisition... (Press CTRL+C to stop)

================================================================================

Heading:  45.23° | Heel:  -2.15° | Pitch:   0.87° | Roll Period:  3.2s | Roll Amp Port/Stbd:  2.50°/ 3.10° | Surge:  0.02 | Sway: -0.01 | Heave:  1.00 | Temp:  25.3°C
```

## Configuration

The monitor is configured with the following default settings:
- **Output Rate**: 200 Hz
- **Filter**: Moving Average (16 samples)
- **Temperature**: Enabled
- **Data Format**: 32-bit
- **Accelerometer Range**: 8G

To modify these settings, edit the `set_config()` call in the `__init__` method of the `IMUMonitor` class.

## Troubleshooting

### Port Not Found
- Verify the COM port name in Device Manager (Windows) or `ls /dev/tty*` (Linux)
- Check that the IMU is properly connected
- Ensure no other program is using the port

### Communication Error
- Verify the baud rate matches your IMU configuration
- Check cable connections
- Try power cycling the IMU

### Import Error
- Make sure esensorlib is installed: `pip install -e .`
- Verify you're in the correct directory

## License

MIT License - Copyright (c) 2023, 2025 Seiko Epson Corporation

