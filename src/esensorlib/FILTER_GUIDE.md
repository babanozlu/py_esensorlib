# IMU Filtreleme Rehberi

Bu rehber, IMU filtreleme ayarlarını nasıl değiştireceğini detaylıca açıklar.

## 📁 Hangi Dosyayı Düzenleyeceğim?

### 1. **`imu_configuration_v2.py`** - Donanım Filtresi (Kalıcı)
- **Ne zaman**: Yeni sensör yapılandırırken veya filtre değiştirirken
- **Nerede**: Satır ~119 (OUTPUT_RATE) ve ~179 (FILTER_SEL)
- **Kalıcılık**: Flash'a kaydedilir, güç kesilse bile kalır
- **Değişiklik sıklığı**: Nadiren (sensör başına bir kez)

### 2. **`imu_orientation_v2.py`** - Yazılım Filtresi (Geçici)
- **Ne zaman**: Ekran görünümünü ince ayar yaparken
- **Nerede**: 
  - Satır ~90 (ALPHA)
  - Satır ~111 (GYRO_THRESHOLD)
  - Satır ~303 (DISPLAY_INTERVAL)
- **Kalıcılık**: Geçici, her çalıştırmada uygulanır
- **Değişiklik sıklığı**: Sık (test ederken)

---

## 🎯 Hızlı Seçim Tablosu

| Kullanım Senaryosu | OUTPUT_RATE | FILTER_SEL | ALPHA | THRESHOLD | DISPLAY |
|---------------------|-------------|------------|-------|-----------|---------|
| **Deniz/Yat** ⭐ | 100 Hz | k128_fc50 | 0.03 | 0.3 | 0.1s |
| **Genel Amaçlı** | 200 Hz | mv_avg16 | 0.10 | 0.2 | 0.1s |
| **Drone/Robot** | 500 Hz | mv_avg4 | 0.15 | 0.1 | 0.05s |
| **Maksimum Stabilite** | 50 Hz | k128_fc50 | 0.02 | 0.5 | 0.2s |
| **Hızlı Tepki** | 1000 Hz | mv_avg2 | 0.20 | 0.1 | 0.05s |

---

## 📊 Parametre Detayları

### 1. OUTPUT_RATE (Donanım - Configuration)

**Ne yapar**: IMU'nun saniyede kaç örnek alacağını belirler.

**Seçenekler**:
```python
2000, 1000, 500, 400, 250, 200, 125, 100, 80, 50, 40, 25, 20, 15.625
```

**Öneriler**:
- **Yüksek (500-2000 Hz)**: Hızlı hareket, drone, robot
  - ✅ Hızlı tepki
  - ⚠️ Daha fazla gürültü
  
- **Orta (100-200 Hz)**: Genel kullanım, deniz ⭐
  - ✅ Dengeli
  - ✅ Önerilen
  
- **Düşük (25-50 Hz)**: Yavaş hareket, maksimum stabilite
  - ✅ Çok stabil
  - ⚠️ Yavaş tepki

**Nasıl değiştiririm**:
```python
# imu_configuration_v2.py - Satır ~119
OUTPUT_RATE = 100  # Buraya istediğin değeri yaz
```

---

### 2. FILTER_SEL (Donanım - Configuration)

**Ne yapar**: IMU içindeki donanım filtresini belirler.

#### **A) Moving Average Filtreleri**
Basit, hızlı, etkili.

```python
'mv_avg0'    # Filtresiz (ham veri)
'mv_avg2'    # Çok hafif
'mv_avg4'    # Hafif
'mv_avg8'    # Orta-hafif
'mv_avg16'   # Orta ⭐ STANDART
'mv_avg32'   # Güçlü
'mv_avg64'   # Çok güçlü
'mv_avg128'  # Maksimum
```

**Gecikme Hesaplama**:
```
Gecikme = (Örnek Sayısı / 2) / Output Rate

Örnek: mv_avg64 @ 100Hz = (64/2)/100 = 0.32s = 320ms
```

#### **B) Kaiser Filtreleri**
Profesyonel, keskin kesim frekansı.

```python
# K32 (32-tap)
'k32_fc50', 'k32_fc100', 'k32_fc200', 'k32_fc400'

# K64 (64-tap)
'k64_fc50', 'k64_fc100', 'k64_fc200', 'k64_fc400'

# K128 (128-tap) ⭐ EN GÜÇLÜ
'k128_fc50', 'k128_fc100', 'k128_fc200', 'k128_fc400'
```

**Kesim Frekansı (fc)**:
- `fc50`: 50 Hz üzeri kesilir (deniz için ideal)
- `fc100`: 100 Hz üzeri kesilir
- `fc200`: 200 Hz üzeri kesilir
- `fc400`: 400 Hz üzeri kesilir

**Gecikme Hesaplama**:
```
Gecikme = (Tap Sayısı / 2) / Output Rate

Örnek: k128_fc50 @ 100Hz = (128/2)/100 = 0.64s = 640ms
```

**Öneriler**:
- **Deniz/Yat**: `k128_fc50` (maksimum stabilite)
- **Genel**: `mv_avg16` (dengeli)
- **Drone**: `mv_avg4` veya `k32_fc200` (hızlı)

**Nasıl değiştiririm**:
```python
# imu_configuration_v2.py - Satır ~179
FILTER_SEL = 'k128_fc50'  # Buraya istediğin filtreyi yaz
```

---

### 3. ALPHA (Yazılım - Orientation)

**Ne yapar**: Yazılım filtresinin hızını belirler (Exponential Moving Average).

**Formül**:
```
filtered = (1-alpha) * old + alpha * new
```

**Değer Aralığı**: 0.0 - 1.0

**Öneriler**:
- **0.01-0.03**: Ultra stabil, çok yavaş (deniz) ⭐
- **0.05-0.10**: Dengeli (genel kullanım)
- **0.10-0.20**: Hızlı tepki (drone/robot)

**Trade-off**:
- Düşük alpha = Daha stabil, daha yavaş
- Yüksek alpha = Daha hızlı, daha gürültülü

**Nasıl değiştiririm**:
```python
# imu_orientation_v2.py - Satır ~90
self.alpha = 0.03  # Buraya istediğin değeri yaz
```

---

### 4. GYRO_THRESHOLD (Yazılım - Orientation)

**Ne yapar**: Bu değerden küçük gyro hareketleri sıfır kabul edilir.

**Birim**: derece/saniye (°/s)

**Öneriler**:
- **0.05-0.10**: Hassas, her şeyi algıla
- **0.10-0.20**: Dengeli (genel) ⭐
- **0.20-0.50**: Stabil, küçük titreşimleri yok say (deniz)

**Etki**:
- Düşük = Daha hassas, drift olabilir
- Yüksek = Daha stabil, küçük hareketleri görmez

**Nasıl değiştiririm**:
```python
# imu_orientation_v2.py - Satır ~111
self.gyro_threshold = 0.3  # Buraya istediğin değeri yaz
```

---

### 5. DISPLAY_INTERVAL (Yazılım - Orientation)

**Ne yapar**: Ekranın ne sıklıkla güncelleneceğini belirler.

**Birim**: saniye

**Öneriler**:
- **0.02-0.05s**: Çok hızlı (20-50 Hz) - titreme olabilir
- **0.05-0.10s**: Hızlı (10-20 Hz) - dengeli
- **0.10-0.20s**: Orta (5-10 Hz) - rahat okunur ⭐
- **0.20-0.50s**: Yavaş (2-5 Hz) - çok stabil

**Trade-off**:
- Düşük = Daha güncel ama titrek
- Yüksek = Daha stabil ama gecikmeli

**Nasıl değiştiririm**:
```python
# imu_orientation_v2.py - Satır ~303
display_interval = 0.1  # Buraya istediğin değeri yaz
```

---

## 🔄 Değişiklik Yapma Adımları

### Donanım Filtresi Değiştirme (Kalıcı):

1. `imu_configuration_v2.py` dosyasını aç
2. Satır ~119: `OUTPUT_RATE` değiştir
3. Satır ~179: `FILTER_SEL` değiştir
4. Dosyayı kaydet
5. Çalıştır:
   ```bash
   cd py_esensorlib/src/esensorlib
   python imu_configuration_v2.py
   ```
6. Seçenek **1** seç (Flash'a kaydet)
7. Bitir! Artık kalıcı.

### Yazılım Filtresi Değiştirme (Geçici):

1. `imu_orientation_v2.py` dosyasını aç
2. İstediğin parametreleri değiştir:
   - Satır ~90: `self.alpha`
   - Satır ~111: `self.gyro_threshold`
   - Satır ~303: `display_interval`
3. Dosyayı kaydet
4. Çalıştır:
   ```bash
   cd py_esensorlib/src/esensorlib
   python imu_orientation_v2.py
   ```
5. Test et, beğenmezsen tekrar değiştir!

---

## 💡 Örnek Senaryolar

### Senaryo 1: "Değerler çok titriyor!"

**Çözüm**: Filtrelemeyi güçlendir

```python
# imu_configuration_v2.py
OUTPUT_RATE = 100
FILTER_SEL = 'k128_fc50'  # Daha güçlü filtre

# imu_orientation_v2.py
self.alpha = 0.02          # Daha yavaş
self.gyro_threshold = 0.5  # Daha yüksek eşik
display_interval = 0.2     # Daha yavaş ekran
```

### Senaryo 2: "Çok yavaş tepki veriyor!"

**Çözüm**: Filtrelemeyi azalt

```python
# imu_configuration_v2.py
OUTPUT_RATE = 500
FILTER_SEL = 'mv_avg8'  # Daha hafif filtre

# imu_orientation_v2.py
self.alpha = 0.15           # Daha hızlı
self.gyro_threshold = 0.1   # Daha düşük eşik
display_interval = 0.05     # Daha hızlı ekran
```

### Senaryo 3: "Heading kayıyor (drift)!"

**Çözüm**: Gyro threshold'u artır

```python
# imu_orientation_v2.py
self.gyro_threshold = 0.5  # Daha yüksek
```

---

## 📈 Filtre Gücü Karşılaştırması

**Zayıftan Güçlüye**:

```
Donanım Filtreleri:
mv_avg0 < mv_avg2 < mv_avg4 < mv_avg8 < mv_avg16 < mv_avg32 < mv_avg64 < mv_avg128

k32_fc400 < k32_fc200 < k32_fc100 < k32_fc50
k64_fc400 < k64_fc200 < k64_fc100 < k64_fc50
k128_fc400 < k128_fc200 < k128_fc100 < k128_fc50 ⭐ EN GÜÇLÜ

Yazılım Filtresi (Alpha):
0.5 < 0.3 < 0.2 < 0.15 < 0.10 < 0.05 < 0.03 < 0.02 < 0.01 ⭐ EN GÜÇLÜ
```

---

## ❓ Sık Sorulan Sorular

**S: Hangi filtre en iyisi?**
C: Uygulamana bağlı. Deniz için `k128_fc50`, genel için `mv_avg16`.

**S: Gecikme sorun olur mu?**
C: Deniz gibi yavaş uygulamalarda 640ms sorun değil. Drone'da sorun olur.

**S: Her iki dosyayı da değiştirmeli miyim?**
C: İdeal olan: Configuration'da donanım filtresi ayarla, Orientation'da ince ayar yap.

**S: Ayarları test ederken ne yapmalıyım?**
C: Önce Orientation'daki yazılım filtrelerini test et (hızlı). Sonra Configuration'da donanım filtresini değiştir (kalıcı).

**S: Fabrika ayarlarına nasıl dönerim?**
C: `imu_configuration_v2.py` çalıştır, Seçenek 3 (Restore factory defaults).

---

## 🎓 Özet

1. **Donanım Filtresi** (Configuration): Güçlü, kalıcı, IMU içinde
2. **Yazılım Filtresi** (Orientation): Ek filtreleme, geçici, Python'da
3. **İkisi birlikte**: Maksimum stabilite için ikisini de kullan
4. **Test et**: Küçük değişiklikler yap, test et, ayarla

Başka soru varsa sor! 🚀

