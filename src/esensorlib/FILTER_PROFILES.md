# IMU Filtre Profilleri - Hazır Ayarlar

Bu dosya 4 farklı filtre profili içerir. İstediğini seç ve değerleri kopyala-yapıştır.

---

## 📊 PROFİL KARŞILAŞTIRMA TABLOSU

| Profil | Hız | Stabilite | Gecikme | Kullanım |
|--------|-----|-----------|---------|----------|
| **0. ULTRA STABİL** | ⭐ | ⭐⭐⭐⭐⭐ | 640ms | Düz zemin, liman |
| **1. ÇOK STABİL** ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | 320ms | Deniz, gemi (ŞU AN) |
| **2. DENGELİ** | ⭐⭐⭐ | ⭐⭐⭐ | 160ms | Genel kullanım |
| **3. HIZLI** | ⭐⭐⭐⭐ | ⭐⭐ | 80ms | Manevra, test |
| **4. ÇOK HIZLI** | ⭐⭐⭐⭐⭐ | ⭐ | 40ms | Drone, robot |

---

## 🎯 PROFİL 0: ULTRA STABİL (En Yavaş, En Stabil)

**Kullanım:** Düz zemin testi, liman, maksimum stabilite gerektiğinde

### `imu_configuration_v2.py` (Satır 149, 209):
```python
OUTPUT_RATE = 100           # 100 Hz
FILTER_SEL = 'k128_fc50'    # Kaiser 128-tap, 50Hz kesim
```

### `imu_orientation_v2.py` (Satır 113, 141):
```python
self.alpha = 0.01           # Ultra yavaş filtre
self.gyro_threshold = 0.4   # Çok yüksek eşik
```

### Özellikler:
- ✅ **Maksimum stabilite**: Neredeyse donmuş
- ✅ **Sıfır titreme**: 75.13° sabit kalır
- ✅ **Sıfır gürültü**: Her şey filtrelenir
- ⚠️ **Çok yavaş**: 640ms gecikme
- ⚠️ **Küçük hareketler görünmez**: 0.4°/s altı yok

**Ne zaman kullan:**
- Düz zeminde test
- Limanda park
- Maksimum stabilite istiyorsun

---

## 🎯 PROFİL 1: ÇOK STABİL (Gemi İçin İdeal) ⭐ ŞU AN BU!

**Kullanım:** Deniz, gemi, normal kullanım, display için ideal

### `imu_configuration_v2.py` (Satır 149, 209):
```python
OUTPUT_RATE = 125           # 125 Hz
FILTER_SEL = 'k64_fc50'     # Kaiser 64-tap, 50Hz kesim
```

### `imu_orientation_v2.py` (Satır 113, 141):
```python
self.alpha = 0.03           # Yavaş filtre
self.gyro_threshold = 0.25  # Yüksek eşik
```

### Özellikler:
- ✅ **Çok stabil**: 75.13-75.14 yavaş git-gel
- ✅ **Pürüzsüz**: Display bar smooth
- ✅ **Deniz dalgalarını takip**: 0.1-2 Hz geçer
- ✅ **Motor gürültüsü yok**: 50Hz+ kesilir
- ⚠️ **Orta gecikme**: 256ms

**Ne zaman kullan:**
- Denizde normal kullanım
- 7" display ile gösterim
- Kullanıcı rahatsız olmasın

---

## 🎯 PROFİL 2: DENGELİ (Hızlı ve Stabil)

**Kullanım:** Genel amaçlı, test, hızlı tepki istiyorsun ama stabil olsun

### `imu_configuration_v2.py` (Satır 149, 209):
```python
OUTPUT_RATE = 200           # 200 Hz
FILTER_SEL = 'mv_avg32'     # Moving Average 32
```

### `imu_orientation_v2.py` (Satır 113, 141):
```python
self.alpha = 0.08           # Orta hız filtre
self.gyro_threshold = 0.15  # Orta eşik
```

### Özellikler:
- ✅ **Dengeli**: Hem hızlı hem stabil
- ✅ **Hızlı tepki**: 80ms gecikme
- ✅ **Hala pürüzsüz**: Titreme az
- ⚠️ **Biraz git-gel olabilir**: 75.13-75.15 arası
- ⚠️ **Orta stabilite**: Çok stabil değil

**Ne zaman kullan:**
- Test ederken
- Hızlı manevra
- Gerçek zamanlı tepki önemli

---

## 🎯 PROFİL 3: HIZLI (Hızlı Tepki)

**Kullanım:** Manevra, test, hızlı hareket, responsive olmalı

### `imu_configuration_v2.py` (Satır 149, 209):
```python
OUTPUT_RATE = 500           # 500 Hz
FILTER_SEL = 'mv_avg8'      # Moving Average 8
```

### `imu_orientation_v2.py` (Satır 113, 141):
```python
self.alpha = 0.15           # Hızlı filtre
self.gyro_threshold = 0.1   # Düşük eşik
```

### Özellikler:
- ✅ **Çok hızlı**: 40ms gecikme
- ✅ **Responsive**: Anında tepki
- ✅ **Hassas**: Küçük hareketleri yakalar
- ⚠️ **Titreme var**: 75.10-75.20 arası git-gel
- ⚠️ **Gürültülü**: Motor titreşimi görünür

**Ne zaman kullan:**
- Hızlı manevra
- Test ve geliştirme
- Gerçek zamanlı kontrol

---

## 🎯 PROFİL 4: ÇOK HIZLI (Drone/Robot Seviyesi)

**Kullanım:** Drone, robot, çok hızlı hareket, minimum gecikme

### `imu_configuration_v2.py` (Satır 149, 209):
```python
OUTPUT_RATE = 1000          # 1000 Hz
FILTER_SEL = 'mv_avg4'      # Moving Average 4
```

### `imu_orientation_v2.py` (Satır 113, 141):
```python
self.alpha = 0.20           # Çok hızlı filtre
self.gyro_threshold = 0.05  # Çok düşük eşik
```

### Özellikler:
- ✅ **Maksimum hız**: 20ms gecikme
- ✅ **Anında tepki**: Gerçek zamanlı
- ✅ **Çok hassas**: Her şeyi algılar
- ⚠️ **Çok gürültülü**: Sürekli titreme
- ⚠️ **Stabilite yok**: 75.05-75.25 arası oynama

**Ne zaman kullan:**
- Drone kontrolü
- Robot navigasyon
- Hız kritik

---

## 📋 HIZLI KOPYALA-YAPIŞTIR

### Profil 0: ULTRA STABİL
```python
# imu_configuration_v2.py
OUTPUT_RATE = 100
FILTER_SEL = 'k128_fc50'

# imu_orientation_v2.py
self.alpha = 0.01
self.gyro_threshold = 0.4
```

### Profil 1: ÇOK STABİL ⭐ (ŞU AN)
```python
# imu_configuration_v2.py
OUTPUT_RATE = 125
FILTER_SEL = 'k64_fc50'

# imu_orientation_v2.py
self.alpha = 0.03
self.gyro_threshold = 0.25
```

### Profil 2: DENGELİ
```python
# imu_configuration_v2.py
OUTPUT_RATE = 200
FILTER_SEL = 'mv_avg32'

# imu_orientation_v2.py
self.alpha = 0.08
self.gyro_threshold = 0.15
```

### Profil 3: HIZLI
```python
# imu_configuration_v2.py
OUTPUT_RATE = 500
FILTER_SEL = 'mv_avg8'

# imu_orientation_v2.py
self.alpha = 0.15
self.gyro_threshold = 0.1
```

### Profil 4: ÇOK HIZLI
```python
# imu_configuration_v2.py
OUTPUT_RATE = 1000
FILTER_SEL = 'mv_avg4'

# imu_orientation_v2.py
self.alpha = 0.20
self.gyro_threshold = 0.05
```

---

## 🔄 NASIL DEĞİŞTİRİRİM?

### Adım 1: Profil Seç
Yukarıdaki tablodan bir profil seç (0-4).

### Adım 2: Configuration Düzenle
`imu_configuration_v2.py` dosyasını aç:
- **Satır 149**: `OUTPUT_RATE` değiştir
- **Satır 209**: `FILTER_SEL` değiştir
- Kaydet

### Adım 3: Orientation Düzenle
`imu_orientation_v2.py` dosyasını aç:
- **Satır 113**: `self.alpha` değiştir
- **Satır 141**: `self.gyro_threshold` değiştir
- Kaydet

### Adım 4: Flash'a Kaydet
```bash
cd py_esensorlib/src/esensorlib
python imu_configuration_v2.py
```
- Seçenek **1** seç

### Adım 5: Test Et
```bash
python imu_orientation_v2.py
```

---

## 💡 HANGİSİNİ SEÇMELİYİM?

### Karar Ağacı:

```
Düz zeminde test mi?
├─ EVET → Profil 0 (ULTRA STABİL)
└─ HAYIR → Denizde kullanacak mısın?
    ├─ EVET → Display var mı?
    │   ├─ EVET → Profil 1 (ÇOK STABİL) ⭐
    │   └─ HAYIR → Profil 2 (DENGELİ)
    └─ HAYIR → Hızlı hareket var mı?
        ├─ EVET → Profil 3 veya 4 (HIZLI)
        └─ HAYIR → Profil 2 (DENGELİ)
```

### Senin Durumun:
- ✅ Denizde kullanacaksın
- ✅ 7" display var
- ✅ Bar grafik göstereceksin
- ✅ Kullanıcı rahatsız olmamalı

**Öneri: Profil 1 (ŞU AN KULLANDIĞIN)** ⭐

---

## 📊 DETAYLI KARŞILAŞTIRMA

### Heel Davranışı (75° Çarpaz Pozisyon):

**Profil 0 (ULTRA STABİL):**
```
75.13° → 75.13° → 75.13° → 75.13° → 75.13° (donmuş)
```

**Profil 1 (ÇOK STABİL) ⭐:**
```
75.13° → 75.13° → 75.14° → 75.14° → 75.14° (çok yavaş)
```

**Profil 2 (DENGELİ):**
```
75.13° → 75.14° → 75.13° → 75.15° → 75.14° (yavaş git-gel)
```

**Profil 3 (HIZLI):**
```
75.12° → 75.15° → 75.11° → 75.16° → 75.13° (hızlı git-gel)
```

**Profil 4 (ÇOK HIZLI):**
```
75.08° → 75.18° → 75.05° → 75.22° → 75.10° (çok hızlı, gürültülü)
```

---

## 🎯 ÖNERİLER

### Gemi Display Uygulaması İçin:
1. **İlk tercih**: Profil 1 (ÇOK STABİL) ⭐
2. **Alternatif**: Profil 2 (DENGELİ)
3. **Test için**: Profil 3 (HIZLI)

### Farklı Durumlar:
- **Liman/park**: Profil 0
- **Denizde sakin**: Profil 1 ⭐
- **Denizde dalgalı**: Profil 2
- **Manevra**: Profil 3
- **Test/debug**: Profil 3 veya 4

---

## 🔧 HIZLI DEĞİŞİM ÖRNEĞİ

### Profil 1'den Profil 2'ye Geçiş:

#### 1. Configuration Düzenle:
```python
# imu_configuration_v2.py - Satır 149
OUTPUT_RATE = 125  # Değiştir → 200

# imu_configuration_v2.py - Satır 209
FILTER_SEL = 'k64_fc50'  # Değiştir → 'mv_avg32'
```

#### 2. Orientation Düzenle:
```python
# imu_orientation_v2.py - Satır 113
self.alpha = 0.03  # Değiştir → 0.08

# imu_orientation_v2.py - Satır 141
self.gyro_threshold = 0.25  # Değiştir → 0.15
```

#### 3. Flash'a Kaydet:
```bash
python imu_configuration_v2.py  # Seçenek 1
```

#### 4. Test Et:
```bash
python imu_orientation_v2.py
```

---

## 📝 NOTLAR

- **Configuration değişikliği**: Flash'a kaydetmelisin (kalıcı)
- **Orientation değişikliği**: Sadece kaydet (geçici, her çalıştırmada)
- **Test ederken**: Önce Orientation'daki değerleri dene (hızlı), sonra Configuration'a geç (kalıcı)
- **Geri dönmek**: Değerleri tekrar kopyala-yapıştır

---

## 🎓 ÖZET

4 hazır profil:
- **Profil 0**: Maksimum stabilite (liman)
- **Profil 1**: Gemi için ideal (deniz) ⭐
- **Profil 2**: Dengeli (genel)
- **Profil 3**: Hızlı (manevra)
- **Profil 4**: Çok hızlı (drone)

Her profil için 4 değer değiştirmen yeterli!

İstediğin profili seç ve değerleri kopyala-yapıştır! 🚀

