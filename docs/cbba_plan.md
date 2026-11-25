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
- `reversed` (**isteğe bağlı**, K9 kararı): İHA kimliği → `assignment` ile aynı uzunlukta bool listesi. `true` olan görev veri setindeki yönün **tersine** uçulur (`u1 → u0`). Alan yoksa bütün görevler veri setindeki yönde uçulur (`false`). Manuel atamada (`fly_task.py`) şimdilik hep `false`; CBBA her görevin yönünü seçtiği için doldurur (CBBA bölümü, C1). Harita planlanan rotayı ve şeridin giriş ucunu bu alana göre çizer.

  ```json
  "reversed": { "1": [false, true, false, false], "2": [] }
  ```
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

> Durum: **K1 (Choi 2009 PDF'iyle doğrulama) ve K16 (İHA arıza olasılığı, aday) dışında kararlar alındı.** K7 25 Kasım 2026'da kaynaklarıyla onaylandı. CBBA kodu henüz yazılmadı.

**Kaynaklar ve kısaltmalar:**
- **[G §V-A], [G Eq. 7]** = Grøntved, Lundquist, Christensen, "Decentralized Multi-UAV Trajectory Task Allocation in Search and Rescue Applications", ICAR 2023, DOI 10.1109/icar58858.2023.10406912. Yazarların kabul edilmiş son taslağı, 8 sayfa; `~/makaleler/Grontved2023.pdf` (repoda değil).
- **[T23 dosya:satır]** = yazarların açık kaynak uygulaması **trajallocpy**, makale dönemi sürümü: commit `13b7bb3` (4 Temmuz 2023, "tag"). Bu commit makaledeki Fig. 3, 4 ve 5'in dosyalarını ekliyor. `~/makaleler/trajallocpy_2023/` (salt okunur kopya, repoda değil).
- **[T-HEAD dosya:satır]** = trajallocpy güncel sürüm, commit `d3932cf` (16 Mayıs 2026). Son commit'te "Fix CBBA correctness, add hard time windows" yazıyor, yani algoritma makaleden sonra değişmiş. **Bu yüzden referans olarak T23 kullanılır**; T-HEAD yalnızca karşılaştırma için anılır.
- **[Choi 2009]** = Choi, Brunet, How, IEEE T-RO 25(4), 2009 (= makalenin [13] numaralı kaynağı). ⚠️ **PDF indirilemedi:** MIT DSpace hem sayfada hem dosya adresinde "HTTP 429 Too Many Requests" verdi. Choi'ye dayanan maddeler şimdilik Grøntved'in özetine ve T23'teki uygulamaya göre yazıldı ("Choi 2009 → G/T23 üzerinden").
- **Etiketler:** "MAKALEDE YOK" = makalede bulunamadı. Kodda bulunduysa kaynak T23 gösterilir; bulunamadıysa "karar gerekli" yazılır.

## C1. Problem tanımı

- Arama alanı, engelleri de içeren bir poligondur ve önceden **tarama şeritlerine (doğru parçaları)** bölünmüştür. Alanı taramak için her şerit bir İHA tarafından bir kez uçulmalıdır. Her İHA'ya birden çok şerit verildiği için problem çok-atamalıdır (multi-assignment). [G §IV]
- **Görev = iki uçlu tarama şeridi:** `j ≜ {u0, u1}` (giriş ve çıkış noktası). [G Eq. 4] Kodda `TrajectoryTask(start, end, trajectory)`. [T23 Task.py:8-23]
  - Nokta görevden farkı: görev bitince İHA diğer uçtadır. Bu yüzden görevler arası maliyet hem giriş hem çıkış noktasına bağlıdır. [G §IV]
  - `u0 = u1` özel durumu makalede anılıyor [G §IV]. h1.json'daki 9. görev buna örnek; nokta görev gibi işlenir (K11).
- **Yön seçimi:** Her şerit iki yönde uçulabilir. İHA, demetine şerit eklerken puanı en çok artıran yönü seçer. [G §IV-A, Eq. 8] Kodda görev yerel kopyada ters çevrilir. [T23 CBBA.py:264-266, Task.py:19-23]
  - Yön ve yol sırası diğer İHA'lara **gönderilmez**; yalnızca kazanan teklifler, kazanan İHA'lar ve zaman damgaları gönderilir. [G §IV-A; T23 CBBA.py:101-102]
- **Amaç:** tarama süresini en aza indirmek [G §IV]. Bu, zamana göre indirimli ödülün toplamını en büyüklemek olarak modellenir. [G Eq. 6]
- **Kapasite `L_t`** = azami uçuş süresi (saniye). [G §V] ⚠️ Orijinal CBBA'da `L_t` görev sayısıdır [G §III]. Kodda bu iki anlam karışmasın diye `capacity_s` adı kullanılacak.
  - **Kapasiteye neler girer:** depot'tan ilk göreve gidiş + görevler arası geçişler + her şeridin kendi uçuşu + **depot'a dönüş**. [T23 CBBA.py:107-118] Makale yalnızca "yol maliyetlerinin toplamı aşılamaz" diyor. [G §V]
- **Depot:** Her problemde rastgele seçilir ve bütün İHA'lar için ortaktır. [G §V-A] Nasıl seçildiği kodda: K4.

## C2. CBBA'nın iki aşaması

CBBA iki aşamayı dönüşümlü olarak tekrarlar: (i) **demet oluşturma**, (ii) **çakışma çözümü / uzlaşma**. Çakışmasız bir atama elde edilene kadar sürer. [G §III; Choi 2009 → G]

### C2.1 Choi 2009'dan gelenler (orijinal CBBA)

- Her İHA iki liste tutar:
  - **Demet `b_i`:** görevler eklenme sırasıyla.
  - **Yol `p_i`:** aynı görevler, puanı en çok artıran uçuş sırasıyla. [G §III; T23 CBBA.py:48-51]
- **Marjinal puan:** `c_ij[b_i] = 0` eğer `j ∈ b_i`; aksi halde `max_{n≤|p_i|} S_i^{p_i ⊕n {j}} − S_i^{p_i}`. [G Eq. 1]
- **Güncelleme:** `b_i = b_i ⊕end {J_i}`, `p_i = p_i ⊕_{n_i,J_i} {J_i}`. [G Eq. 2; T23 CBBA.py:252-272]
  - Kodda bir görev ancak teklifi, İHA'nın o görev için bildiği en yüksek tekliften büyükse eklenebilir. [T23 CBBA.py:255-260]
- **Azalan marjinal kazanç (DMG):** `c_ij[b_i] ≥ c_ij[b_i ⊕end b]`. [G Eq. 5]
- **Uzlaşma:** Her İHA kazanan teklifleri (`y`), kazanan İHA'ları (`z`) ve zaman damgalarını (`s`) gönderir. Çakışmalar yerel eylem kurallarıyla çözülür. [G §III → Choi 2009]
  - Kodda **17 kural** (güncelle / sıfırla / bırak) olarak uygulanmış. [T23 CBBA.py:274-404]
  - **Eşit tekliflerde küçük kimlikli İHA kazanır.** [T23 CBBA.py:308-310, 321, 354, 374-376]
  - ⚠️ K1 kararı "Choi 2009 tablosu aynen" olduğu için kurallar Choi PDF'iyle satır satır karşılaştırılacak. O zamana kadar T23 geçici referans.
- **Teklif kaybedilince:** Demette kaybedilen ilk görevden (`n̄`) sonraki görevler de çıkarılır. [G §III; T23 CBBA.py:406-427]
- **Karmaşıklık** `O(N_t·L_t)` [G Eq. 3]. **Yakınsama sınırı** `max{N_t, L_t·N_u}·D` [G §III]. %50 optimallik garantisi [G §III].

### C2.2 Grøntved 2023'ün katkısı (yörünge görevleri)

- **Yönlü marjinal puan:** `c_ij[b_i] = max_n max_dir S_i^{p_i ⊕n {j_dir}} − S_i^{p_i}`. [G Eq. 8]
- **Yön değiştirme kuralı:** `τ(p_{u1}) < τ(p_{u0})` ise `u0` ile `u1` yer değiştirir. [G §IV-A]
  - Kodda: eklenen görevin yalnızca **kendinden önceki** görevin çıkışına göre iki ucu karşılaştırılır; daha erken varılan uç giriş olur. [T23 CBBA.py:169-178, 198-205]
  - Görev yolun **başına** (n = 0) ekleniyorsa yön değerlendirilmez. [T23 CBBA.py:186, 199]
  - Sonraki görevle bağlantı yön seçiminde hesaba katılmaz.
  - Yani makaledeki "her yön için en büyük" ifadesinin kodda daraltılmış bir uygulaması var (K14).
- **İlk görev** eklenirken puan başlangıç konumuna göre hesaplanır. [G §IV-A; T23 CBBA.py:186]
- **Sınırlılık:** Makale, Eq. 8 ile DMG'nin korunduğunu kanıtlamıyor. A2'de deneysel olarak test edilecek (K10).

## C3. Puan fonksiyonu ve maliyet modeli

**Zamana göre indirimli ödül:**
```text
S_i^{p_i} = Σ_{j ∈ p_i}  λ^{τ_ij(p_i)} · c̄_j                                    (G Eq. 6)
```
- `τ_ij`: göreve varış süresi tahmini [G Eq. 6].
- `c̄_j`: sabit ödül, kodda `reward = 1` [T23 Task.py:13].
- `λ = 0.95` [G §V; T23 CBBA.py:69].

**Hız rampası** (görevler arasında tam duruş):
```text
             ⎧ sqrt( 4·d / a_max ),            d <  d_a
  τ(d)  =    ⎨                                                 d_a = v_max² / a_max      (G Eq. 7)
             ⎩ d / v_max  +  v_max / a_max,    d ≥ d_a
```
- Kodda birebir aynı. [T23 CBBA.py:149-151]
- `v_max = 3 m/s`, `a_max = 1 m/s²` ⇒ `d_a = 9 m`. [G §V; T23 CBBA.py:38-39]
- Kaynağı Bähnemann vd. 2021 [8] ve Agarwal & Akella 2022 [11]. [G §IV-A]
- Kontrol değerleri (A2 birim testi): `d = 4,5 m` → `4,243 s`; `d = 20 m` → `9,667 s`.

**Kodda netleşen ayrıntılar** (makale yazmıyor):

| Konu | trajallocpy (T23) | Karar |
|---|---|---|
| **Mesafe `d`** | Düz çizgi değil. **Engellerden kaçınan en kısa yol** (görünürlük grafiği, `extremitypathfinder` kütüphanesi). [T23 CBBA.py:139-141, CoverageProblem.py:27-50] | K13 |
| **Engel ve sınır ölçeği** | Yol planlamasında engeller merkezlerine göre **%95'e küçültülüyor**, alan sınırı **%101'e büyütülüyor**. [T23 main.py:71-80] Şeritler engel kenarlarında olduğu için (A0.2) bu gerekli. | K13 |
| **Rampa nerede uygulanıyor** | Her ayak ayrı: depot → ilk giriş, her geçiş (çıkış → sonraki giriş), her şeridin kendisi (giriş → çıkış), son çıkış → depot. [T23 CBBA.py:107-118] | K2 ✅ |
| **`τ_ij` neyi içeriyor** | Puan hesabında **yalnızca geçiş süreleri** toplanıyor; şeritlerin kendi uçuş süreleri `τ`'ya eklenmiyor. [T23 CBBA.py:181-211] | K2 (kod esas) |
| **Puanda depot'a dönüş** | Yeni görevli yolun puanına depot'a dönüş için bir terim daha ekleniyor [T23 CBBA.py:213-218], mevcut yolun puanında ise bu terim yer almıyor [T23 CBBA.py:159-167]. Marjinal puan bu iki hesabın farkı olduğu için terim yalnızca bir tarafta kalıyor. | K14 |
| **Kapasite kontrolü** | Kapasite, görev **eklenmeden önce** kontrol ediliyor [T23 CBBA.py:253]; son eklenen görevle rota kapasiteyi biraz geçebiliyor. Sonuç dosyasında gözlemlenen: 2 İHA × 1500 s dosyasında en uzun rota 1507,6 s. | K14 |

**Nokta görev karşılaştırması** (makaledeki %6 sonucu):
- Makale: "giriş noktasına Öklid uzaklığı". [G §V-A]
- Kod: aynı rampa ve görünürlük grafiği maliyeti kullanılıyor, yön optimizasyonu kapatılıyor (`use_single_point_estimation`). [T23 CBBA.py:192-196]
- ⚠️ T23'te komut satırındaki `--point_estimation` seçeneği okunuyor ama algoritmaya **iletilmiyor** [T23 main.py:134, 84-85]. Bu sürümle %6 deneyinin nasıl çalıştırıldığı belirsiz.

## C4. Parametre tablosu

| Parametre | Değer | Kaynak | Not |
|---|---|---|---|
| `λ` | **0,95** | [G §V]; [T23 CBBA.py:69] | **Karar: 0,95.** Güncel kodda 0,99 [T-HEAD trajallocpy/CBBA.py:86]. 0,99'a geçiş makaleden sonra, commit `7fdad3d` (15 Ağu 2024, "fixed floatingpoint error"). Makale dönemi kodu metinle aynı (0,95). |
| `v_max` | 3 m/s | [G §V]; [T23 CBBA.py:38] | Simülasyonda ölçülen 3,13 m/s (CLAUDE.md §13) |
| `a_max` | 1 m/s² | [G §V]; [T23 CBBA.py:39] | |
| `d_a` | 9 m | [G Eq. 7] türetilmiş | |
| `c̄_j` | 1 | [G §IV-A] "sabit"; [T23 Task.py:13] | K3 ✅ |
| `ω` (azami atama çarpanı) | 15 | [G §V] → Turner 2017; [T23 CBBA.py:72] `removal_threshold = 15` | Tanım koddan (K5 ✅) |
| Kapasite (D1) | 2 İHA × **1200 s** | [G §V, §V-A, Fig. 2–3] | ⚠️ Yazarların sonuç dosyalarında farklı değerler gözlemlendi (C10) |
| Kapasite (ölçeklenebilirlik) | 2: 1500 · 4: 750 · 6: 600 · 8/10/12/14: 500 s | [G Fig. 4–5] | ⚠️ İHA sayıları 2'şer adımla. Deney betiğinde farklı değerler gözlemlendi (C10) |
| Ağ | Tam bağlı | [G §V]; [T23 Experiment.py:27] | |
| Depot | Rastgele, ortak | [G §V-A]; [T23 main.py:83-84, CoverageProblem.py:69-74] | K4 ✅ |
| Veri seti | AC300: 300 ortam, 10.000 m², 0–15 engel, 35–161 görev | [G §V] | |
| Sensör | "3 m² field-of-view" | [G §V] | CoverageTasks README'si "3 m sweep width" diyor |

## C5. Aşamalar

| Aşama | İçerik | Bitti sayılma koşulu |
|---|---|---|
| **A1** CBBA çekirdeği | `swarm_core`: rampa, görünürlük grafiğiyle mesafe (K13), puan, yönlü demet, 17 kurallı uzlaşma, senkron ağ simülasyonu | Çakışmasız atama; `swarm_core` Gazebo/MAVSDK/arayüzden bağımsız |
| **A2** h1 ile birim testler | Eq. 7 değerleri, yön seçimi, eşit teklif (küçük kimlik kazanır), demet kesme (`n̄`), `ω` eşiği, kapasite, sıfır uzunluklu görev, DMG kontrolü, yakınsama sınırı | `pytest` geçiyor (h1 birimsiz; yalnızca mantık testi) |
| **A3** AC300'de D1–D3 | Hem makale metnindeki değerlerle hem yazarların sonuç dosyalarından hesaplanan değerlerle karşılaştırma (C10) | C10'daki tablonun bizim sonuçlarımızla dolu hali |
| **A4** Enerji modeli | Zeng vd. 2019 güç modeli; Rodrigues vd. 2021 verisiyle kontrol | **Sınırlılık:** Rodrigues verisindeki araç x500 değil (kullanıcı notu); model adı ve özellikleri Rodrigues 2021'den doğrulanacak. İki kaynak henüz okunmadı. |
| **A5** Dayanıklılık | Paket kaybı (D4), İHA arızası ve yeniden atama, lider kaybı (D5) | Makalede gelecek çalışma olarak geçiyor [G §VI] |
| **A6** Gazebo | CBBA → A0 arayüzü (`source: "cbba"`, `reversed`) → uçuş (D6) | 5 İHA (WSL yetmezse 2 veya 4) |

## C6. Dosyalar ve mevcut kodla bağlantı

**Yeni (`swarm_core/`, Gazebo/MAVSDK/arayüz bağımlılığı yok):**

| Dosya | İçerik | Kaynak |
|---|---|---|
| `swarm_core/motion.py` | `ramp_time(d, v_max, a_max)` | G Eq. 7; T23 CBBA.py:149-151 |
| `swarm_core/environment.py` | Engellerden kaçınan en kısa yol (K13); engel %95, sınır %101 ölçeği | T23 CoverageProblem.py, main.py:71-80 |
| `swarm_core/scoring.py` | Yol süresi, puan, kapasite maliyeti; nokta puanlama modu | G Eq. 6; T23 CBBA.py:107-219 |
| `swarm_core/cbba.py` | `CbbaAgent`: demet/yol, yönlü teklif, 17 kural, `ω` sayacı | G Eq. 1, 2, 8; T23 CBBA.py; Choi 2009 |
| `swarm_core/network.py` | Senkron turlar, tam bağlı; A5'te paket kaybı ve İHA düşürme | T23 Experiment.py:102-157 |
| `swarm_core/allocation.py` | `run_cbba(...) → Allocation(assignment, reversed, iterations, costs)` | — |
| `swarm_core/params.py` | Deney parametreleri, her biri kaynağıyla | C4 |
| `tests/test_motion.py`, `test_scoring.py`, `test_cbba.py` | A2 | — |
| `experiments/` (repo içinde, `swarm_core` dışında) | D1–D5 çalıştırıcıları ve sonuç tabloları | — |

**Mevcut koddan kullanılacaklar:**
- `swarm_core/dataset.py` (`load_tasks`, `load_boundary`, `load_obstacles`) değişmez.
- `swarm_core/models.py`: `Task` ve `UAV` (başlangıç konumu) kullanılır. `UAV.battery` ve `UAV.is_leader` silinmez. CBBA'nın iç durumu `cbba.py` içinde tutulur.
- `swarm_core/tasks.py` ve `coverage.py`: CBBA kullanmaz; legacy olarak işaretlenecek (kural 3).

**A0 arayüzüne bağlantı:**
```text
swarm_core.allocation.run_cbba(...) → Allocation(assignment={1: [5, 2, 9]}, reversed={1: [False, True, False]})
swarm_sim/cbba_mission.py           → mission_events.send_assignment(assignment, reversed=..., source="cbba")
A0 harita / Gazebo işaretçileri      → aynı kod; panelde "CBBA"
```
`reversed` alanı A0.0.5'e eklendi (K9 ✅).

## C7. Deneyler ve İHA sayıları

**Alınan kararlar** (kullanıcı, 24 Kasım 2026):
1. **Python deneyleri (D1–D5)** makaledeki İHA sayıları ve kapasitelerle yapılır. **Gerekçe:** D1 makaleyle karşılaştırmadır.
   - D1: 2 İHA × 1200 s.
   - Ölçeklenebilirlik: 2/4/6/8/10/12/14 İHA × 1500/750/600/500 s [G §V, Fig. 4]. (Gözlemlenen farklar: C10.)
2. **D6 (Gazebo):** 5 İHA × 600 s. **MAKALEDE YOK – temkinli seçim:** 5 İHA için kapasite yok; 4 İHA (750 s) ile 6 İHA (600 s) arasından daha kısıtlayıcı olan seçildi. WSL yetmezse 2 veya 4 İHA ile yapılır ve sınırlılık olarak yazılır.
3. **λ = 0,95.**

| Deney | Soru | Koşullar | Makaledeki karşılığı |
|---|---|---|---|
| D1 | Bizim uygulamamız makaledeki sonuca ulaşıyor mu? | 2 İHA × 1200 s (+ K15: 1500 s), 300 ortam; yörünge ve nokta puanlama; `paper_compat` modu | İki ayrı karşılaştırma (C10): (1) makale metnindeki değerler: 554.920 s, %6, %1,9; (2) yazarların sonuç dosyalarından hesaplanan değerler, ortam ortam |
| D2 | Ölçeklenebilirlik | 2–14 İHA, 2'şer adım | 972 → 229 s [G Fig. 4] |
| D3 | Yakınsama | D2 ile aynı | [G Fig. 5] |
| D4 | Paket kaybı | D1 koşulları + K7 | Makalede yok (katkı) |
| D5 | İHA arızası, yeniden atama, lider kaybı | D1/D2 + olaylar (K8, K16) | Makalede yok (katkı) |
| D6 | Gazebo gösterimi | AC10_0000, 5 İHA × 600 s | Makalede yok |

## C8. "MAKALEDE YOK" maddeleri — kararlar ve trajallocpy karşılaştırması

| # | Konu | Durum | Karar ve kaynak |
|---|---|---|---|
| K1 | Uzlaşma kuralları, eşit teklif | ✅ Karar: Choi 2009 tablosu aynen. ⏳ PDF bekleniyor (MIT 429). | Geçici referans: 17 kural [T23 CBBA.py:274-404]; eşitlikte küçük kimlik [T23 CBBA.py:308-310]. Choi PDF'iyle karşılaştırılmadan uzlaşma kodu "tamamlandı" sayılmaz. |
| K2 | Rampa nerede, `τ` neyi içeriyor | ✅ Kod esas | Her ayak ayrı rampa [T23 CBBA.py:107-118] — **önerimle aynı**. `τ_ij` = yalnızca birikmiş **geçiş** süreleri, şerit süreleri hariç [T23 CBBA.py:181-211] — **önerimden farklı** (ben şerit sürelerinin de dahil olmasını önermiştim). Kapasitede şerit süreleri dahil. |
| K3 | `c̄_j` | ✅ | 1 [T23 Task.py:13] — önerimle aynı. |
| K4 | Depot | ✅ Kod esas | Sınır kutusunda düzgün dağılım; alan dışı ve engel içi noktalar reddediliyor [T23 CoverageProblem.py:69-74]. Ortam başına 1 depot, bütün İHA'lar için ortak [T23 main.py:83-84]. Tohum: bütün çalışma için tek tohum, `random.seed(1352323)` [T23 main.py:126-128]; ortamlar sırayla aynı rastgele diziden. **Önerimden farkı:** ben ortam başına ayrı tohum önermiştim. D1 kodu taklit eder. 5 tohumlu duyarlılık analizi ek olarak kalır (test ayarı). |
| K5 | `ω = 15` tanımı | ✅ Koddan | Bir İHA bir görevi demetinden ilk kaybedilen görev olarak `ω`'dan fazla kez kaybederse, o görev için artık teklif vermez [T23 CBBA.py:72, 238, 421-423]. Turner 2017 gerekmedi; tanım Turner'la ayrıca karşılaştırılmadı. **Önerimden farklı:** ben `ω`'yu kullanmamayı önermiştim. |
| K6 | Senkron/asenkron, iterasyon | ✅ | Senkron: her turda bütün İHA'lar demet oluşturur → mesajlar toplanır → bütün İHA'lar uzlaşır. 1 tur = 1 iterasyon. Bütün İHA'lar o turda hiç görev kaybetmediyse yakınsamış sayılır [T23 Experiment.py:102-157, CBBA.py:431-436]. **Önerimle aynı.** |
| K7 | Paket kaybı oranları | ✅ **Onaylandı (25 Kasım 2026)** | **%0** (temel durum), **%10, %30** [Aznar 2026 §5.1, §6.4.2], **%50** [Liu 2026 §VI-F-1]. Metinden doğrulandı: Aznar 2026'da temel durum paket kaybı %0 (parametre tablosu, "Packet Loss Probability 0%"); senaryolar "probabilistic packet loss set at 10% and 30%, which also included bandwidth limitations" (§5.1) ve "packet loss (10% and 30%, with bandwidth limits)" (§6.4.2). Liu 2026'da "each delivery of a broadcast to one in-range receiver is dropped independently with probability p ∈ {0.1, 0.3, 0.5}" (§VI-F-1); sonuçlar %30 ve %50 için ayrıca verilmiş. **Kayıp modeli:** Liu 2026'daki tanım alınır: her mesajın her alıcıya teslimi bağımsız olarak `p` olasılıkla düşer. Aznar 2026 kaybı yalnızca "bir mesajın kaybolma olasılığı" olarak tanımlıyor ve bant genişliği sınırıyla birlikte uyguluyor; bant sınırı bizim deneyimizde **yok**, bu fark raporda belirtilir. **Bağlam farkı (sınırlılık):** iki çalışma da Grøntved'in senaryosundan farklı (Aznar: 20 yer robotu, SimPy, 3000 s, olay tetiklemeli CBBA; Liu: 10 İHA, 30 görev, 250 m iletişim yarıçapı, çevrimiçi atama). Oranlar "literatürde CBBA türevlerinde denenmiş kayıp düzeyleri" olarak alınır, sonuçlar doğrudan karşılaştırılmaz. Oran başına 10 tohum: **test ayarı.** Sao vd. 2025 bu karar için kaynak değil (paket kaybı deneyi yok); ilgili çalışma olarak C9'da. |
| K8 | Lider | ✅ | Yalnızca izleme/raporlama; atama kararı vermez. Kayıpta en küçük kimlikli canlı İHA lider olur; D5'te atamanın etkilenmediği gösterilir. |
| K9 | Yön bilgisi | ✅ | `reversed` alanı A0.0.5'e eklendi. |
| K10 | DMG | ✅ | A2'de deneysel test; bozuluyorsa sınırlılık. |
| K11 | Sıfır uzunluklu görev | ✅ | Nokta görev gibi. |
| K12 | Depot'a dönüş kapasitede mi | ✅ Kod esas | **Dahil** [T23 CBBA.py:116-117]; raporlanan rota maliyetlerinde de dahil [T23 Experiment.py:43]. **Önerimden farklı** (ben dahil değil demiştim). |
| **K13** | Mesafe nasıl hesaplanacak | ✅ **Onaylandı** | Engellerden kaçınan en kısa yol, yazarlar gibi `extremitypathfinder` ile (pip; lisansı kurulumda kontrol edilecek). Engel %95 ve sınır %101 ölçeği de taklit edilir. **Gerekçe:** D1 karşılaştırması aynı maliyet modelini gerektirir. Alternatif: shapely + networkx ile kendi görünürlük grafiğimiz (daha çok iş, aynı sonucu verdiği ayrıca test edilmeli). |
| **K14** | Kodun makale metninden ayrıldığı noktalar: (a) yön yalnızca önceki göreve göre seçiliyor, başa eklemede seçilmiyor; (b) depot dönüş terimi puan hesabının yalnızca bir tarafında; (c) kapasite eklemeden önce kontrol ediliyor | ✅ **Onaylandı: iki mod** |  **`paper_compat`** (D1–D3): T23'ün davranışını olduğu gibi uygular; makale ve sonuç dosyalarıyla karşılaştırma bununla yapılır. **`corrected`** (D4–D6): makale metnine (Eq. 8) göre her iki yön ve her ekleme yeri, iki puan hesabında aynı terimler, kapasite aşılmaz; iki mod arasındaki fark ayrıca raporlanır. **Gerekçe:** Makalenin yayımlanan sayıları T23 ile üretildi; projenin kendi deneyleri makale metnindeki tanıma uygun bir uygulamayla yapılmalı. |
| **K15** | D1 kapasitesi | ✅ **Onaylandı** | Ana tablo **1200 s** (makale metni); ek olarak **1500 s** (sonuç dosyası). **Gerekçe:** C10'da gözlemlenen farkı açıkça göstermek. |
| **K16** | İHA arıza olasılığı (D5) | ⏳ **Aday — karar bekliyor** | Aday kaynak: Aznar 2026 §5.1, §6.4.2: kalıcı ajan arızası "0.01% and 0.1% per step after an initial 500s grace period"; temel durum %0. **Sorun:** makalede "adım" (step) süresi tanımlı değil (SimPy ayrık olay simülasyonu, §5.1). Adım süresi bilinmeden olasılık bizim zaman birimimize çevrilemez. Ayrıca bu olasılıklar uçuş sırasındaki (yürütme) arızalar için; CBBA'nın atama aşamasında ise "adım" CBBA turudur ve süresi farklıdır. **Seçenekler:** (a) yazarlara/koda bakıp adım süresini doğrulamak; (b) olasılık yerine deterministik senaryo: belirli bir İHA belirli bir anda düşer (kaynak gerektirmez, yeniden atamayı göstermek için yeterli); (c) değerleri "adım = 1 s" varsayımıyla kullanmak — varsayım kaynaksız olduğu için yalnızca **test ayarı** olur. |

## C9. Kaynak notları

- **Yazar adı:** Makale PDF'inde yazarlar "Kasper A. R. Grøntved, **Ulrik P. S. Lundquist**, Anders Lyhne Christensen". CLAUDE.md §12 ve `scenarios/README.md` buna göre düzeltildi (24 Kasım 2026). CoverageTasks README'sindeki BibTeX'te hâlâ "Schultz, Ulrik Pagh" yazıyor.
- Elimizdeki makale yazarların kabul edilmiş son taslağı (SDU Research Portal). Bölüm ve denklem numaraları buna göre.
- trajallocpy klonu: `~/makaleler/trajallocpy/` (güncel sürüm) ve `~/makaleler/trajallocpy_2023/` (`git worktree`, commit `13b7bb3`). İkisi de repo dışında; yalnızca okumak için.
- **Eksik PDF'ler:**
  - Choi 2009: MIT DSpace 429 hatası verdi; kullanıcı tarayıcıdan İndirilenler'e indirecek, `~/makaleler/Choi2009.pdf` olarak kopyalanıp K1 doğrulanacak.
  - Turner 2017: K5 koddan çözüldüğü için şimdilik gerekmiyor.
  - Zeng 2019 ve Rodrigues 2021: A4'ten önce gerekli.
- **K7 ve K16 kaynakları** (arXiv'den indirildi, 25 Kasım 2026):
  - **[Aznar 2026]** = Aznar, Pujol, Díez, "Event-Triggered Adaptive Consensus for Multi-Robot Task Allocation", arXiv:2604.06813 (v1, 2026), `~/makaleler/Aznar2026_EventTriggeredCBBA.pdf`.
  - **[Liu 2026]** = Liu, Zhang, "CC-OPI: Online Distributed Task Allocation for UAV Swarms under Communication Constraints", arXiv:2609.19208 (v1, 2026), `~/makaleler/Liu2026_CCOPI.pdf`.
  - İkisi de arXiv ön baskısı (hakem onayından geçmemiş olabilir); raporda bu belirtilir.
- **İlgili çalışma (K7 kaynağı değil):** Sao, Ho, Bhore, Sujit, "Event Driven CBBA with Reduced Communication", arXiv:2509.06481 (2025), `~/makaleler/Sao2025_EventDrivenCBBA.pdf`. Olay tetiklemeli CBBA ile yayın sayısını %52'ye kadar azaltıyor (§IV: 100 m × 100 m, 5–50 İHA, 100 Monte Carlo). Paket kaybı deneyi yok; kayıp yalnızca motivasyon (§III) ve gelecek çalışma (§V) olarak geçiyor.

## C10. Gözlemlenen farklar: makale metni ve yazarların sonuç dosyaları

Yazarların sonuç dosyaları (`benchmarks/AC300/*.csv`) ve deney betiği (`run_experiments.sh`) T23 sürümünde yer alıyor. Dosyaları okuyup topladım ve makale metnindeki değerlerle karşılaştırdım. Aşağıdaki tablo yalnızca **gözlemleri** içerir; farkların nedeni doğrulanmadı. Grafikler ayrı bir işlemle, farklı bir ölçütle ya da bu depoda bulunmayan dosyalarla üretilmiş olabilir.

| Makale metni | Sonuç dosyası / betik | Gözlem |
|---|---|---|
| D1: 2 İHA × **1200 s**, toplam **554.920 s** [G §V] | `2robots_1500capacity_AC300.csv` toplamı **554.921 s** (300 ortam). Bu depoda 1200 s'lik bir yörünge sonuç dosyası yok. | Makaledeki toplam, 1500 s dosyasının toplamıyla sayısal olarak aynı. |
| Merkezi yöntem **544.592 s** [G §V] | `agarwal_AC300_1200_Capacity.csv` toplamı **544.592 s**, **320 ortam** (AC0–AC15, her birinden 20). | Yörünge dosyası 300 ortam içeriyor; iki toplam farklı sayıda ortamdan. |
| 6 İHA × **600 s** [G Fig. 4–5 açıklaması] | Dosya `6robots_500capacity`; betikte `--capacity=500` [T23 run_experiments.sh:39] | Kapasite değeri farklı. |
| 8/10/12/14 İHA × **500 s** [G Fig. 4–5 açıklaması] | 8 İHA: `--capacity=500`. 10/12/14 İHA: `--capacity=400`, dosya adları `500capacity` [T23 run_experiments.sh:35-38] | 10/12/14 için komut satırı değeri ile dosya adı farklı. 10 ve 12 İHA dosyaları 177 ve 162 ortam içeriyor (300 değil). |
| Ortalama en uzun İHA süresi: 2 İHA **972 s**, 14 İHA **229 s** [G §V-A] | Dosyalardan hesaplanan ortalama `maxRouteCost`: 2 İHA **1059,8 s**, 14 İHA **259,9 s** | Değerler farklı; grafikte kullanılan ölçüt dosyalardan belirlenemedi. |

**D1'de iki ayrı karşılaştırma yapılacak** (K15 ile birlikte):
1. **Makale metnindeki değerlerle:** 554.920 s, merkezi 544.592 s (%1,9), nokta puanlamaya göre %6, 972/229 s.
2. **Sonuç dosyalarından hesaplanan değerlerle, ortam ortam:**
   - Bizim 1200 s ve 1500 s sonuçlarımız, yazarların `2robots_1500capacity` dosyasıyla.
   - Merkezi yöntem, `agarwal_AC300_1200_Capacity.csv` içindeki ortam başına `Sum of Costs of Routes` değerleriyle; yalnızca iki dosyada da bulunan ortamlar üzerinden.
   - Ölçeklenebilirlik (D2), dosyalardaki kapasite değerleriyle de ayrıca çalıştırılıp karşılaştırılır.

Raporda iki karşılaştırma ayrı tablolarda verilir ve bu bölümdeki gözlemler sınırlılık olarak belirtilir.
