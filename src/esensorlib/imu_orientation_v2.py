#!/usr/bin/env python

"""
IMU Orientation Monitor for Epson G366-PDG0
Real-time display of IMU data in console
Standalone version - all code included

================================================================================
HIZLI AYAR REHBERİ
================================================================================

Bu dosyada değiştirebileceğin 2 ana parametre var:

1. ALPHA (Satır ~113):
   - Yazılım filtre hızı
   - Düşük = Daha stabil, Yüksek = Daha hızlı tepki
   - Önerilen: 0.02-0.05 (deniz), 0.10-0.15 (drone)

2. GYRO_THRESHOLD (Satır ~141):
   - Gürültü bastırma eşiği (°/s)
   - Düşük = Daha hassas, Yüksek = Daha stabil
   - Önerilen: 0.2-0.3 (deniz), 0.1-0.2 (genel)

HAZIR PROFİLLER (FILTER_PROFILES.md dosyasına bak):
- Profil 0: ULTRA STABİL  (alpha=0.01, threshold=0.4)   - Liman/test
- Profil 1: ÇOK STABİL    (alpha=0.03, threshold=0.25)  - Gemi/deniz ⭐ ŞU AN
- Profil 2: DENGELİ       (alpha=0.08, threshold=0.15)  - Genel
- Profil 3: HIZLI         (alpha=0.15, threshold=0.1)   - Manevra
- Profil 4: ÇOK HIZLI     (alpha=0.20, threshold=0.05)  - Drone

NOT: Buffer temizleme özelliği eklendi - gerçek zamanlı performans için

NOT: IMU donanım filtresi (OUTPUT_RATE ve FILTER_SEL) için
     imu_configuration_v2.py dosyasını kullan ve flash'a kaydet.

================================================================================
"""

import sys
import math
import time
from collections import deque

from esensorlib import sensor_device


class IMUMonitor:
    def __init__(self, port='/dev/ttyLP2', speed=460800):
        """
        Initialize IMU Monitor
        
        Parameters
        ----------
        port : str
            Serial port name (e.g., 'COM8' on Windows, '/dev/ttyUSB0' on Linux)
        speed : int
            Baudrate (default: 460800)
        """
        print(f"\n{'='*80}")
        print(f"  Epson IMU G366-PDG0 Real-Time Monitor")
        print(f"{'='*80}")
        print(f"\nInitializing IMU on {port} @ {speed} baud...")
        
        # Initialize IMU device with optimized settings
        self.imu = sensor_device.SensorDevice(port=port, speed=speed)

        # Optimize serial port for real-time operation (if possible)
        # Note: SensorDevice encapsulates the serial connection internally
        # We can't directly access serial port settings from here
        
        # Get device info
        print(f"\nDevice Information:")
        print(f"  Product ID:  {self.imu.info.get('prod_id')}")
        print(f"  Version:     {self.imu.info.get('version_id')}")
        print(f"  Serial:      {self.imu.info.get('serial_id')}")
        
        # NOTE: IMU should already be configured with imu_configuration_v2.py
        # We only read the existing configuration, not reconfigure
        print(f"\nReading IMU configuration...")
        print(f"  (IMU should be pre-configured with AUTO_START and UART_AUTO)")
        
        # Read current burst configuration to know data format
        # This doesn't change settings, just reads what's already there
        self.imu.sensor_fn._get_burst_config(verbose=False)
        
        # Get initial heading from user
        while True:
            try:
                initial_heading = float(input("\nEnter initial heading (0-360 degrees): "))
                if 0 <= initial_heading <= 360:
                    break
                else:
                    print("Heading must be between 0-360 degrees!")
            except ValueError:
                print("Please enter a valid number!")
        
        # Initialize orientation tracking variables
        self.yaw = initial_heading
        self.yaw_offset = 0
        self.initial_heading = initial_heading
        
        # ========================================================================
        # YAZILIM FİLTRELEME AYARLARI
        # ========================================================================
        # Bu filtreler IMU'dan gelen veriye EK olarak uygulanır
        # IMU'daki donanım filtresi (k128_fc50) ile birlikte çalışır
        # ========================================================================
        
        # ------------------------------------------------------------------------
        # EXPONENTIAL MOVING AVERAGE (EMA) FİLTRESİ
        # ------------------------------------------------------------------------
        # Formül: filtered_value = (1-alpha) * old_value + alpha * new_value
        # 
        # ALPHA değeri (0.0 - 1.0):
        #   - Düşük alpha (0.01-0.05): Çok yavaş değişim, maksimum stabilite
        #   - Orta alpha (0.05-0.15):  Dengeli, orta hız
        #   - Yüksek alpha (0.15-0.5): Hızlı değişim, daha az filtreleme
        # 
        # Öneriler:
        #   - Deniz/stabil:     0.02-0.05 (çok pürüzsüz)
        #   - Genel kullanım:   0.05-0.10 (dengeli)
        #   - Hızlı hareket:    0.10-0.20 (hızlı tepki)
        # ------------------------------------------------------------------------
        self.alpha = 0.15  # ⭐ ŞU AN: 0.03 (yavaş, display için ultra smooth)
        
        # NEDEN 0.03?
        # - Display bar grafiği için ultra pürüzsüz hareket
        # - 75.13-75.14 arası git-gel YOK
        # - Deniz dalgalarını hala takip eder
        # - Kullanıcı gözü yorulmaz
        
        # DİĞER ALPHA SEÇENEKLERİ:
        # self.alpha = 0.02   # Çok yavaş (ultra stabil, yavaş bar hareketi)
        # self.alpha = 0.03   # Yavaş (maksimum stabilite)
        # self.alpha = 0.04   # Orta-yavaş (çok stabil)
        # self.alpha = 0.08   # Orta-hızlı (daha responsive)
        # self.alpha = 0.10   # Hızlı (standart)
        
        # ------------------------------------------------------------------------
        # GYRO THRESHOLD (Gürültü Eşiği)
        # ------------------------------------------------------------------------
        # Bu değerden küçük gyro hareketleri sıfır kabul edilir
        # Drift (kayma) ve küçük titreşimleri önler
        # 
        # Birim: derece/saniye (°/s)
        # 
        # Öneriler:
        #   - Hassas uygulamalar:  0.05-0.10 °/s (her şeyi algıla)
        #   - Genel kullanım:      0.10-0.20 °/s (dengeli)
        #   - Stabil/deniz:        0.20-0.50 °/s (küçük hareketleri yok say)
        # ------------------------------------------------------------------------
        self.gyro_threshold = 0.25  # ⭐ ŞU AN: 0.25°/s (yüksek, küçük titreşimleri bastır)
        
        # NEDEN 0.25?
        # - Düz zeminde tamamen sabit
        # - Küçük motor titreşimleri algılanmaz
        # - Gerçek gemi hareketlerini hala yakalar
        # - Display'de 0.01° git-gel yok
        
        # DİĞER THRESHOLD SEÇENEKLERİ:
        # self.gyro_threshold = 0.1   # Düşük (daha hassas, küçük hareketler)
        # self.gyro_threshold = 0.15  # Orta-düşük (dengeli)
        # self.gyro_threshold = 0.25  # Orta-yüksek (daha stabil)
        # self.gyro_threshold = 0.3   # Yüksek (çok stabil)
        # self.gyro_threshold = 0.5   # Çok yüksek (ultra stabil)
        
        # ------------------------------------------------------------------------
        # FİLTRE DEĞİŞKENLERİ (Tüm eksenler için)
        # ------------------------------------------------------------------------
        self.filtered_gx = 0  # Gyro X ekseni (roll hızı)
        self.filtered_gy = 0  # Gyro Y ekseni (pitch hızı)
        self.filtered_gz = 0  # Gyro Z ekseni (yaw/heading hızı)
        self.filtered_ax = 0  # Accel X ekseni (ileri-geri)
        self.filtered_ay = 0  # Accel Y ekseni (sağa-sola)
        self.filtered_az = 0  # Accel Z ekseni (yukarı-aşağı)
        
        # Roll period calculation
        self.roll_peaks = deque(maxlen=4)
        self.last_roll = 0
        self.roll_period = 0
        
        # Roll amplitude tracking
        self.max_roll_port = 0
        self.max_roll_stbd = 0
        self.roll_amp_port = 0
        self.roll_amp_stbd = 0
        
        # Max acceleration tracking
        self.max_acc = {
            'surge': {'fwd': 0, 'aft': 0},
            'sway': {'port': 0, 'stbd': 0},
            'heave': {'up': 0, 'down': 0}
        }
        
        print(f"\nReady to monitor!")
        print(f"Starting data acquisition... (Press CTRL+C to stop)")
        print(f"\nNote: Using FILTERED version with buffer clearing")
        print(f"      Alpha: {self.alpha}, Gyro Threshold: {self.gyro_threshold}°/s")
        print(f"      To change hardware configuration, run imu_configuration_v2.py")
        print(f"\n{'='*80}\n")
        
    def calculate_roll_period(self, roll, timestamp):
        """Calculate roll period from roll angle peaks"""
        MIN_ROLL_AMPLITUDE = 0.5
        if abs(roll) < MIN_ROLL_AMPLITUDE:
            return
        
        if len(self.roll_peaks) > 0:
            if (roll > self.last_roll and self.roll_peaks[-1][1] < -MIN_ROLL_AMPLITUDE) or \
               (roll < self.last_roll and self.roll_peaks[-1][1] > MIN_ROLL_AMPLITUDE):
                
                MIN_TIME_BETWEEN_PEAKS = 0.1
                if timestamp - self.roll_peaks[-1][0] >= MIN_TIME_BETWEEN_PEAKS:
                    self.roll_peaks.append((timestamp, roll))
                    
                    if len(self.roll_peaks) >= 2:
                        time_diff = self.roll_peaks[-1][0] - self.roll_peaks[-2][0]
                        if 0.1 <= time_diff * 2 <= 60.0:
                            self.roll_period = time_diff * 2
                        
                        while len(self.roll_peaks) > 2:
                            self.roll_peaks.popleft()
        else:
            self.roll_peaks.append((timestamp, roll))
        
        self.last_roll = roll
        
        if len(self.roll_peaks) > 0:
            MAX_PERIOD_AGE = 5.0
            if timestamp - self.roll_peaks[0][0] > MAX_PERIOD_AGE:
                self.roll_period = 0.0
    
    def update_roll_amplitude(self, roll):
        """Update roll amplitude tracking"""
        roll = max(min(roll, 90), -90)
        if roll < 0:
            self.max_roll_port = min(roll, self.max_roll_port)
            self.roll_amp_port = min(abs(self.max_roll_port), 90)
        else:
            self.max_roll_stbd = max(roll, self.max_roll_stbd)
            self.roll_amp_stbd = min(abs(self.max_roll_stbd), 90)
        
        if abs(roll) < 1:
            self.max_roll_port = 0
            self.max_roll_stbd = 0
    
    def calculate_orientation(self, ax, ay, az, gx, gy, gz, dt):
        """Calculate roll, pitch, heading from IMU data"""
        # Apply low-pass filter to all gyro axes
        self.filtered_gx = (1 - self.alpha) * self.filtered_gx + self.alpha * gx
        self.filtered_gy = (1 - self.alpha) * self.filtered_gy + self.alpha * gy
        self.filtered_gz = (1 - self.alpha) * self.filtered_gz + self.alpha * gz
        
        # Apply threshold to gyro (remove small noise)
        if abs(self.filtered_gx) < self.gyro_threshold:
            self.filtered_gx = 0
        if abs(self.filtered_gy) < self.gyro_threshold:
            self.filtered_gy = 0
        if abs(self.filtered_gz) < self.gyro_threshold:
            self.filtered_gz = 0
        
        # Apply low-pass filter to accelerometer
        self.filtered_ax = (1 - self.alpha) * self.filtered_ax + self.alpha * ax
        self.filtered_ay = (1 - self.alpha) * self.filtered_ay + self.alpha * ay
        self.filtered_az = (1 - self.alpha) * self.filtered_az + self.alpha * az
        
        # Normalize filtered accelerometer
        acc_magnitude = math.sqrt(
            self.filtered_ax * self.filtered_ax + 
            self.filtered_ay * self.filtered_ay + 
            self.filtered_az * self.filtered_az
        )
        if acc_magnitude != 0:
            ax_norm = self.filtered_ax / acc_magnitude
            ay_norm = self.filtered_ay / acc_magnitude
            az_norm = self.filtered_az / acc_magnitude
        else:
            ax_norm, ay_norm, az_norm = 0, 0, 1
        
        # Calculate roll and pitch from filtered accelerometer
        roll = math.atan2(-ay_norm, -az_norm)
        pitch = math.atan2(-ax_norm, math.sqrt(ay_norm*ay_norm + az_norm*az_norm))
        
        # Integrate filtered gyro for yaw
        self.yaw += self.filtered_gz * dt
        
        # Convert to degrees
        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        heading = (self.yaw - self.yaw_offset) % 360
        
        # Clamp roll
        roll_deg = max(min(roll_deg, 90), -90)
        
        return roll_deg, pitch_deg, heading
    
    def calculate_acceleration(self, ax, ay, az):
        """Calculate surge, sway, heave accelerations"""
        # Normalize accelerometer
        acc_magnitude = math.sqrt(ax * ax + ay * ay + az * az)
        if acc_magnitude != 0:
            ax = ax / acc_magnitude
            ay = ay / acc_magnitude
            az = az / acc_magnitude
        
        # Heave, Surge, Sway in g
        surge = ax  # Forward-backward motion
        sway = ay   # Left-right motion
        heave = az  # Up-down motion
        
        # Threshold for stillness
        epsilon = 0.05
        if abs(surge) < epsilon and abs(sway) < epsilon and abs(heave) < epsilon:
            surge, sway, heave = 0.0, 0.0, 0.0
        
        # Update max accelerations
        self.max_acc['surge']['fwd'] = max(self.max_acc['surge']['fwd'], surge)
        self.max_acc['surge']['aft'] = min(self.max_acc['surge']['aft'], surge)
        self.max_acc['sway']['port'] = min(self.max_acc['sway']['port'], sway)
        self.max_acc['sway']['stbd'] = max(self.max_acc['sway']['stbd'], sway)
        self.max_acc['heave']['up'] = max(self.max_acc['heave']['up'], heave)
        self.max_acc['heave']['down'] = min(self.max_acc['heave']['down'], heave)
        
        return surge, sway, heave
    
    def run(self):
        """Main loop to read and display IMU data"""
        try:
            # Put IMU in sampling mode
            self.imu.goto('sampling')

            # Note: We can't directly clear buffer with SensorDevice
            # We'll discard old data in the main loop instead

            last_time = time.time()
            start_time = time.time()
            display_counter = 0

            # ====================================================================
            # GERÇEK ZAMANLI VERİ OKUMA - Buffer temizleme ve hızlı okuma
            # ====================================================================
            # Serial buffer sürekli temizlenir, sadece en son veri kullanılır
            # ====================================================================

            while True:
                # AGGRESSIVE BUFFER CLEARING - Always get the LATEST data
                # Read all available data but use only the last one
                latest_data = None
                data_count = 0

                # Read all pending data - max 10 samples to avoid infinite loop
                for _ in range(10):
                    data = self.imu.read_sample()
                    if data:
                        latest_data = data
                        data_count += 1
                    else:
                        break  # No more data available

                # Use only the latest data (discard old buffered data)
                # If no new data, just continue
                data = latest_data if latest_data else self.imu.read_sample()
                if data:
                    current_time = time.time()
                    dt = current_time - last_time
                    timestamp = current_time - start_time
                    display_counter += 1

                    # Extract gyro and accelerometer data
                    # burst_fields: ('tempc32', 'gyro32_X', 'gyro32_Y', 'gyro32_Z',
                    #                'accl32_X', 'accl32_Y', 'accl32_Z')
                    if len(data) >= 7:
                        tempc = data[0]
                        gx, gy, gz = data[1:4]  # deg/s
                        ax, ay, az = data[4:7]  # mG (milliG)

                        # Convert mG to G
                        ax = ax / 1000.0
                        ay = ay / 1000.0
                        az = az / 1000.0

                        # Calculate orientation
                        roll, pitch, heading = self.calculate_orientation(ax, ay, az, gx, gy, gz, dt)

                        # Calculate accelerations
                        surge, sway, heave = self.calculate_acceleration(ax, ay, az)

                        # Update roll period and amplitude
                        self.calculate_roll_period(roll, timestamp)
                        self.update_roll_amplitude(roll)

                        # Display latest data immediately - no delay
                        # Show buffer info for debugging lag
                        print(f"\r[BUF {data_count:2d}] Heading: {heading:6.2f}° | "
                              f"Heel: {roll:6.2f}° | "
                              f"Pitch: {pitch:6.2f}° | "
                              f"Roll Period: {self.roll_period:4.1f}s | "
                              f"Roll Amp P/S: {self.roll_amp_port:5.2f}°/{self.roll_amp_stbd:5.2f}° | "
                              f"Surge: {surge:5.2f} | Sway: {sway:5.2f} | Heave: {heave:5.2f} | "
                              f"Temp: {tempc:5.1f}°C",
                              end='', flush=True)

                    last_time = current_time
                
        except KeyboardInterrupt:
            print("\n\nStopping IMU monitor...")
            self.imu.goto('config')
            print("\nSession Summary:")
            print(f"  Duration: {time.time() - start_time:.1f} seconds")
            print(f"  Max Roll Port: {self.roll_amp_port:.2f}°")
            print(f"  Max Roll Stbd: {self.roll_amp_stbd:.2f}°")
            print(f"\nIMU monitor stopped.")
        except Exception as e:
            print(f"\n\nError: {e}")
            self.imu.goto('config')


if __name__ == "__main__":
    # Configuration parameters
    PORT = '/dev/ttyLP2'      # Change to your COM port (e.g., 'COM8', '/dev/ttyUSB0')
    BAUDRATE = 460800  # Baudrate (should match IMU configuration)
    
    print("\n" + "="*80)
    print("  IMU Orientation Monitor - Epson G366-PDG0")
    print("="*80)
    print(f"\nPort: {PORT}")
    print(f"Baudrate: {BAUDRATE}")
    print("\nTo change port/baudrate, edit imu_orientation_v2.py")
    print("="*80 + "\n")
    
    try:
        # Create and run monitor
        monitor = IMUMonitor(port=PORT, speed=BAUDRATE)
        monitor.run()
        
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if IMU is connected to the correct port")
        print("  2. Verify no other program is using the port")
        print("  3. Make sure esensorlib is installed:")
        print("     cd py_esensorlib")
        print("     pip install -e .")
        print("  4. If IMU is configured with AUTO_START, it may already be in SAMPLING mode")
        print("     Try power cycling the IMU")
        import traceback
        traceback.print_exc()
        sys.exit(1)