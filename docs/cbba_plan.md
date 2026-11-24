# CBBA Uygulama Planı

> Durum: **A0 kararları alındı (24 Kasım 2026). Plan son onay bekliyor; onaydan sonra A0.8'deki sırayla kodlamaya başlanır.**
> CLAUDE.md bölüm 14, kural 1: plan onaylanmadan kod yazılmaz.

---

## A0 — Görselleştirme

### A0.0 Amaç, kısıtlar ve kapsam

**Amaç:** Danışmanın "İHA'ların gerçekten hareket ettiği görülebilmeli" beklentisini karşılamak ve CBBA sonuçlarını ileride izlenebilir hale getirmek.

**Temel kısıtlar:**
- Görselleştirme CBBA geliştirmesini geciktirmemeli. CBBA öncesine yalnızca dar bir çekirdek alınır; geri kalanı CBBA sonrasına ertelenir (A0.7).
- Mevcut PX4 + Gazebo Harmonic + MAVSDK altyapısı korunur. PX4 dosyaları değiştirilmez.
- Görselleştirme kapatıldığında `connect_uav.py`, `takeoff_land.py`, `fly_task.py` ve `multi_takeoff_land.py` aynen çalışmaya devam eder.
- `swarm_core/` hiçbir Gazebo, MAVSDK veya arayüz kütüphanesi import etmez.
- **Görev ataması ve görev olayları genel bir arayüzdür** (A0.0.5). Bugün elle verilen atama, yarın CBBA çıktısı aynı biçimde verilir; CBBA eklendiğinde görselleştirme kodu değişmez.

**Uygulama sırası:** Önce A0.1 (2D canlı harita + panel), sonra A0.2–A0.3 (temel Gazebo sahnesi), sonra A0.5 (performans ölçümü). A0.4 ve iki İHA'lı görev uçuşu CBBA sonrasına bırakılır.

### A0.0.1 Tasarım referansı ve kullanılmayacak öğeler

**Referans:** `Downloads/Gazebo’da Sürü İHA Alan Taraması.png` ve `Downloads/Neon İHA Sürü Tarama Simülasyonu.png`. Bunlar yapay zekâ ile üretilmiş tasarım fikirleri; ikisi aynı fikrin sahne ve panel ağırlıklı versiyonları.

**Görsellerden alınacaklar:**
- Koyu zemin üzerinde açık renkli sınır
- Şeritlerde gri/yeşil renk ayrımı
- İHA başına renk (mavi/turuncu)
- Sağda bilgi paneli ve kuş bakışı harita
- Gösterge (renk açıklamaları), metre ölçeği, kuzey oku

**Görsellerden alınmayacaklar** (gerçek değil ya da projeye uymuyor):

| Görseldeki öğe | Neden kullanılmayacak |
|---|---|
| 161 görev, 103/161, 79/161 | AC10_0000'da **107** görev var. Bütün sayılar veri setinden ve görev durumundan gelecek. |
| Pil %76/%82, Enerji %80 | Enerji modeli yok (A4'ten sonra). Gösterilmeyecek. |
| Alan kapsama %49, 4.900 m² | Kapsama oranının tanımı henüz belirlenmedi (A0.6). Görev tamamlama oranıyla karıştırılmayacak. |
| "Algoritma: CBBA" seçimi | CBBA henüz yok. Panelde atamanın kaynağı yazılacak: elle verilen atama "Manuel atama", CBBA sonucu "CBBA" (A0.0.5). |
| Çok katlı binalar | Engeller 1,0 m yüksekliğinde beton bloklar olacak (A0.2). |
| Ağaçlar, koniler, helipad, neon ışık | "Daha sonra" listesinde; A0 kapsamında değil. |
| Durdur / Sıfırla / Ayarlar düğmeleri | Kontrol paneli değil, izleme paneli yapıyoruz. |

### A0.0.2 Doğrulanan Gazebo Harmonic altyapısı

Kurulu sürümler: gz-sim **8.15.0** (Harmonic), gz-msgs 10, gz-transport 13, gz-gui 8, gz-rendering 8.

| Mekanizma | Durum | Kaynak |
|---|---|---|
| Marker servisleri `/marker`, `/marker_array`, `/marker/list` | ✅ Var | gz-gui8 `src/plugins/marker_manager/MarkerManager.cc`; gz-sim8 `examples/standalone/marker/marker.cc` |
| `MarkerManager` GUI eklentisi | ✅ Kurulu ve kullanıcı GUI yapılandırmasında açık (`~/.gz/sim/8/gui.config`) | Yerel dosya kontrolü |
| Marker türleri: LINE_STRIP, LINE_LIST, ARROW, BOX, TRIANGLE_LIST, TEXT... | ✅ Mesajda tanımlı | `/usr/share/gz/gz-msgs10/protos/gz/msgs/marker.proto` |
| Marker `parent` alanı | ✅ Var (`parent->AddChild(visual)`). ⚠️ Görselin sahnedeki adı bilinmeli. | MarkerManager.cc |
| TEXT marker (İHA etiketi) | ❌ Büyük olasılıkla çizilmiyor: MarkerManager metin alanını okumuyor, ogre2'de `Ogre2Text` sınıfı yok. | MarkerManager.cc; `libgz-rendering-ogre2.so` sembol kontrolü |
| SDF `<polyline>` (yüksekliği verilen çokgen) | ✅ SDF 1.9; gz-sim8 görsellerde çiziyor (`CreateExtrudedPolyline`) | sdformat `sdf/1.9/polyline_shape.sdf`; gz-sim8 `src/rendering/SceneManager.cc` |
| Dünya SDF'inde `<gui>`, `--gui-config` | ✅ `--gui-config` > SDF `<gui>` > `~/.gz/sim/8/gui.config` | https://gazebosim.org/api/sim/8/gui_config.html |
| Başlangıç kamera konumu (`MinimalScene` → `<camera_pose>`) | ✅ | Aynı sayfa |
| `/gui/move_to/pose`, `/gui/follow` | ✅ Bu oturumda canlı olarak denendi ve çalıştı | — |
| SDF `<scene><grid>` | ⚠️ gz-sim8'de işlendiği bulunamadı. Yerine `GridConfig` GUI eklentisi var (kurulu). | gz-gui8 `src/plugins/grid_config/` |
| Gerçek zaman oranı (RTF) | ✅ `/world/<dünya_adı>/stats` → `gz.msgs.WorldStatistics.real_time_factor` | gz-sim8 `SimulationRunner.cc`; https://gazebosim.org/api/sim/8/pause_run_simulation.html |
| Python `gz.transport13`, `gz.msgs10` | ✅ Sistem Python'unda var; ⚠️ `.venv` içinde yok | Yerel kontrol |
| PX4 yer istasyonu telemetrisi | ✅ Her PX4 örneği `18570+i` portundan **14550**'ye gönderiyor | PX4 `px4-rc.mavlink`; `mavlink_main.h` (`DEFAULT_REMOTE_PORT_UDP 14550`) |
| PX4 dünya eklentileri | ℹ️ Dünya dosyasında değil, `server.config` içinde (`GZ_SIM_SERVER_CONFIG_PATH`, `gz_env.sh`) | `PX4-Autopilot/src/modules/simulation/gz_bridge/server.config` |
| PX4'ün çalışan dünyaya bağlanması | ✅ "gazebo already running world" dalı | `px4-rc.gzsim` |

### A0.0.3 Mimari (CBBA öncesi)

```text
 PX4 -i 0 ──┐  (yer istasyonu telemetrisi, 18570+i → 14550)
 PX4 -i 1 ──┴──► swarm_viz/live_map.py (venv)
                  │   MAVSDK ile pasif yer istasyonu; iki İHA'yı 14550'den dinler
                  │   2D harita + bilgi paneli (matplotlib + Tk)
                  ▲
                  │   görev ataması + görev olayları (UDP, 127.0.0.1)
 swarm_sim/fly_task.py ──► PX4 14540   (uçuş kontrolü değişmez)
```

- **Telemetri uçuş betiklerinden bağımsız.** Harita 14550'den PX4'ün kendi akışını dinler. Harita kapalıyken uçuş kodu etkilenmez.
- **Görev durumu telemetride yok.** Uçuş betiği atamayı ve görev olaylarını A0.0.5'teki arayüzle yerel UDP'ye "gönder ve unut" biçiminde yollar. Dinleyen yoksa hiçbir şey olmaz, betik beklemez.
- **Katman ayrımı:** `swarm_core/` (saf algoritma) ← `swarm_sim/` (PX4/MAVSDK uçuş) ← `swarm_viz/` (görselleştirme). `swarm_viz` diğerlerini okuyabilir; tersi olmaz.
- CBBA sonrası (A0.4) Gazebo işaretçileri için ayrı bir süreç eklenecek (`gz.transport13` yalnızca sistem Python'unda olduğu için). CBBA öncesi buna gerek yok.

### A0.0.4 Parametre ayrımı

- **Görselleştirme ayarları** tek dosyada, her biri "görselleştirme ayarı" olarak işaretli: `swarm_viz/viz_config.py`. Bunlar renkler, çizgi kalınlıkları, ızgara aralığı, kamera konumları, UDP portu, güncelleme sıklığı ve:
  - `OBSTACLE_HEIGHT_M = 1.0` (görselleştirme ayarı; 2,5 m uçuş irtifasından düşük)
  - `OBSTACLE_INSET_M = 0.5` (görselleştirme ayarı; A0.2'ye bakın)

  Bunlar deney sonuçlarını etkilemez.
- **Deney parametreleri** (v_max, a_max, λ, L_t, ω...) CLAUDE.md bölüm 13'te kalır. Görselleştirme bunları değiştirmez.
- **Test ayarları** (kaynaksız uçuş ayarları) CLAUDE.md bölüm 14, kural 2'deki gibi işaretli kalır.
- **3 m tarama genişliği** veri setinden gelir (CoverageTasks README: "sweep-width of 3 meters"). A0.4'teki efekt bunu gösterir; görselleştirme ayarı değildir.

### A0.0.5 Görselleştirme arayüzü: görev ataması + görev olayları

**İlke:** Görselleştirme (2D harita ve ileride Gazebo işaretçileri) yalnızca bu arayüzü okur. Atamanın kim tarafından üretildiğini bilmez. Bugün atama elle verilen görev listesinden, ileride CBBA çıktısından gelir. **CBBA eklendiğinde görselleştirme kodu değişmez**; yalnızca atamayı üreten taraf değişir.

Arayüz iki mesaj türünden oluşur. Her ikisi de JSON'dur ve yerel UDP ile (`127.0.0.1`, port `viz_config.py`'de) "gönder ve unut" biçiminde gönderilir. Dinleyen yoksa gönderen beklemez, hata vermez.

**1) Görev ataması** (`type: "assignment"`): uçuş başlamadan bir kez, atama değişirse yeniden gönderilir.

```json
{
  "type": "assignment",
  "time": 1795515220.12,
  "scenario": "scenarios/AC10_0000.json",
  "source": "manual",
  "assignment": { "1": [1, 2, 3, 4], "2": [] }
}
```

- `assignment`: İHA kimliği (= PX4 Sistem ID) → görev kimliklerinin **uçuş sırasıyla** listesi (`{iha_id: [görev_id sırası]}`). Görev kimlikleri `swarm_core/dataset.py`'deki numaralardır (veri setindeki sıra, 1'den başlar).
- `source`: atamanın kaynağı. Yalnızca iki değer alır:
  - `"manual"` → ekranda **"Manuel atama"**
  - `"cbba"` → ekranda **"CBBA"**
- Elle verilen atama hiçbir zaman CBBA sonucu gibi gösterilmez. Etiket panelin üstünde ve gösterge kutusunda sürekli görünür.
- Yeni bir `assignment` mesajı öncekinin yerine geçer. Ekran yeni atamaya göre yeniden çizilir; o ana kadar tamamlanan görevler tamamlanmış olarak kalır. Bu, ileride İHA kaybı sonrası yeniden atama için gerekli.

**2) Görev olayları** (`type: "event"`):

```json
{ "type": "event", "time": 1795515230.48, "uav": 1, "event": "task_started",  "task": 3 }
{ "type": "event", "time": 1795515241.90, "uav": 1, "event": "task_finished", "task": 3 }
```

| `event` | Anlamı | Zorunlu mu |
|---|---|---|
| `task_started` | İHA görevin tarama çizgisine başladı (başlangıç noktasında durdu, çizgi boyunca uçmaya başladı) | Evet |
| `task_finished` | İHA çizginin bitiş noktasına vardı ve durdu | Evet |
| `takeoff`, `landed` | Kalkış ve iniş (panelde durum bilgisi; `task` alanı yok) | Hayır |

- Ekranda: `task_started` → şerit "aktif" (İHA renginde, kalın); `task_finished` → şerit yeşil, tamamlanan görev sayısı +1.
- Atamada olmayan bir görev için olay gelirse uyarı yazılır, ama ekranda yine gösterilir (gerçekte ne olduysa o görünür).
- Konum, hız ve irtifa bu arayüzden **gelmez**; doğrudan PX4 telemetrisinden okunur (A0.0.3). Arayüz yalnızca telemetride olmayan bilgiyi taşır: atama ve görev durumu.

**Kim gönderir:**

| Dönem | `assignment` | Olaylar |
|---|---|---|
| Şimdi (CBBA öncesi) | Uçuş betiği, komut satırındaki görev listesinden: `fly_task.py --tasks 1 2 3 4` → `{"1": [1,2,3,4]}`, `source: "manual"`. Ya da harita bir JSON dosyasından okur: `live_map.py --assignment dosya.json`. | Uçuş betiği (`swarm_sim/mission_events.py` üzerinden) |
| CBBA sonrası | CBBA'yı çalıştıran kod, aynı biçimde, `source: "cbba"` | Aynı uçuş kodu, aynı olaylar |

**Kod tarafı:**
- `swarm_sim/mission_events.py`: gönderen taraf (`send_assignment(...)`, `send_event(...)`). Yalnızca standart kütüphane.
- `swarm_viz/assignment.py`: mesajları ayrıştırır ve doğrular. Bilinmeyen görev kimliği, aynı görevin iki İHA'ya verilmesi ve `manual`/`cbba` dışında bir kaynak hata olur.
- `swarm_viz/mission_state.py`: atama + olaylar → ekrandaki durum (aktif/tamamlanan görevler, ilerleme). Saf Python.
- Atama ve olay biçimi bilinçli olarak `swarm_core` dışında tutuldu. CBBA (`swarm_core`) yalnızca `{iha_id: [görev_id]}` sözlüğünü üretir; onu bu mesaja saran ve gönderen kod `swarm_sim` tarafında olur. Böylece `swarm_core` ağ ve arayüzden bağımsız kalır.
- **Testler:** `tests/test_assignment.py` (geçerli/geçersiz mesajlar, `manual`/`cbba` etiketleri), `tests/test_mission_state.py` (olay sırası → beklenen durum; yeniden atamada tamamlanan görevlerin korunması).

---

### A0.1 — Canlı 2D harita ve bilgi paneli · **CBBA öncesi**

**Mekanizma:** Gazebo'dan bağımsız ayrı bir masaüstü penceresi (WSLg).

**Kütüphaneler:**
- `matplotlib` 3.11 (venv'de var) + `TkAgg`. **Kurulum (kullanıcı):** `sudo apt install python3-tk`.
- `mavsdk` 4.2 (venv'de var): 14550'de pasif bağlantı, `get_systems()` ile iki İHA.
- Standart kütüphane: `asyncio`, `socket`, `json`, `threading`.

**Gösterilecekler** (hepsi gerçek veriden):
- **Veri setinden:** alan sınırı, 10 engel (0,5 m içeri küçültülmüş hali, A0.2 ile aynı), 107 tarama şeridi.
- **Telemetriden:** İHA konumu (enlem/boylam → dünya ENU metre), yön oku (hız vektörü), son N saniyelik iz.
- **Panel, her İHA için:** Sistem ID, hız, irtifa, uçuş modu, aktif görev.
- **Atamadan:** her İHA'ya atanmış şeritler İHA'nın renginde ince çizgiyle.
- **Görev olaylarından:** aktif şerit kalın, tamamlanan şerit yeşil; tamamlanan/toplam görev ve ilerleme çubuğu (**görev tamamlama oranı**).
- **Atama kaynağı etiketi:** `source` alanından: "Manuel atama" veya "CBBA" (A0.0.5).
- Renk açıklamaları, metre ölçek çubuğu, kuzey oku, koyu tema.

**Dosyalar:**
- **Yeni:**
  - `swarm_viz/__init__.py`, `swarm_viz/viz_config.py`
  - `swarm_viz/geo.py` (enlem/boylam ↔ dünya metre)
  - `swarm_viz/assignment.py` (A0.0.5)
  - `swarm_viz/mission_state.py` (olaylardan görev durumu; saf Python)
  - `swarm_viz/live_map.py` (pencere + telemetri)
  - `swarm_sim/mission_events.py` (A0.0.5 arayüzünün gönderen tarafı: `assignment` ve `task_started`, `task_finished`, `takeoff`, `landed` olayları; hata olursa sessizce geçer)
- **Değişecek:** `swarm_sim/fly_task.py` (başlarken `assignment` (`source: "manual"`), görevlerde `task_started`/`task_finished`; uçuş davranışı değişmez).
- **Testler:** `tests/test_geo.py`, `tests/test_assignment.py`, `tests/test_mission_state.py`, `tests/test_live_map_smoke.py` (pencere açmadan `Agg` ile bir kare çizer).

**CBBA öncesi demo:**
- Tek İHA görev uçuşu: `fly_task.py`, AC10_0000, görev 1–4, atama `{"1": [1,2,3,4]}`, kaynak `manual`.
- İki İHA'nın haritada aynı anda görünmesi: `multi_takeoff_land.py`.

İki İHA'ya elle görev verilen uçuş CBBA sonrasına ertelendi (A0.7).

**Ortak koordinat sistemi:** Harita konumları GPS'ten (enlem/boylam) dünya başlangıcına göre metreye çevirir; dünya başlangıcı PX4 dünyasındaki `spherical_coordinates` (47.397971057728974, 8.546163739800146). Veri seti (0,0) = dünya (0,0); x doğu, y kuzey.

**Zorluk / süre:** Orta. **≈ 3 iş günü.**
- Olay modülü + `fly_task` değişikliği: 0,5
- Atama + görev durumu + coğrafi yardımcılar ve testleri: 1
- Harita/panel: 1,5

**Riskler:**
- WSLg'de matplotlib canlı güncelleme hızı. Hedef 5 Hz; yetmezse iz kısaltılır.
- 14550'yi aynı anda tek süreç dinleyebilir; QGroundControl açıksa çakışır.
- MAVSDK'nin tek bağlantıda iki sistemi ayırması bu projede henüz denenmedi. İlk iş kısa bir deneme.
- GPS tabanlı konum gürültülü olabilir. Görünür bir sapma olursa yerel konum + bilinen kalkış noktası kullanılır.

---

### A0.2 — Temel Gazebo dünyası · **CBBA öncesi**

**Mekanizma:** GeoJSON → SDF 1.9 dünya üreticisi. Fizik, `spherical_coordinates`, `magnetic_field` ve `atmosphere` değerleri PX4'ün `default.sdf` dosyasından **okunarak** kopyalanır (PX4 dosyasına yazılmaz).

**Sahne içeriği:**
- **Zemin:** koyu gri düzlem. Zemin çarpışması PX4 dünyasındaki gibi kalır.
- **Izgara:** `GridConfig` GUI eklentisi (fiziği etkilemez). Hücre 10 m, görselleştirme ayarı. Yedek plan: SDF'te ince kutularla ızgara çizgileri.
- **Alan sınırı:** açık renkli ince kutular (yükseklik ~2 cm), collision yok.
- **Tarama şeritleri:** her görev için ince gri kutu (107 adet), collision yok.
- **Engeller:** `<polyline>` görseli, yükseklik `OBSTACLE_HEIGHT_M = 1.0`, beton grisi, **`<collision>` yok**.
  - **0,5 m içeri küçültülmüş** çizilir (`shapely` ile `polygon.buffer(-OBSTACLE_INSET_M)`). Böylece engel kenarları boyunca uzanan şeritler blokların altında kalmaz.
  - **Neden:** Şeritlerin bir kısmı engel kenarlarının tam üzerinden geçiyor. Engel içine düşer gibi görünen bütün şerit noktalarının kenara uzaklığı 0,000 m (kendi kontrolüm: 20.779 örnek nokta). Engeller 0,5 m içeri küçültülünce hiçbir şerit engel içine girmez (kullanıcının shapely kontrolü). Bu bir veri seti hatası değil; geometri değiştirilmez, yalnızca çizim 0,5 m içeriden yapılır.
  - **Yeni bağımlılık:** `shapely` (venv'e `pip install shapely`; A5'teki kapsama hesabında da kullanılacak).

**Dünyanın yüklenmesi** (PX4 dosyaları değişmeden): `px4-rc.gzsim`, `PX4_GZ_WORLDS` değişkenini her seferinde PX4 klasörüne sabitliyor. Bu yüzden Gazebo önce bizim dünyamızla başlatılır, PX4 de çalışan dünyayı bulup İHA'yı içine yerleştirir.

```bash
# Terminal 0: Gazebo, PX4 eklenti ayarlarıyla
source ~/PX4-Autopilot/build/px4_sitl_default/gz_env.sh   # yalnızca okunur
GZ_IP=127.0.0.1 gz sim -r ~/suruiha/worlds/ac10_0000.sdf --gui-config ~/suruiha/worlds/gui_ac10.config
# Terminal 1 ve 2: mevcut PX4 komutları + PX4_GZ_NO_FOLLOW=1
```

Mevcut yöntem (`make px4_sitl gz_x500` ve `default` dünya) hiç değişmeden çalışmaya devam eder.

**Dosyalar:**
- **Yeni (commit edilecek):** `swarm_viz/make_world.py` (üretici), `worlds/gui_ac10.config` (varsayılan GUI eklentileri + `GridConfig` + sabit kamera).
- **Üretilen (commit edilmeyecek):** `worlds/*.sdf` → `.gitignore`'a `worlds/*.sdf` eklenecek.
- **Test:** `tests/test_make_world.py`. Geçici klasöre dünya üretir, XML'i ayrıştırır ve kontrol eder:
  - 10 engel ve 107 şerit
  - Engel yüksekliği 1,0 m (< 2,5 m)
  - Engellerde `<collision>` yok
  - Engel köşeleri, veri setindeki poligonun 0,5 m içeri küçültülmüş hali
  - Hiçbir şerit küçültülmüş engel içine girmiyor

**Zorluk / süre:** Orta. **≈ 2–2,5 gün.**

**Riskler:**
- `<polyline>` içbükey engellerde düzgün çizilmeyebilir. Prototipte 8 köşeli engellerle (1 ve 4) denenecek. Yedek plan: üçgenlere bölme.
- `buffer(-0.5)` çok ince bir engeli yok edebilir ya da ikiye bölebilir (sonuç `MultiPolygon`). Bu durumda bütün parçalar çizilir; boş kalan engel uyarıyla atlanır.
- PX4 ilk örneğinin bu yöntemle dünyayı bulması bu projede henüz denenmedi.

---

### A0.3 — Sabit kamera · **CBBA öncesi**

- **Mekanizma:** `worlds/gui_ac10.config` → `MinimalScene` → `<camera_pose>`: alanın tamamını gösteren sabit çapraz-üst görünüm. PX4 komutlarına `PX4_GZ_NO_FOLLOW=1` eklenir.
- Kuş bakışı kamera ve ışık/gölge ayarları CBBA sonrasına ertelendi. Dünya PX4'teki ışığı aynen kullanır.
- **Zorluk / süre:** Kolay. **≈ 0,5 gün.**
- **Risk:** `PX4_GZ_NO_FOLLOW` henüz denenmedi (CLAUDE.md, Aşama 2 notu).

---

### A0.4 — Dinamik uçuş görselleştirmesi · **CBBA sonrası**

**Mekanizma:** `swarm_viz/gz_markers.py` (sistem `python3`, `gz.transport13`) → `/marker_array`. Konumu `live_map.py`'nin yerel UDP durum yayınından, atamayı ve görev olaylarını A0.0.5 arayüzünden alır. 2D harita ile aynı arayüz kullanıldığı için CBBA eklendiğinde bu kod da değişmez.

| Özellik | İşaretçi | Not / risk |
|---|---|---|
| Gerçek uçuş izi (İHA-1 mavi, İHA-2 turuncu) | `LINE_STRIP` | İz parçalara bölünür (ör. 200 noktada bir yeni kimlik). |
| Planlanan rota | `LINE_LIST` (kesik çizgi taklidi) | Kesik çizgi türü yok. |
| Yön okları | `ARROW` | ogre2'de çizildiği doğrulanacak. |
| Tamamlanan şerit → yeşil | `LINE_LIST`, gri SDF çizginin biraz üstünde | SDF görselinin rengi çalışırken değiştirilemiyor. |
| 3 m tarama efekti (yarı saydam) | `BOX`/`TRIANGLE_LIST`, `parent` = İHA görseli | Saydamlık ve görsel adı doğrulanmadı; yedek planlar hazır. |
| İHA etiketi | `TEXT` | ❌ Büyük olasılıkla çizilmez. Yedek plan: renkli küre, isimler 2D panelde. |
| Işık/gölge ayarları, kuş bakışı kamera | SDF `<scene>`, `/gui/move_to/pose` | Görsel iyileştirme. |

**Zorluk / süre:** Zor. **≈ 3–5 gün** (+ ışık/kamera 0,5).

---

### A0.5 — Performans ölçümü (RTF) · **CBBA öncesi**

- **Ölçüm:** `/world/<dünya>/stats` → `real_time_factor`, her senaryo için 60 s ortalama ve en düşük değer. Senaryo: iki İHA havada bekliyor (`multi_takeoff_land.py`).
- **CBBA öncesi karşılaştırma:**
  1. PX4 `default` dünyası (referans)
  2. `ac10_0000` dünyası
  3. `ac10_0000` + 2D harita açık
- A0.4 eklendiğinde her özellik (iz, ok, efekt, gölge) ayrı ayrı ölçülür. RTF'yi belirgin düşüren özellik `viz_config.py`'de varsayılan olarak kapalı yapılır.
- **Dosya:** `swarm_viz/measure_rtf.py` (sistem python3 ya da `gz topic -e` çıktısını ayrıştırma). Sonuçlar `docs/` altına tablo olarak yazılır.
- **Süre:** ≈ 0,5 gün.

### A0.6 — Metriklerin karıştırılmaması

- **Görev tamamlama oranı** = tamamlanan görev / toplam görev. Görev olaylarından gelir. A0'da panelde **yalnızca bu** gösterilir.
- **Fiziksel alan kapsama oranı:** uçulan izin 3 m tarama alanının, engel dışındaki alana oranı (`shapely`). Tanım A5 metrikleriyle birlikte yapılacak. **A0'da gösterilmeyecek.**

### A0.7 — CBBA öncesi / sonrası

| Özellik | Ne zaman | Süre |
|---|---|---|
| 2D canlı harita + panel (atama girdisi, görev olayları dahil) | **CBBA öncesi** | ≈ 3 gün |
| Temel Gazebo dünyası (ızgara, sınır, şeritler, 1 m engeller) | **CBBA öncesi** | ≈ 2–2,5 gün |
| Sabit kamera | **CBBA öncesi** | ≈ 0,5 gün |
| Performans ölçümü (temel) | **CBBA öncesi** | ≈ 0,5 gün |
| Gazebo izleri, oklar, yeşile dönen şeritler, tarama efekti, planlanan rota | CBBA sonrası | ≈ 3–5 gün |
| Işık ayarları, kuş bakışı kamera | CBBA sonrası | ≈ 0,5 gün |
| İki İHA'ya görev verilen uçuş (ortak koordinat sistemi ile) | CBBA sonrası (CBBA çıktısıyla, Aşama 4) | ≈ 1–1,5 gün |

**CBBA öncesi toplam: ≈ 6–6,5 iş günü.** CBBA sonrası görselleştirme işleri: ≈ 4,5–7 gün.

### A0.8 Test ve commit planı (her parça ayrı commit)

1. `feat(viz): assignment and mission event interface` (`mission_events.py` + `fly_task.py` olayları) + test + tek İHA uçuşuyla doğrulama
2. `feat(viz): assignment parsing, mission state and geo helpers` + testler
3. `feat(viz): live 2D map and panel` + `Agg` çizim testi + uçuş sırasında elle doğrulama
4. `chore: ignore generated worlds` (`.gitignore`: `worlds/*.sdf`)
5. `feat(viz): GeoJSON to SDF world generator with 0.5 m obstacle inset` + XML testi
6. `feat(viz): fixed camera GUI config` (elle doğrulama)
7. `feat(viz): RTF measurement` + `docs` sonuç tablosu

Her commit'ten önce `pytest`; uçuşa dokunan değişikliklerden sonra simülasyonda uçuş.

### A0.9 Kararlar

| # | Karar | Durum |
|---|---|---|
| 1 | 2D pencere: matplotlib + Tk. `python3-tk` kullanıcı tarafından kurulacak. | ✅ Karar verildi |
| 2 | Engel görsel yüksekliği 1,0 m, "görselleştirme ayarı" olarak işaretli. | ✅ Karar verildi |
| 3 | Yalnızca üretici betik commit edilir; `worlds/*.sdf` `.gitignore`'da. | ✅ Karar verildi |
| 4 | CBBA öncesi: 2D harita + panel, temel dünya, sabit kamera, performans ölçümü. Gerisi sonraya. | ✅ Karar verildi |
| 5 | 23 görev konusu risk değil: şeritler engel kenarları boyunca; engeller 0,5 m içeriden çizilir. | ✅ Karar verildi, doğrulandı |
| 6 | Görselleştirme, görev atamasını (`{iha_id: [görev_id sırası]}`) ve görev başladı/bitti olaylarını genel bir arayüzden alır (A0.0.5). Elle verilen atama "Manuel atama", CBBA çıktısı "CBBA" olarak etiketlenir; CBBA eklendiğinde görselleştirme kodu değişmez. | ✅ Karar verildi |

### Daha sonra (isteğe bağlı, A0 kapsamı dışında)

- x500 modellerine farklı renklerde LED (model SDF'ini kopyalayıp renk ekleme; PX4 modeli değiştirilmez).
- Neon benzeri ışıklı rota efektleri.
- Gerçekçi arazi dokuları; ağaçlar yalnızca alan dışında, dekor olarak.
- React + FastAPI + WebSocket kontrol paneli.
- A4 enerji modelinden sonra pil ve enerji göstergeleri.

---

# CBBA — Dağıtık görev atama

> Durum: **TASLAK — onay bekliyor.** Kod yazılmadı.
> **Birincil kaynak:** Grøntved, Lundquist, Christensen, "Decentralized Multi-UAV Trajectory Task Allocation in Search and Rescue Applications", ICAR 2023, DOI 10.1109/icar58858.2023.10406912 (yazarların kabul edilmiş son taslağı, 8 sayfa; `~/makaleler/Grontved2023.pdf`, repoda değil). Aşağıda **[G §V-A]** = bu makalenin V-A bölümü, **[G Eq. 7]** = denklem 7.
> **İkincil kaynak:** Choi, Brunet, How, "Consensus-Based Decentralized Auctions for Robust Task Allocation", IEEE T-RO 25(4), 2009 = makalenin [13] numaralı kaynağı. **Bu PDF henüz elimizde değil.** Choi 2009'a dayanan maddeler yalnızca Grøntved'in Choi 2009'u nasıl özetlediğine göre yazıldı ve **[Choi 2009, G'den aktarma]** diye işaretlendi; A1'den önce asıl metinden doğrulanmalı.
> İşaretler: **MAKALEDE YOK – karar gerekli** = Grøntved 2023'te bulunamadı, tahmin edilmedi; her birine öneri ve gerekçe yazıldı (C8).

## C1. Problem tanımı

- Arama alanı, engelleri de içeren bir poligondur. Bu alan önceden **doğru parçalarına (tarama şeritlerine)** bölünmüştür; alanı taramak için her şerit bir İHA tarafından bir kez uçulmalıdır. [G §IV]
- Her İHA'ya birden çok şerit verilir. Bu yüzden problem çok-atamalı (multi-assignment) bir görev atama problemidir. [G §IV]
- **Görev = iki uçlu tarama şeridi:** `j ≜ {u0, u1}`, yani bir giriş ve bir çıkış noktası. [G Eq. 4]
  - Nokta görevden farkı: görev bitince İHA başladığı yerde değil, diğer uçta olur. Bu yüzden görevler arası maliyet hem giriş hem çıkış noktasına bağlıdır. [G §IV]
  - `u0 = u1` özel durumu makalede açıkça anılıyor. h1.json'daki 9. görev (`(7,0) → (7,0)`) bu durumdur ve nokta görev gibi işlenir. [G §IV]
- **Yön seçimi:** Her şerit iki yönde uçulabilir. İHA bir şeridi demetine (bundle) eklerken iki yönü de dener ve puanı en çok artıran yönü seçer. [G §IV, Eq. 8]
  - Yön bilgisi ve yol sırası **diğer İHA'lara gönderilmez**; yalnızca kimin hangi görevi kazandığı paylaşılır. Böylece iletişim yükü orijinal CBBA'dan artmaz. [G §IV-A]
- **Amaç:** kurtulanları olabildiğince çabuk bulmak, yani tarama süresini en aza indirmek. [G §IV] Bu, zamana göre indirimli ödülün toplamını en büyüklemek olarak modellenir. [G Eq. 6]
- **Kapasite:** `L_t` bu makalede **azami uçuş süresidir (saniye)**. Bir İHA'nın yol maliyetlerinin toplamı bu değeri aşamaz. [G §V]
  - ⚠️ Orijinal CBBA'da `L_t` bir İHA'nın alabileceği **görev sayısı**dır. [G §III, Choi 2009 G'den aktarma] Grøntved aynı sembolü süre bütçesi olarak kullanıyor. Uygulamada bu ikisi karıştırılmayacak; kodda `capacity_s` adı kullanılacak.
- **Başlangıç noktası (depot):** Her problemde rastgele seçilir ve bütün İHA'lar için ortaktır. [G §V-A] Rastgeleliğin nasıl yapıldığı yazmıyor → **MAKALEDE YOK – karar gerekli** (K4).

## C2. CBBA'nın iki aşaması

CBBA iki aşamayı dönüşümlü olarak tekrarlar: (i) **demet oluşturma** (bundle construction), (ii) **çakışma çözümü / uzlaşma** (conflict resolution / consensus). Çakışmasız bir atama elde edilip `N_min ≜ min{N_t, N_u·L_t}` sağlanana kadar sürer. [G §III, Choi 2009 G'den aktarma]

### C2.1 Choi 2009'dan gelen kısımlar (orijinal CBBA) — [G §III'te özetlendiği haliyle]

- Her İHA `i` iki liste tutar:
  - **Demet `b_i`:** görevler eklenme sırasıyla.
  - **Yol `p_i`:** aynı görevler, puanı en çok artıran uçuş sırasıyla.
- **Marjinal puan artışı** (nokta görevler için):
  ```text
  c_ij[b_i] = 0                                         eğer j ∈ b_i
            = max_{n ≤ |p_i|}  S_i^{p_i ⊕n {j}} − S_i^{p_i}   aksi halde        (G Eq. 1)
  ```
  `⊕n`: görevi yolun n'inci elemanından sonra eklemek.
- **Demet ve yol güncellemesi:**
  ```text
  b_i = b_i ⊕end {J_i},    p_i = p_i ⊕_{n_i,J_i} {J_i}                        (G Eq. 2)
  ```
  `J_i`: puanı en çok artıran görev; `n_i`: yoldaki en iyi ekleme yeri.
- **Azalan marjinal kazanç (DMG):** Bir görevin değeri, önüne başka görev eklenince artamaz. CBBA'nın garantileri için puan fonksiyonu bunu sağlamalıdır.
  ```text
  c_ij[b_i] ≥ c_ij[b_i ⊕end b]                                                (G Eq. 5)
  ```
- **Uzlaşma aşaması:** Her İHA komşularına kazanan teklif listesini, kazanan İHA listesini ve her İHA'dan son bilgi aldığı zaman damgasını gönderir. Çakışmalar yerel **eylem kurallarıyla** çözülür. [G §III → Choi 2009]
  - ⚠️ Eylem kurallarının kendisi (güncelle / sıfırla / bırak tablosu) Grøntved'de **yazmıyor**; Choi 2009'dan alınacak (K1).
- **Teklif kaybedilince:** Demette o görevden **sonra** eklenen görevler de çıkarılır, çünkü puanları artık geçersiz bilgiye dayanır. [G §III]
- **Karmaşıklık:** Bir İHA için demet oluşturma en kötü durumda `O(N_t · L_t)`. [G Eq. 3]
- **Yakınsama:** En fazla `max{N_t, L_t·N_u} · D` iterasyonda; `D` ağ çapı, en fazla `N_u`. [G §III] Tam bağlı ağda `D = 1`.
- **Optimallik:** İHA'ların kazananlar hakkındaki bilgisi doğruysa en az %50 optimallik garantisi. [G §III]

### C2.2 Grøntved 2023'ün katkısı (yörünge görevleri)

- **Yönlü marjinal puan:** Her olası ekleme yeri ve her iki yön denenir.
  ```text
  c_ij[b_i] = 0                                                             eğer j ∈ b_i
            = max_{n ≤ |p_i|}  max_dir  S_i^{p_i ⊕n {j_dir}} − S_i^{p_i}         aksi halde   (G Eq. 8)
  ```
  `j_dir`: önceki görevlere ve yönlere göre en yüksek puanı veren yaklaşma yönü (açgözlü iyileştirme). [G §IV-A]
- **Yön değiştirme kuralı:** İHA, `τ(p_{u1}) < τ(p_{u0})` ise yani çıkış ucuna daha erken varabiliyorsa `u0` ile `u1`'i yer değiştirir. [G §IV-A]
- **İlk görev** eklenirken puan İHA'nın başlangıç konumuna göre hesaplanır. [G §IV-A]
- Açık artırmayı kazandıktan sonra, uzlaşmadan önce, İHA görevi en iyi yönde ve en iyi yere yoluna ekler (G Eq. 2). Yön ve sıra paylaşılmaz. [G §IV-A]
- **Sınırlılık:** Makale Eq. 8 ile DMG'nin (Eq. 5) korunduğunu **kanıtlamıyor** → A2'de deneysel olarak test edilecek (C5).

## C3. Puan fonksiyonu ve maliyet modeli

**Zamana göre indirimli ödül:**
```text
S_i^{p_i} = Σ_{j ∈ p_i}  λ^{τ_ij(p_i)} · c̄_j                                   (G Eq. 6)
```
- `τ_ij(p_i)`: İHA `i`'nin mevcut yol `p_i` üzerinde görev `j`'ye **varış** süresinin tahmini.
- `c̄_j`: görevin sabit ödülü. Makalede bütün görevler için sabit tutuluyor. [G §IV-A] Değeri yazmıyor (K3).
- `λ ∈ (0, 1)`: indirim çarpanı. Deneylerde `λ = 0.95`. [G §V]

**Hız rampası modeli** (görevler arasında tam duruş):
```text
             ⎧ sqrt( 4·d / a_max ),            d <  d_a
  τ(d)  =    ⎨                                                 d_a = v_max² / a_max      (G Eq. 7)
             ⎩ d / v_max  +  v_max / a_max,    d ≥ d_a
```
- `d`: gidilecek mesafe. Makalede: yol `p_i` üzerinde görev `j`'ye kadar biriken mesafe `d_i^j`.
- `v_max = 3 m/s`, `a_max = 1 m/s²` ⇒ `d_a = 9 m`. [G §V]
- Model, SAR'daki keskin dönüşlerde İHA'nın neredeyse durmasını temsil eder; görevler arasında tam duruş zorunlu tutularak ek maliyet eklenir. Kaynağı Bähnemann vd. 2021 [8] ve Agarwal & Akella 2022 [11]. [G §IV-A]
- `τ_i(p_i)`, bir önceki görevin çıkış noktasından sonraki görevin giriş noktasına kadar, yoldaki her görev için süreyi hesaplar. [G §IV-A]
- Kontrol için iki örnek: `d = 4,5 m` ⇒ `τ = √18 ≈ 4,243 s`; `d = 20 m` ⇒ `τ = 20/3 + 3 ≈ 9,667 s`. Bu değerler A2'de birim testi olacak.
- ⚠️ Makale şunları açıkça yazmıyor:
  - Rampanın **şeridin kendi uçuşuna** ayrı mı uygulandığı (giriş ve çıkışta durarak).
  - `τ_ij`'nin şeridin **başlangıcına** mı **bitişine** mi varış süresi olduğu.

  → **MAKALEDE YOK – karar gerekli** (K2).

**Nokta görev karşılaştırması** (%6 sonucu için): (i) giriş noktasına Öklid uzaklığıyla tek nokta maliyet tahmini; (ii) yön iyileştirmeli yörünge tahmini. [G §V-A]

## C4. Parametre tablosu

| Parametre | Değer | Kaynak | Not |
|---|---|---|---|
| İndirim çarpanı `λ` | **0,95** | [G §V] "discount factor λ = 0.95" | **Karar: 0,95 kullanılacak.** Yazarların `trajallocpy` kodunda 0,99 olduğu bildirildi (kullanıcı notu; bu planda doğrulanmadı). Karşılaştırma makaledeki sonuçlarla yapıldığı için makale metni esas. |
| `v_max` | 3 m/s | [G §V] | Simülasyonda ölçülen en yüksek hız 3,13 m/s (CLAUDE.md §13) |
| `a_max` | 1 m/s² | [G §V] | |
| `d_a` | 9 m | [G Eq. 7] türetilmiş | `v_max²/a_max` |
| Ödül `c̄_j` | sabit | [G §IV-A] | Sayısal değer → K3 |
| Kapasite `L_t` (D1 ana karşılaştırma) | 2 İHA × **1200 s** | [G §V intro, §V-A, Fig. 2, Fig. 3] | |
| Kapasite (ölçeklenebilirlik) | 2 İHA: 1500 s · 4: 750 s · 6: 600 s · 8, 10, 12, 14: 500 s | [G Fig. 4 ve Fig. 5 açıklamaları] | ⚠️ İHA sayıları **2'şer adımla**: 2, 4, 6, 8, 10, 12, 14. 9, 11, 13 İHA test edilmemiş. |
| Ağ topolojisi | Tam bağlı | [G §V] | Yazarlar, topoloji ve tutarsız bilginin etkisinin az olduğunu Choi 2009'a dayanarak söylüyor. |
| Azami atama çarpanı `ω` | 15 | [G §V] → Turner vd. 2017 [26] | Aynı görevlerin tekrar tekrar açık artırmaya çıkmasını önler. **Tanım Grøntved'de yok** → K5. |
| Depot | Rastgele, bütün İHA'lar için ortak | [G §V-A] | Dağılım ve tekrar sayısı → K4 |
| Veri seti | AC300: 300 ortam, her biri 10.000 m², 0–15 engel, 35–161 görev | [G §V] | |
| Sensör | "3 m² field-of-view" | [G §V] | ⚠️ CoverageTasks README'si "sweep-width of 3 meters" diyor; makalede birim m². Görselleştirmede 3 m genişlik kullanılacak (README). |
| Görev üretimi | Agarwal & Akella [11] tarama çizgileri (boustrophedon) | [G §V] | `scenarios/` verisi bu |
| **Makale sonuçları (karşılaştırma hedefleri)** | | | |
| Toplam süre, 2 İHA × 1200 s, bütün AC300 | Merkezi [11]: 544.592 s · Grøntved: 554.920 s · fark 10.328 s = **%1,9** | [G §V] | |
| Yörünge ve nokta puanlama | Yörünge ortalama **%6** daha iyi | [G §V-A, Fig. 2] | ⚠️ Metinde "2 İHA, 1200 s" deniyor, ama hemen ardından "farklı İHA sayılarında" deniyor; Fig. 2 açıklaması 2 İHA diyor. D1'de 2 İHA esas alınacak. |
| En uzun İHA süresi (ortalama) | 2 İHA: **972 s** · 14 İHA: **229 s**; ~10 İHA'dan sonra belirgin iyileşme yok | [G §V-A, Fig. 4] | Ölçeklenebilirlik kapasiteleriyle |
| Yakınsama iterasyonu | İHA sayısıyla hafif artış | [G §V-B, Fig. 5] | Sayısal değer yalnızca grafikte |
| Yazarların donanımı | Python, i5-9400F, 16 GB, Ubuntu 20.04 | [G §V] | |

## C5. Aşamalar

| Aşama | İçerik | Bitti sayılma koşulu |
|---|---|---|
| **A1** CBBA çekirdeği (Python, simülasyonsuz) | `swarm_core` içinde: rampa (Eq. 7), puan (Eq. 6), yönlü demet oluşturma (Eq. 8), uzlaşma (Choi 2009 kuralları), mesaj geçişli ağ simülasyonu (tam bağlı, senkron turlar → K6) | Çakışmasız atama üretiyor; `swarm_core` dışında bağımlılık yok |
| **A2** h1 ile birim testler | Elle hesaplanmış küçük örnekler: Eq. 7 değerleri (C3), tek İHA'da yön seçimi, iki İHA'da çakışma çözümü, sıfır uzunluklu görev (h1 #9), kapasite sınırı, yakınsama üst sınırı, DMG'nin deneysel kontrolü | `pytest` geçiyor; h1'in birimi belirsiz olduğu için yalnızca mantık testi (CLAUDE.md §12) |
| **A3** AC300'de D1 ve makaleyle karşılaştırma | 300 ortamın hepsi; D1–D3 (C7) | Sonuçlar ve makaledeki değerler yan yana tabloda; fark yorumlanmış |
| **A4** Enerji modeli | Zeng vd. 2019 döner kanatlı İHA güç modeli; Rodrigues vd. 2021 uçuş/enerji verisiyle kontrol | Model + veriyle hata analizi. **Sınırlılık:** Rodrigues verisindeki araç x500 değil (kullanıcı notu); aracın modeli ve özellikleri Rodrigues 2021 metninden **doğrulanacak**. İki kaynak henüz okunmadı; parametreler A4 planında, kaynaklarıyla yazılacak. |
| **A5** Dayanıklılık | Paket kaybı, İHA arızası sonrası yeniden atama, lider kaybı (D4, D5) | Makalede olmayan katkı: yazarlar bunları gelecek çalışma olarak belirtiyor [G §VI] |
| **A6** Gazebo entegrasyonu | CBBA çıktısı → A0 arayüzü → uçuş (D6) | 5 İHA (ya da WSL yetmezse 2/4) ile AC10_0000 üzerinde gösterim |

## C6. Dosyalar ve mevcut kodla bağlantı

**Yeni (`swarm_core/`, Gazebo/MAVSDK/arayüz bağımlılığı yok):**

| Dosya | İçerik | Kaynak |
|---|---|---|
| `swarm_core/motion.py` | `ramp_time(d, v_max, a_max)` | G Eq. 7 |
| `swarm_core/scoring.py` | Yol süresi `τ` ve puan `S` (yönlü yollar için); nokta puanlama (karşılaştırma için) | G Eq. 6, §V-A |
| `swarm_core/cbba.py` | `CbbaAgent`: demet/yol, yönlü marjinal puan, kapasite kontrolü, uzlaşma kuralları | G Eq. 1, 2, 8; Choi 2009 |
| `swarm_core/network.py` | Mesaj geçişi: tam bağlı, senkron turlar; A5'te paket kaybı ve İHA düşürme | G §V; A5 |
| `swarm_core/allocation.py` | `run_cbba(tasks, uavs, params) → Allocation` (atama, yönler, iterasyon sayısı) | — |
| `swarm_core/params.py` | Deney parametreleri (λ, v_max, a_max, kapasiteler, ω), her biri kaynağıyla | C4 |
| `tests/test_motion.py`, `test_scoring.py`, `test_cbba.py` | A2 | — |
| `experiments/` (repo içinde, `swarm_core` dışında) | D1–D5 çalıştırıcıları ve sonuç tabloları | — |

**Mevcut koddan kullanılacaklar:**
- `swarm_core/dataset.py`: `load_tasks()` (görev kimliği, `waypoints = [u0, u1]`), `load_boundary()` (depot üretimi için), `load_obstacles()`. Değişmez.
- `swarm_core/models.py`: `Task` olduğu gibi kullanılır. `UAV` başlangıç konumu (`x, y`) için kullanılır.
  - `UAV.battery` ve `UAV.is_leader` A4/A5'e kadar kullanılmaz; silinmez (kural 3).
  - CBBA'nın iç durumu (demet, yol, kazanan listeleri) `models.py`'ye eklenmez; `cbba.py` içinde ayrı tutulur.
- `swarm_core/tasks.py` ve `coverage.py` (eski 20 bölgelik örnek): CBBA kullanmaz. **Legacy** olarak işaretlenecek (kural 3); testleri kalır.

**CBBA çıktısının A0 arayüzüne bağlanması:**
```text
swarm_core.allocation.run_cbba(...)  →  Allocation(assignment={1: [5, 2, 9], 2: [...]}, reversed={1: [False, True, False], ...})
                                       │  (saf Python, ağ yok)
swarm_sim/ (ör. cbba_mission.py)      →  mission_events.send_assignment(assignment, source="cbba", reversed=...)
                                       ▼
A0 2D harita / Gazebo işaretçileri    →  aynı kod; panelde "CBBA" etiketi
```
- ⚠️ **A0 arayüzüne eklenmesi önerilen alan — karar gerekli (K9):** `assignment` mesajında yön bilgisi yok. CBBA her görev için yön seçtiği için, planlanan rotanın çizilmesi ve uçuş için `reversed` (isteğe bağlı, İHA başına bool listesi; yoksa hepsi `false`) alanı eklenmeli. Bu, A0 kodlanmadan önce karara bağlanmalı. Böylece CBBA eklendiğinde görselleştirme kodu yine değişmez.

## C7. Deneyler ve İHA sayıları

**Alınan kararlar** (kullanıcı, 24 Kasım 2026):
1. **Python deneyleri (D1–D5)** makaledeki İHA sayıları ve kapasitelerle yapılır.
   - **Gerekçe:** D1, makaleyle doğrudan karşılaştırmadır; aynı koşullar olmadan karşılaştırma anlamsız olur.
   - **Değerler:** D1: 2 İHA × 1200 s. Ölçeklenebilirlik: 2/4/6/8/10/12/14 İHA × 1500/750/600/500 s. [G §V, Fig. 4]
2. **Gazebo gösterimi (D6):** proje tanımındaki **5 İHA**, İHA başına **600 s**.
   - **MAKALEDE YOK – temkinli seçim:** Makale 5 İHA için kapasite vermiyor. 5'e en yakın iki değer 4 İHA (750 s) ve 6 İHA (600 s); daha kısıtlayıcı olan 600 s seçildi.
   - WSL performansı yetmezse D6, 2 veya 4 İHA ile yapılır ve sınırlılık olarak yazılır.
3. **λ = 0,95** (makale metni), trajallocpy'deki 0,99 değil. **Gerekçe:** karşılaştırma makaledeki sonuçlarla yapılıyor.

**Deneylerin tanımı (öneri):**

| Deney | Soru | Koşullar | Makaledeki karşılığı |
|---|---|---|---|
| D1 | Bizim uygulamamız makaledeki sonuca ulaşıyor mu? | 2 İHA × 1200 s, 300 ortam; yörünge ve nokta puanlama | Toplam 554.920 s; %6 iyileşme; merkezi ile %1,9 fark [G §V, §V-A] |
| D2 | Ölçeklenebilirlik | 2–14 İHA (2'şer), kapasiteler C4 | Ortalama en uzun süre 972 → 229 s [G Fig. 4] |
| D3 | Yakınsama | D2 ile aynı | İterasyon sayısı [G Fig. 5] |
| D4 | Paket kaybı | D1 koşulları + kayıp oranları (K7) | Makalede yok (katkı) |
| D5 | İHA arızası, yeniden atama, lider kaybı | D1/D2 koşulları + olaylar (K7, K8) | Makalede yok (katkı) |
| D6 | Gazebo gösterimi | AC10_0000, 5 İHA × 600 s | Makalede yok |

**Not:** Merkezi yöntemi (Agarwal & Akella 2022) çalıştırmıyoruz. D1'de bizim sonucumuz makalenin **yayımladığı** merkezi değerle (544.592 s) karşılaştırılır.

## C8. "MAKALEDE YOK" maddeleri: öneriler (onay bekliyor)

| # | Konu | Öneri | Gerekçe |
|---|---|---|---|
| K1 | Uzlaşma eylem kuralları (güncelle/sıfırla/bırak), eşit tekliflerde kazanan | Choi 2009'daki tablo **aynen** uygulanır. Choi 2009 PDF'i `~/makaleler/`'e eklenir ve A1'den önce okunur. Tablo bulunana kadar uzlaşma kodu yazılmaz. | Grøntved bu kısmı doğrudan Choi 2009'a bırakıyor [G §III]. Tahminle yazılırsa yakınsama garantisi bozulabilir. |
| K2 | Rampa şeridin kendisine de uygulanıyor mu? `τ_ij` şeridin başına mı sonuna mı varış? | Her ayak ayrı ayrı Eq. 7 ile hesaplanır: geçiş ayağı (önceki çıkış → giriş) ve şerit ayağı (giriş → çıkış), aralarda tam duruş. `τ_ij` = **giriş noktasına varış** süresi. Kapasite kontrolü = son görevin **çıkışına** kadar toplam süre. | Makale "görevler arasında tam duruş" diyor [G §IV-A] ve `τ_ij`'yi "göreve varış süresi" olarak tanımlıyor [G Eq. 6]. Yön kuralı da uçlara varış süresini karşılaştırıyor [G §IV-A]. Bizim uçuş kodumuz da her ayakta duruyor (`fly_task.py`). |
| K3 | Ödül `c̄_j` değeri | `c̄_j = 1` (bütün görevler) | Makale ödülü sabit tutuyor [G §IV-A]. Sabit bir çarpan teklif sıralamasını değiştirmez. |
| K4 | Depot nasıl rastgele seçiliyor, kaç tekrar? | Alan poligonu içinde, engel dışında, düzgün dağılımlı; ortam başına sabit tohum (ortam adından türetilmiş). D1'de ortam başına **1** depot (makaledeki gibi tek toplam). Ek olarak 5 tohumla duyarlılık analizi. | Makale "rastgele ve ortak" diyor ama dağılım vermiyor [G §V-A]. Tek depot makalenin raporlama biçimine uyuyor; tohum sabitlemek tekrarlanabilirlik sağlar. |
| K5 | `ω = 15`'in tanımı | Turner vd. 2017 [26] okunup tanım oradan alınır. O zamana kadar `ω` kullanılmaz; yakınsama, Choi 2009'un üst sınırı (C2.1) ve bir iterasyon tavanıyla izlenir. İzlenen değer "test ayarı" olarak işaretlenir. | Grøntved yalnızca değeri ve amacını veriyor [G §V]. |
| K6 | Senkron mu asenkron mu, iterasyon nasıl sayılıyor? | Senkron turlar: her turda bütün İHA'lar demet oluşturur, sonra mesaj alışverişi yapar. 1 tur = 1 iterasyon. Choi 2009'dan doğrulanacak. | Asenkron CBBA ayrı bir çalışma olarak anılıyor (Johnson vd. 2011 [23]); bu, temel CBBA'nın senkron olduğunu düşündürüyor, ama doğrulanmadı. |
| K7 | D4 paket kaybı oranları, tekrar sayısı | Mesaj başına bağımsız kayıp: %0, 10, 20, 30, 50; oran başına 10 tohum; metrik: yakınsama turu, çakışma sayısı, toplam süre artışı | Makalede yok (katkı). Aralık, kayıpsızdan ağır kayba kadar eğilimi göstermek için; kesin değerler literatürden ayrıca gerekçelendirilebilir. |
| K8 | "Lider" nedir? (CBBA lider gerektirmez) | Lider yalnızca **izleme/raporlama** rolü: atamayı toplayıp operatöre (A0 paneli) iletir. Atama kararı vermez. Lider kaybında yeni lider seçimi en küçük canlı İHA kimliğiyle yapılır; D5'te atamanın lider kaybından **etkilenmediği** gösterilir. | CBBA tam dağıtıktır [G §III]. Projenin "lider seçimi" hedefi (CLAUDE.md §1) atama mantığını merkezileştirmemeli. |
| K9 | A0 arayüzünde yön bilgisi | `assignment` mesajına isteğe bağlı `reversed` alanı (C6) | CBBA yön seçiyor [G Eq. 8]; görselleştirme kodu CBBA'da değişmemeli (A0.0.5). |
| K10 | Eq. 8 ile DMG korunuyor mu? | A2'de rastgele küçük örneklerle Eq. 5'in sağlanıp sağlanmadığı test edilir. Bozuluyorsa sonuçlarda sınırlılık olarak yazılır. | Makale bunu göstermiyor; CBBA garantileri DMG'ye bağlı [G §IV-A]. |
| K11 | Görev 0 uzunluklu (`u0 = u1`) | Nokta görev gibi işlenir: şerit ayağı 0 s, yön seçimi yok | Makale özel durumu anıyor [G §IV]; CLAUDE.md §12 kararı. |
| K12 | Kapasiteye dönüş (depot'a geri) dahil mi? | Dahil **değil**: kapasite = son görevin çıkışına kadar süre | Makale yalnızca "yol maliyetlerinin toplamı" diyor [G §V] ve geri dönüşten söz etmiyor. Merkezi yöntemin [11] dönüşü sayıp saymadığı bilinmiyor → D1 karşılaştırmasında sınırlılık olarak not edilir. |

## C9. Kaynak notları

- **Yazar adı farkı:** Makale PDF'inde yazarlar "Kasper A. R. Grøntved, **Ulrik P. S. Lundquist**, Anders Lyhne Christensen". CoverageTasks README'sindeki BibTeX'te "Schultz, Ulrik Pagh". `scenarios/README.md` ve CLAUDE.md §12'de "Schultz" yazıyor. Kaynakçada yayımlanmış sürümdeki (IEEE) ad kullanılmalı; kontrol edilip düzeltilecek.
- Makalenin elimizdeki sürümü yazarların kabul edilmiş son taslağı ("Accepted manuscript", SDU Research Portal). Sayfa ve denklem numaraları buna göre.
