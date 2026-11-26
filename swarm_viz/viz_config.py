"""Görselleştirme ayarları (docs/cbba_plan.md, A0.0.4).

Buradaki HER değer "görselleştirme ayarı"dır: yalnızca görüntüyü etkiler,
deney parametresi değildir ve deney sonuçlarını değiştirmez.
Deney parametreleri CLAUDE.md bölüm 13'te kalır.
"""

# --- Engeller (A0.2) ---
OBSTACLE_HEIGHT_M = 1.0   # görselleştirme ayarı; 2,5 m uçuş irtifasından düşük
OBSTACLE_INSET_M = 0.5    # görselleştirme ayarı; engel kenarındaki şeritler blokların altında kalmasın
OBSTACLE_COLOR = (0.62, 0.60, 0.56)  # beton grisi

# --- Zemin, şeritler, sınır (A0.2) ---
GROUND_COLOR = (0.22, 0.25, 0.23)    # koyu zemin: gri şeritler ve beyaz sınır seçilebilsin
GROUND_SIZE_M = 500.0                # PX4 default.sdf ile aynı görsel boyut
STRIP_WIDTH_M = 0.15                 # çizgi kalınlığı (tarama genişliği değil; o 3 m ve veri setinden gelir)
STRIP_HEIGHT_M = 0.01
STRIP_COLOR = (0.70, 0.70, 0.70)
BOUNDARY_WIDTH_M = 0.30
BOUNDARY_HEIGHT_M = 0.02
BOUNDARY_COLOR = (0.95, 0.95, 0.95)
MIN_STRIP_LENGTH_M = 0.05            # bundan kısa şerit kutu yerine küçük kare olarak çizilir

# --- Sabit kamera (A0.3) ---
# Alanın güneyinden kuzeye bakan çapraz-üst görünüm. Kamera, alanın dört köşesi ekrana
# sığacak EN YAKIN noktaya otomatik konur (make_world.camera_pose). Aynı görüş açısında
# güneyden bakış, güneybatıdan çapraz bakışa göre merkeze ~%30 daha yakın (26 Kasım 2026 hesabı).
CAMERA_HFOV_DEG = 60.0          # yatay görüş açısı; Gazebo varsayılanı daha geniş ve her şeyi küçültüyor
CAMERA_ELEVATION_DEG = 45.0     # bakış eğimi (0 = yatay, 90 = tam tepeden)
CAMERA_AZIMUTH_DEG = 90.0       # kameranın merkeze göre geldiği yön: 90 = güneyden kuzeye bakış
CAMERA_ASPECTS = (16 / 9, 1000 / 845)  # sığma kontrolü: geniş ekran ve Gazebo varsayılan pencere oranı
CAMERA_FIT_MARGIN = 0.95        # köşeler ekran kenarının %95'ine kadar
