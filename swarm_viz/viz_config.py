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
# Alanın güneybatısından, kuzeydoğuya bakan çapraz-üst görünüm.
# Konum alan merkezine göre verilir: (geri_x, geri_y, yükseklik) metre.
CAMERA_OFFSET_M = (-65.0, -65.0, 80.0)
