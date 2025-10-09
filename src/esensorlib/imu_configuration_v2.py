#!/usr/bin/env python

# MIT License

# Copyright (c) 2023, 2025 Seiko Epson Corporation

"""
IMU Configuration Script for Epson G366-PDG0
Configures the IMU with AUTO_START and UART_AUTO modes
Saves settings to flash memory for persistent configuration

================================================================================
HIZLI AYAR REHBERİ
================================================================================

Bu dosyada değiştirebileceğin 2 ana parametre var (Satır ~119 ve ~179):

1. OUTPUT_RATE:
   - IMU çıkış hızı (Hz)
   - Seçenekler: 2000, 1000, 500, 400, 250, 200, 125, 100, 80, 50, 40, 25, 20
   - Önerilen: 100-200 Hz (deniz), 500-1000 Hz (drone)
   - ⭐ ŞU AN: 100 Hz

2. FILTER_SEL:
   - Donanım filtresi (IMU içinde)
   - Moving Average: 'mv_avg0' - 'mv_avg128'
   - Kaiser: 'k32_fc50' - 'k128_fc50'
   - Önerilen: 'k128_fc50' (deniz), 'mv_avg16' (genel)
   - ⭐ ŞU AN: 'k128_fc50'

KULLANIM:
1. Bu dosyayı düzenle (OUTPUT_RATE ve FILTER_SEL)
2. Çalıştır: python imu_configuration_v2.py
3. Seçenek 1'i seç (Flash'a kaydet)
4. Artık ayarlar kalıcı!

NOT: Bu ayarlar flash'a kaydedilir ve güç kesilse bile kalır.
     Orientation dosyasındaki ayarlar ise geçicidir (her çalıştırmada).

================================================================================
"""

import sys
import time

from esensorlib import sensor_device


class IMUConfigurator:
    def __init__(self, port='COM8', speed=460800):
        """
        Initialize IMU Configurator
        
        Parameters
        ----------
        port : str
            Serial port name (e.g., 'COM8' on Windows, '/dev/ttyUSB0' on Linux)
        speed : int
            Baudrate (default: 460800)
        """
        self.port = port
        self.speed = speed
        self.imu = None
        
    def print_header(self):
        """Print configuration header"""
        print(f"\n{'='*80}")
        print(f"  Epson IMU G366-PDG0 Configuration Tool")
        print(f"{'='*80}")
        print(f"\nThis tool will configure your IMU with the following settings:")
        print(f"  - AUTO_START: Enabled (IMU starts automatically on power-up)")
        print(f"  - UART_AUTO: Enabled (Continuous data streaming)")
        print(f"  - Baudrate: 460800")
        print(f"  - Output Rate: 200 Hz")
        print(f"  - Filter: Moving Average (16 samples)")
        print(f"  - Data Format: 32-bit")
        print(f"  - Temperature: Enabled")
        print(f"  - Accelerometer Range: 8G")
        print(f"\nSettings will be saved to FLASH memory (persistent).")
        print(f"{'='*80}\n")
        
    def connect(self):
        """Connect to IMU"""
        print(f"Connecting to IMU on {self.port} @ {self.speed} baud...")
        try:
            self.imu = sensor_device.SensorDevice(
                port=self.port, 
                speed=self.speed,
                verbose=False
            )
            print(f"✓ Connected successfully!\n")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def display_device_info(self):
        """Display device information"""
        print(f"Device Information:")
        print(f"  Product ID:  {self.imu.info.get('prod_id')}")
        print(f"  Version:     {self.imu.info.get('version_id')}")
        print(f"  Serial:      {self.imu.info.get('serial_id')}")
        print()
    
    def perform_checks(self):
        """Perform initial hardware checks"""
        print("Performing hardware checks...")
        try:
            # Check for hardware errors
            self.imu.init_check(verbose=False)
            print("✓ Hardware check passed")
            
            # Perform self-test
            print("Running self-test (this may take a few seconds)...")
            self.imu.do_selftest(verbose=False)
            print("✓ Self-test passed")
            
            # Perform flash test
            print("Testing flash memory...")
            self.imu.do_flashtest(verbose=False)
            print("✓ Flash test passed\n")
            
            return True
        except Exception as e:
            print(f"✗ Check failed: {e}")
            return False
    
    def configure_device(self):
        """Configure IMU with desired settings"""
        print("Configuring IMU...")
        
        # ============================================================================
        # IMU CONFIGURATION - Detaylı Ayarlar ve Seçenekler
        # ============================================================================
        
        # ----------------------------------------------------------------------------
        # OUTPUT RATE (Çıkış Hızı) - Saniyede kaç örnek alınacak
        # ----------------------------------------------------------------------------
        # Seçenekler: 2000, 1000, 500, 400, 250, 200, 125, 100, 80, 50, 40, 25, 20, 15.625
        # 
        # Öneriler:
        #   - Hızlı hareket/drone/robot: 500-2000 Hz (hızlı tepki, daha fazla gürültü)
        #   - Genel kullanım/deniz:      100-200 Hz  (dengeli, önerilen)
        #   - Yavaş hareket/stabilite:   25-50 Hz    (çok stabil, yavaş tepki)
        # 
        # Trade-off: Yüksek Hz = Hızlı tepki ama daha fazla gürültü
        #            Düşük Hz  = Daha stabil ama yavaş tepki
        # ----------------------------------------------------------------------------
        OUTPUT_RATE = 100  # ⭐ ŞU AN: 100 Hz (deniz için ideal)
        
        # ----------------------------------------------------------------------------
        # FILTER SELECTION (Filtre Seçimi) - Gürültü azaltma
        # ----------------------------------------------------------------------------
        # 
        # 1) MOVING AVERAGE FİLTRELERİ (Basit, Hızlı):
        #    'mv_avg0'   - Filtresiz (ham veri, maksimum gürültü)
        #    'mv_avg2'   - 2 örnek ortalaması (çok hafif)
        #    'mv_avg4'   - 4 örnek ortalaması (hafif)
        #    'mv_avg8'   - 8 örnek ortalaması (orta-hafif)
        #    'mv_avg16'  - 16 örnek ortalaması (orta) ⭐ STANDART
        #    'mv_avg32'  - 32 örnek ortalaması (güçlü)
        #    'mv_avg64'  - 64 örnek ortalaması (çok güçlü)
        #    'mv_avg128' - 128 örnek ortalaması (maksimum)
        # 
        # 2) KAISER FİLTRELERİ (Profesyonel, Keskin Kesim):
        #    K32 (32-tap):
        #      'k32_fc50', 'k32_fc100', 'k32_fc200', 'k32_fc400'
        #    K64 (64-tap):
        #      'k64_fc50', 'k64_fc100', 'k64_fc200', 'k64_fc400'
        #    K128 (128-tap): ⭐ EN GÜÇLÜ
        #      'k128_fc50', 'k128_fc100', 'k128_fc200', 'k128_fc400'
        # 
        # KULLANIM SENARYOLARI:
        # 
        # A) Deniz/Yat Uygulaması (Senin Durumun):
        #    - Önerilen: 'k128_fc50' veya 'mv_avg64'
        #    - Neden: Deniz dalgaları düşük frekanslı (0.1-1 Hz)
        #             Motor/rüzgar gürültüsü yüksek frekanslı (10-100 Hz)
        #    - Gecikme: ~640ms (k128) veya ~320ms (mv_avg64) - deniz için OK
        # 
        # B) Drone/Robot (Hızlı Hareket):
        #    - Önerilen: 'mv_avg4' veya 'k32_fc200'
        #    - Neden: Hızlı tepki gerekli
        #    - Gecikme: ~8ms (mv_avg4) veya ~80ms (k32_fc200)
        # 
        # C) Genel Amaçlı:
        #    - Önerilen: 'mv_avg16' veya 'k64_fc100'
        #    - Neden: Dengeli performans
        #    - Gecikme: ~80ms (mv_avg16) veya ~320ms (k64_fc100)
        # 
        # D) Maksimum Stabilite (Yavaş Hareket):
        #    - Önerilen: 'k128_fc50' veya 'mv_avg128'
        #    - Neden: En güçlü filtreleme
        #    - Gecikme: ~640ms (k128) veya ~640ms (mv_avg128)
        # 
        # GECIKME HESAPLAMA:
        #   Moving Average: (Örnek Sayısı / 2) / Output Rate
        #   Kaiser:         (Tap Sayısı / 2) / Output Rate
        # 
        #   Örnek (k128_fc50 @ 100Hz): (128/2)/100 = 0.64 saniye = 640ms
        #   Örnek (mv_avg64 @ 100Hz):  (64/2)/100  = 0.32 saniye = 320ms
        # 
        # FİLTRE GÜCÜ TABLOSU (Düşükten Yükseğe):
        #   mv_avg0 < mv_avg2 < mv_avg4 < mv_avg8 < mv_avg16 < mv_avg32 < mv_avg64 < mv_avg128
        #   k32_fc400 < k32_fc200 < k32_fc100 < k32_fc50
        #   k64_fc400 < k64_fc200 < k64_fc100 < k64_fc50
        #   k128_fc400 < k128_fc200 < k128_fc100 < k128_fc50 ⭐ EN GÜÇLÜ
        # ----------------------------------------------------------------------------
        FILTER_SEL = 'k128_fc50'  # ⭐ ŞU AN: Kaiser 128-tap, 50Hz kesim (maksimum stabilite)
        
        # DİĞER POPÜLER SEÇİMLER (İstersen değiştirebilirsin):
        # FILTER_SEL = 'mv_avg64'    # Güçlü ama daha hızlı (320ms gecikme)
        # FILTER_SEL = 'k64_fc50'    # Orta güç, orta hız (320ms gecikme)
        # FILTER_SEL = 'mv_avg32'    # Dengeli (160ms gecikme)
        # FILTER_SEL = 'k128_fc100'  # Biraz daha hızlı tepki (640ms gecikme)
        
        # ----------------------------------------------------------------------------
        # DİĞER AYARLAR (Genelde değiştirmeye gerek yok)
        # ----------------------------------------------------------------------------
        
        # Configuration dictionary
        device_cfg = {
            'dout_rate': OUTPUT_RATE,   # Yukarıda tanımlandı
            'filter_sel': FILTER_SEL,   # Yukarıda tanımlandı
            'ndflags': False,            # ND/EA flags (hata bayrakları) - genelde kapalı
            'tempc': True,               # Sıcaklık verisi - açık tut (yararlı)
            'counter': '',               # Sayaç - kapalı
            'chksm': False,              # Checksum (veri doğrulama) - kapalı (hız için)
            'uart_auto': True,           # UART AUTO mode - açık (sürekli veri akışı)
            'auto_start': True,          # AUTO START - açık (açılışta otomatik başla)
            'is_32bit': True,            # 32-bit veri - açık (daha hassas)
            'a_range': False,            # İvmeölçer aralığı: False=8G, True=16G
            'ext_trigger': False,        # Harici tetikleme - kapalı
            'verbose': False             # Debug mesajları - kapalı
        }
        
        try:
            # Apply configuration
            self.imu.set_config(**device_cfg)
            print("✓ Configuration applied successfully\n")
            
            # Display configuration summary
            print("Configuration Summary:")
            print(f"  Output Rate:        {device_cfg['dout_rate']} Hz")
            print(f"  Filter:             {device_cfg['filter_sel']}")
            print(f"  Data Format:        {'32-bit' if device_cfg['is_32bit'] else '16-bit'}")
            print(f"  Temperature:        {'Enabled' if device_cfg['tempc'] else 'Disabled'}")
            print(f"  Accel Range:        {'16G' if device_cfg['a_range'] else '8G'}")
            print(f"  UART AUTO:          {'Enabled' if device_cfg['uart_auto'] else 'Disabled'}")
            print(f"  AUTO START:         {'Enabled' if device_cfg['auto_start'] else 'Disabled'}")
            print()
            
            return True
        except Exception as e:
            print(f"✗ Configuration failed: {e}")
            return False
    
    def save_to_flash(self):
        """Save configuration to flash memory"""
        print("Saving configuration to FLASH memory...")
        print("WARNING: This will make the configuration persistent!")
        print("The IMU will automatically start with these settings on power-up.\n")
        
        # Ask for confirmation
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Flash backup cancelled.")
            return False
        
        try:
            # Backup configuration to flash
            print("\nWriting to flash memory (this may take a moment)...")
            self.imu.backup_flash(verbose=False)
            print("✓ Configuration saved to flash successfully!\n")
            return True
        except Exception as e:
            print(f"✗ Flash backup failed: {e}")
            return False
    
    def verify_configuration(self):
        """Verify the configuration by reading registers"""
        print("Verifying configuration...")
        try:
            # Check MODE_CTRL for AUTO_START
            mode_ctrl = self.imu.get_reg(
                self.imu.mdef.Reg.MODE_CTRL.WINID,
                self.imu.mdef.Reg.MODE_CTRL.ADDR
            )
            
            # Check UART_CTRL for UART_AUTO
            uart_ctrl = self.imu.get_reg(
                self.imu.mdef.Reg.UART_CTRL.WINID,
                self.imu.mdef.Reg.UART_CTRL.ADDR
            )
            
            # Check SMPL_CTRL for output rate
            smpl_ctrl = self.imu.get_reg(
                self.imu.mdef.Reg.SMPL_CTRL.WINID,
                self.imu.mdef.Reg.SMPL_CTRL.ADDR
            )
            
            print(f"  MODE_CTRL:  0x{mode_ctrl:04X}")
            print(f"  UART_CTRL:  0x{uart_ctrl:04X}")
            print(f"  SMPL_CTRL:  0x{smpl_ctrl:04X}")
            
            # Verify AUTO_START bit (bit 1 in UART_CTRL low byte)
            auto_start_enabled = (uart_ctrl & 0x02) != 0
            # Verify UART_AUTO bit (bit 0 in UART_CTRL low byte)
            uart_auto_enabled = (uart_ctrl & 0x01) != 0
            
            print(f"\n  AUTO_START: {'✓ Enabled' if auto_start_enabled else '✗ Disabled'}")
            print(f"  UART_AUTO:  {'✓ Enabled' if uart_auto_enabled else '✗ Disabled'}")
            
            if auto_start_enabled and uart_auto_enabled:
                print("\n✓ Configuration verified successfully!\n")
                return True
            else:
                print("\n✗ Configuration verification failed!")
                return False
                
        except Exception as e:
            print(f"✗ Verification failed: {e}")
            return False
    
    def test_sampling(self):
        """Test sampling mode briefly"""
        print("Testing sampling mode...")
        try:
            self.imu.goto('sampling')
            print("Reading 10 samples...")
            
            for i in range(10):
                data = self.imu.read_sample()
                if data and len(data) >= 7:
                    tempc = data[0]
                    gx, gy, gz = data[1:4]
                    ax, ay, az = data[4:7]
                    print(f"  Sample {i+1}: Temp={tempc:.1f}°C, "
                          f"Gyro=({gx:.2f}, {gy:.2f}, {gz:.2f}), "
                          f"Accel=({ax:.2f}, {ay:.2f}, {az:.2f})")
                time.sleep(0.05)
            
            self.imu.goto('config')
            print("✓ Sampling test successful!\n")
            return True
        except Exception as e:
            print(f"✗ Sampling test failed: {e}")
            self.imu.goto('config')
            return False
    
    def restore_defaults(self):
        """Restore factory default settings"""
        print("\nRestoring factory default settings...")
        response = input("Are you sure? This will erase all custom settings. (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Restore cancelled.")
            return False
        
        try:
            self.imu.init_backup(verbose=False)
            print("✓ Factory defaults restored!\n")
            return True
        except Exception as e:
            print(f"✗ Restore failed: {e}")
            return False
    
    def run(self):
        """Main configuration workflow"""
        self.print_header()
        
        # Connect to device
        if not self.connect():
            return False
        
        # Display device info
        self.display_device_info()
        
        # Show menu
        print("Configuration Options:")
        print("  1. Configure and save to flash (recommended)")
        print("  2. Configure only (temporary, not saved)")
        print("  3. Restore factory defaults")
        print("  4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        print()
        
        if choice == '1':
            # Full configuration with flash backup
            if not self.perform_checks():
                print("\nHardware checks failed. Cannot continue.")
                return False
            
            if not self.configure_device():
                print("\nConfiguration failed. Cannot continue.")
                return False
            
            if not self.save_to_flash():
                print("\nFlash backup cancelled or failed.")
                return False
            
            if not self.verify_configuration():
                print("\nConfiguration verification failed.")
                return False
            
            if not self.test_sampling():
                print("\nSampling test failed.")
                return False
            
            print("="*80)
            print("  Configuration Complete!")
            print("="*80)
            print("\nYour IMU is now configured with AUTO_START and UART_AUTO modes.")
            print("The IMU will automatically start streaming data on power-up.")
            print("\nNext steps:")
            print("  1. Power cycle the IMU to test AUTO_START")
            print("  2. Run imu_orientation_v2.py to monitor real-time data")
            print("\nNote: The IMU will start in SAMPLING mode automatically.")
            print("      Use imu.goto('config') if you need to reconfigure.")
            print("="*80 + "\n")
            
        elif choice == '2':
            # Configuration without flash backup
            if not self.configure_device():
                print("\nConfiguration failed.")
                return False
            
            if not self.test_sampling():
                print("\nSampling test failed.")
                return False
            
            print("Configuration applied (temporary - not saved to flash).")
            print("Settings will be lost on power cycle.\n")
            
        elif choice == '3':
            # Restore defaults
            self.restore_defaults()
            
        elif choice == '4':
            print("Exiting without changes.\n")
            return True
        
        else:
            print("Invalid option. Exiting.\n")
            return False
        
        return True


if __name__ == "__main__":
    # Configuration parameters
    PORT = 'COM8'       # Change to your COM port
    BAUDRATE = 460800   # Baudrate (460800 is standard for G366-PDG0)
    
    print("\nIMU Configuration Tool")
    print(f"Port: {PORT}, Baudrate: {BAUDRATE}")
    print("\nTo change port/baudrate, edit imu_configuration_v2.py\n")
    
    try:
        configurator = IMUConfigurator(port=PORT, speed=BAUDRATE)
        success = configurator.run()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nConfiguration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

