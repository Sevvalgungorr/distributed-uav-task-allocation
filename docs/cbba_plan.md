# CBBA Uygulama Planı

> Durum: **A0 kararları alındı (24 Kasım 2026). A0.8 madde 1 (olay arayüzü) tamamlandı (`bf47850`, 25 Kasım 2026).**
> **25 Kasım 2026 güncellemesi:** A0.1 panel tasarımı ve teknolojisi yeniden ele alındı (A0.1, A0.9 #1 ve #7 **onay bekliyor**, maket: `docs/design/panel_maket.html`). A7 (kişi tespiti) eklendi (**onay bekliyor**).
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

**Referans:** `Downloads/Gazebo’da Sürü İHA Alan Taraması.png` **[R-G]**, `Downloads/Neon İHA Sürü Tarama Simülasyonu.png` **[R-N]** ve `Downloads/Gazebo + panel (temsili).pdf` **[R-P]**. İlk ikisi yapay zekâ ile üretilmiş tasarım fikirleri (aynı fikrin sahne ve panel ağırlıklı versiyonları); R-P, AC10_0000 geometrisiyle çizilmiş temsili bir görsel. Üçündeki sayılar örnektir, kullanılmaz. Panelin hangi özelliği hangi referanstan aldığı A0.1.1'deki tabloda.

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

**3) A7 için planlanan olaylar** (⏳ **henüz kodda yok**; `mission_events.py` A7 entegrasyonuna kadar değişmez, A7 bölümü):

```json
{ "type": "event", "time": 1795515301.20, "uav": 2, "event": "person_detected",
  "x": 41.5, "y": 63.0, "confidence": 0.91, "model": "resnet50_heridal_v1",
  "image": "heridal/patches/test/pos_000123.png" }
{ "type": "event", "time": 1795515301.25, "uav": 2, "event": "confirm_task_created",
  "task": 1001, "x": 41.5, "y": 63.0, "source_event_uav": 2 }
```

| `event` | Anlamı | Alanlar |
|---|---|---|
| `person_detected` | İHA'nın taradığı hücrede sensör modeli (A7) pozitif karar verdi | `x`, `y` (veri seti metre, hücre merkezi), `confidence` (0–1), `model` (model adı/sürümü), `image` (**isteğe bağlı**, modele verilen parçanın yolu). `task` alanı yok. |
| `confirm_task_created` | Tespit noktası için bir **doğrulama görevi** (nokta görev) oluşturuldu; CBBA'ya dinamik görev olarak eklenecek (A5 mekanizması) | `task` (yeni görev kimliği; veri seti görevleriyle çakışmasın diye 1000'den başlar — **arayüz ayarı**), `x`, `y`, `source_event_uav` |

- Doğrulama görevinin atanması ayrı bir olay değildir: yeni bir `assignment` mesajıyla gelir (yeni atama öncekinin yerine geçer, kural yukarıda). Doğrulama görevinin uçuşu da aynı `task_started`/`task_finished` olaylarını kullanır.
- Panelde: `person_detected` → haritada işaret + "Tespitler" kartında satır; `confirm_task_created` → haritada nokta görev simgesi.

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

> **25 Kasım 2026: yeniden tasarlandı, onay bekliyor.** Önceki karar (matplotlib + Tk penceresi, A0.9 #1) bu bölümün sonundaki teknoloji değerlendirmesi nedeniyle **değişiklik önerisi** durumunda. Uçuş kodu ve `mission_events.py` arayüzü bu değişiklikten etkilenmez.

**Amaç:** Basit bir test arayüzü değil, mühendislik izleme paneli: tek bakışta senaryo, atama kaynağı, İHA durumları, görev ilerlemesi ve fiziksel kapsama. Panel **yalnızca izler**, İHA'ya komut göndermez.

**Tasarım maketi:** `docs/design/panel_maket.html`
- Gerçek AC10_0000 geometrisi (sınır, 10 engel, 107 şerit; `swarm_core.dataset` ile okunup sayfaya gömüldü).
- Atama, ilerleme, hız/irtifa, süre, zaman çizelgesi ve olay günlüğü **örnek** değerler, sayfada "ÖRNEK" etiketli. Örnek atama: şerit orta noktası y ≥ 50 → İHA-1 (58 görev), değilse İHA-2 (49 görev), şeritler y'ye göre sıralı, veri setindeki yönde; **yalnızca maket için**.
- **Örnek animasyon** ("ÖRNEK ANİMASYON" etiketli): İHA'lar ortak kalkış noktasından (0,0) şeritleri sırayla tarar. Hareket hız rampası modeliyle (v_max 3 m/s, a_max 1 m/s², her ayakta tam duruş; CLAUDE.md §13) hesaplanır; engellerden kaçınma yok (`fly_task.py` gibi). Oynat/duraklat, başa sar, ×5–×40 hız ve zaman çubuğu yalnızca maketi etkiler. Adres sonuna `?t=640` eklenirse animasyon o saniyede durmuş açılır.
- **Hareketin anlaşılırlığı (öncelikli hedef):** İHA simgesi + yön oku (hareket yönü), İHA renginde son 60 s'lik iz (eskiden yeniye solar), aktif şerit İHA renginde kalın ve parlak, sıradaki şerit İHA renginde kesik, biten şerit yeşile döner ve 3 m tarama izi belirir; sayaçlar, oranlar, grafik ve olay günlüğü aynı anda ilerler.
- Dış kütüphane ve ağ bağlantısı yok; dosyayı tarayıcıda açmak yeterli. Windows'ta: `\\wsl$\Ubuntu-24.04\home\sevval\suruiha\docs\design\panel_maket.html` (ya da WSL'de `explorer.exe docs/design/panel_maket.html`).

#### A0.1.1 Özellik tablosu

Referanslar: **R-G** = Gazebo'da Sürü İHA Alan Taraması.png, **R-N** = Neon İHA Sürü Tarama Simülasyonu.png, **R-P** = Gazebo + panel (temsili).pdf (A0.0.1).
Veri kaynağı: **telemetri** = PX4 (UDP 14550), **olay** = A0.0.5 arayüzü (UDP 15600), **veri seti** = `scenarios/*.json`, **henüz yok** = kaynağı olan bir modül henüz yazılmadı.

| # | Özellik | Referans | Veri kaynağı | Karar | Neden / not |
|---|---|---|---|---|---|
| 1 | Başlık + bağlantı rozetleri (telemetri, olay akışı) | R-N ("Simülasyon Çalışıyor"), R-G | telemetri, olay (son mesajın yaşı) | **Şimdi** | R-N'deki tek "çalışıyor" rozeti yerine iki kaynak ayrı gösterilir: hangisinin koptuğu görünür. |
| 2 | Üst sekmeler | R-N | — | **Şimdi** (yalnız "Canlı izleme" etkin) | Görevler, İHA'lar: sonra; Atama/CBBA: A1 sonrası; Tespitler: A7; Deneyler: A3 sonrası. Etkin olmayan sekmeler "sonra" etiketiyle görünür. |
| 3 | Senaryo bilgi kartı (ortam, alan, engel, görev, toplam şerit uzunluğu, 3 m, v_max/a_max) | R-N ("Senaryo") | veri seti; v/a CLAUDE.md §13 | **Şimdi** | Bütün sayılar dosyadan hesaplanır; her değerin kaynağı kartın altında yazar. |
| 4 | Senaryo ve algoritma seçme listeleri | R-N | — | **Çıkarıldı** | İzleme paneli; senaryo uçuş betiğinden gelir. Algoritma seçilmez, kaynağı etiketlenir (#5). |
| 5 | Atama kaynağı etiketi (Manuel atama / CBBA) | R-P ("Atama: Manuel atama") | olay (`assignment.source`) | **Şimdi** | A0.0.5 kuralı: elle atama hiçbir zaman CBBA gibi gösterilmez. |
| 6 | İHA kartı: renk, ad, Sistem ID | R-G, R-N, R-P | telemetri | **Şimdi** | — |
| 7 | İHA durum rozeti (Bağlantı yok / Yerde / Havada / Görevde) | R-N ("Görevde") | telemetri (`armed`, `in_air`, son mesaj yaşı) + olay (`task_started`) | **Şimdi** | Kurallar `mission_state.py`'de, birim testli. |
| 8 | Hız, irtifa | R-G, R-N, R-P | telemetri | **Şimdi** | — |
| 9 | Uçuş modu | — (A0.1 ilk planı) | telemetri | **Şimdi** | OFFBOARD/HOLD/LAND ayrımı hata ayıklamada gerekli. |
| 10 | Aktif görev | R-G, R-N, R-P | olay | **Şimdi** | Biçim `#görev_no`. R-G/R-N'deki "27 / 161" biçimi anlamsız (görev no / toplam). |
| 11 | Tamamlanan / atanan (İHA başına) + çubuk | R-N, R-P | olay + atama | **Şimdi** | — |
| 12 | Pil / enerji | R-G, R-N | **henüz yok** | **Sonra (A4)** | Enerji modeli yok; kartta "— A4" yazar, uydurma yüzde gösterilmez. |
| 13 | İHA fotoğrafı | R-N | — | **Çıkarıldı** | Bilgi taşımıyor, yer kaplıyor. |
| 14 | **Görev tamamlama oranı** | R-G, R-N, R-P | olay | **Şimdi** | tamamlanan görev ÷ toplam görev. |
| 15 | **Fiziksel kapsama oranı** (ayrı kart) | R-N ("Alan Kapsama"); formül bizim | olay + veri seti (şerit uzunlukları) | **Şimdi** | Tanım ve sınırları A0.6'da. Formül kartta açıkça yazılı, iki oran yan yana ama ayrı kartlarda; karıştırılmaz. |
| 16 | Kapsama zaman çizelgesi | R-N | olay zaman damgaları | **Şimdi** | İki seri (görev tamamlama, fiziksel kapsama) + senaryonun kapsama üst sınırı çizgisi (AC10_0000: %96,2). |
| 17 | Anlık metrik kutuları (ort. hız, toplam süre, kapsama, enerji) | R-N | telemetri, olay; enerji henüz yok | **Kısmen** | Geçen süre üst çubukta. Ortalama hız gibi metrikler A5 metrik tanımlarından sonra (C7, Aşama 5); enerji A4. |
| 18 | Ana 2D harita: sınır, engeller, şeritler, durum renkleri | R-G, R-N, R-P (3D sahne) | veri seti + olay | **Şimdi** | Panel 2D üstten görünüm; 3D sahne Gazebo'nun işi (A0.2–A0.4). |
| 19 | 3 m tarama izi (tamamlanan şeridin genişliği) | R-G ("Tarama alanı 3 m"), R-P ("Taranan şerit 3 m") | veri seti (3 m) + olay | **Şimdi** (katman) | Fiziksel kapsamanın haritadaki karşılığı. |
| 20 | Uçulan iz | R-G, R-N, R-P | telemetri | **Şimdi** (katman) | İHA renginde, son N saniye (maket: 60 s), eskiden yeniye solar; N görselleştirme ayarı. Uzun iz biten şeritlerin yeşilini örttüğü için kısa tutulur. |
| 21 | Planlanan rota (kesik çizgi) | R-N, R-P | atama (+ `reversed`) | **Şimdi** (katman) | — |
| 22 | Yön oku | R-G | telemetri (hız vektörü) | **Şimdi** | İHA simgesine bağlı; dururken son hareket yönünü gösterir. |
| 22b | Aktif şerit vurgusu / sıradaki şerit / biten şeridin renk değiştirmesi | R-G, R-N, R-P | olay | **Şimdi** | Aktif: İHA renginde kalın + parlama; sıradaki (şerit başına giderken): İHA renginde kesik; biten: yeşil + 3 m izi. |
| 23 | Ölçek çubuğu, kuzey oku, metre eksenleri, kalkış noktası | R-G, R-N, R-P | veri seti | **Şimdi** | — |
| 24 | Katman aç/kapa düğmeleri | — (bizim) | — | **Şimdi** | Yalnızca görünümü değiştirir; İHA'ya hiçbir şey gönderilmez. |
| 25 | Mini harita | R-G, R-N, R-P | atama | **Şimdi**, **atama görünümü** olarak | Ana harita zaten bütün alanı gösterdiği için mini harita aynısını tekrar etmez: şeritleri **atandığı İHA'nın rengiyle** (sahiplik) gösterir. CBBA/yeniden atama sonrası dağılım tek bakışta görülür. |
| 26 | Lejant | R-G, R-N, R-P | — | **Şimdi** | — |
| 27 | Olay günlüğü | — (bizim) | olay | **Şimdi** | Son olaylar zaman damgasıyla; deney sırasında neyin ne zaman olduğu görülür. |
| 28 | Tespitler kartı | — (A7) | **henüz yok** (`person_detected`) | **Boş kart, A7'de dolar** | — |
| 29 | Kaynak notu | R-P | — | **Şimdi** | Geometri ve parametrelerin kaynağı panelde yazar. |
| 30 | "Temsili / örnek" uyarısı | R-P | — | **Yalnızca makette** | Canlı panelde yerine bağlantı rozetleri (#1) var. |
| 31 | Durdur / Sıfırla / Ayarlar düğmeleri | R-N | — | **Çıkarıldı** | **Güvenlik:** panel İHA'ya komut göndermez; uçuşu yalnızca uçuş betiği yönetir. |
| 32 | Simülasyon hızı seçici (x1.0) | R-G | — | **Çıkarıldı** | Gazebo'nun işi. Ölçülen RTF A0.5'ten sonra salt okunur rozet olarak eklenebilir. |
| 33 | 3D perspektif sahne, binalar, ağaçlar, helipad, neon ışık | R-G, R-N | — | **Panelde yok** | 3D görünüm Gazebo'da (A0.2–A0.4); dekor "Daha sonra" listesinde. |

#### A0.1.2 Teknoloji değerlendirmesi

**Tk + matplotlib bu görünümü verebilir mi?** Haritayı (çizgiler, çokgenler, iz) verebilir. Paneli **maketteki kalitede vermesi zor**:
- Kartlar, yuvarlatılmış köşeler, durum rozetleri, sekmeler, tipografi ve esnek yerleşim Tk'de elle çizim ya da ek kütüphane (ör. CustomTkinter) gerektirir; sonuç yine "masaüstü test aracı" gibi görünür.
- matplotlib'in WSLg'de canlı güncellemesi A0.1'in ilk planında zaten risk olarak yazılmıştı (hedef 5 Hz).
- Qt (PySide6) görünümü verebilir ama ağır bir bağımlılık ve yeni bir çerçeve öğrenmek demek.

**Öneri: tarayıcıda açılan yerel web paneli.**

```text
PX4 -i 0..n ── MAVLink UDP 14550 ──┐
fly_task.py ── mission_events UDP 15600 ──┤
                                          ▼
              swarm_viz/server.py  (Python, asyncio + aiohttp)
              - 14550: MAVSDK pasif bağlantı (konum, hız, irtifa, mod, armed/in_air)
              - 15600: olay alıcısı → assignment.py + mission_state.py (saf Python, test edilir)
              - Birleşik durumu 5 Hz'de WebSocket ile yayınlar
              - Statik dosyaları sunar: http://localhost:8765
                                          ▼
              Tarayıcı (Windows'ta Chrome/Edge): swarm_viz/web/ (HTML + CSS + JS, SVG harita)
```

| | Tk + matplotlib | **Yerel web paneli (öneri)** |
|---|---|---|
| Görünüm | Harita iyi, panel sınırlı | Maketteki görünüm doğrudan (maket zaten HTML) |
| Ek kütüphane | `python3-tk` (apt) | `aiohttp` (pip, tek paket; HTTP + WebSocket). Ön yüzde kütüphane yok: düz JS + SVG, CDN yok, çevrimdışı çalışır. |
| Canlı güncelleme | WSLg + matplotlib yeniden çizimi (risk) | Tarayıcı SVG'yi kendisi çizer; 5 Hz rahat |
| Test | `Agg` ile çizim testi | Sunucu ve durum mantığı `pytest`; sayfa için başsız Chrome ekran görüntüsü (bu maket de böyle kontrol edildi) |
| Yeni öğrenilecek | Az | WebSocket ve biraz JS (bilgisayar mühendisliği müfredatında tanıdık) |
| Sunum / rapor | Pencere ekran görüntüsü | Aynı sayfa sunumda açılabilir; ekran görüntüsü kolay |
| Risk | WSLg hızı | WSL2 → Windows `localhost` yönlendirmesi (WSL2'de varsayılan açık; çalışmazsa WSL IP'si kullanılır). 14550 tek süreç kuralı aynı. |

- **Uçuş kodu ve `mission_events.py` değişmez:** sunucu, A0.0.5 arayüzünün dinleyen tarafıdır.
- **Katman ayrımı korunur:** `swarm_viz/` `swarm_core` ve `swarm_sim`'i okuyabilir; tersi olmaz. `aiohttp` yalnızca `swarm_viz`'de.
- "Daha sonra" listesindeki React + FastAPI önerisinin hafif hâli: derleme adımı ve Node.js yok.

**Dosyalar (öneri onaylanırsa):**
- **Yeni:** `swarm_viz/__init__.py`, `viz_config.py`, `geo.py`, `assignment.py`, `mission_state.py` (yukarıdaki planla aynı), `swarm_viz/server.py` (UDP + MAVSDK + WebSocket + statik dosya), `swarm_viz/web/index.html`, `panel.css`, `panel.js` (maketten türetilir).
- **Değişmeyecek:** `swarm_sim/fly_task.py`, `swarm_sim/mission_events.py`.
- **Testler:** `tests/test_geo.py`, `test_assignment.py`, `test_mission_state.py` (durum rozeti kuralları ve iki oran dahil), `tests/test_viz_server.py` (sahte UDP olayı → WebSocket'ten beklenen durum; `aiohttp` test istemcisi).

**CBBA öncesi demo** (değişmedi): `fly_task.py` AC10_0000 görev 1–4 (`manual`); iki İHA'nın aynı anda görünmesi için `multi_takeoff_land.py`.

**Ortak koordinat sistemi** (değişmedi): Harita konumları GPS'ten (enlem/boylam) dünya başlangıcına göre metreye çevirir; dünya başlangıcı PX4 dünyasındaki `spherical_coordinates` (47.397971057728974, 8.546163739800146). Veri seti (0,0) = dünya (0,0); x doğu, y kuzey.

**Zorluk / süre:** Orta. **≈ 4 iş günü** (önceki Tk planı ≈ 3 gündü; fark ≈ +1 gün).
- Olay modülü + `fly_task` değişikliği: 0,5 — ✅ tamamlandı (`bf47850`)
- Atama + görev durumu + coğrafi yardımcılar ve testleri: 1
- Sunucu (UDP + MAVSDK + WebSocket) ve testi: 1
- Sayfa (maketten canlı veriye): 1,5

**Riskler:**
- 14550'yi aynı anda tek süreç dinleyebilir; QGroundControl açıksa çakışır.
- MAVSDK'nin tek bağlantıda iki sistemi ayırması bu projede henüz denenmedi. İlk iş kısa bir deneme.
- GPS tabanlı konum gürültülü olabilir. Görünür bir sapma olursa yerel konum + bilinen kalkış noktası kullanılır.
- WSL2 → Windows tarayıcı erişimi (`localhost:8765`) bu makinede henüz denenmedi.

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

- **Görev tamamlama oranı** = tamamlanan görev / toplam görev. Görev olaylarından gelir.
- **Fiziksel kapsama oranı (yaklaşık, panel için)** — *25 Kasım 2026 kararıyla A0'da ayrı kartta gösterilir* (A0.1.1 #15):
  `Σ (task_finished olayı gelmiş şeritlerin uzunluğu) × 3 m ÷ sınır alanı`
  - 3 m: CoverageTasks README ("sweep-width of 3 meters"). Sınır alanı veri setinden (AC10_0000: 10.000 m²).
  - **Sınırlar:** şerit uçlarındaki örtüşme ve engel alanı düşülmez; yarım kalan şerit sayılmaz. AC10_0000'da toplam şerit uzunluğu 3.206,4 m olduğundan bütün görevler bitince değer **%96,2**'de kalır (%100 olmaz). Payda engel dışı alan (8.577,2 m²) alınsaydı %112,1 çıkardı; bu yüzden payda bilerek sınır alanıdır. Panelde "yaklaşık" yazar ve üst sınır gösterilir.
  - Hesap yeri: `swarm_viz/mission_state.py` (saf Python, birim testli).
- **Kesin fiziksel kapsama** (uçulan gerçek izin 3 m genişlikteki tamponunun, engel dışı alanla kesişimi; `shapely`): deney metriği olarak A5 metrik tanımlarıyla birlikte yapılacak. Panel değeri deney sonucu olarak raporlanmaz.

### A0.7 — CBBA öncesi / sonrası

| Özellik | Ne zaman | Süre |
|---|---|---|
| 2D canlı harita + panel (atama girdisi, görev olayları dahil) — yerel web paneli önerisiyle (A0.1.2) | **CBBA öncesi** | ≈ 4 gün (olay arayüzü ✅) |
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
3. `feat(viz): live web panel (server + page)` + sunucu testi + başsız tarayıcı ekran görüntüsü + uçuş sırasında elle doğrulama (A0.1.2 onaylanırsa; onaylanmazsa eski Tk planı)
4. `chore: ignore generated worlds` (`.gitignore`: `worlds/*.sdf`)
5. `feat(viz): GeoJSON to SDF world generator with 0.5 m obstacle inset` + XML testi
6. `feat(viz): fixed camera GUI config` (elle doğrulama)
7. `feat(viz): RTF measurement` + `docs` sonuç tablosu

Her commit'ten önce `pytest`; uçuşa dokunan değişikliklerden sonra simülasyonda uçuş.

### A0.9 Kararlar

| # | Karar | Durum |
|---|---|---|
| 1 | 2D pencere: matplotlib + Tk. `python3-tk` kullanıcı tarafından kurulacak. | ⏳ **Değişiklik önerildi (25 Kasım 2026):** yerel web paneli (`aiohttp` + HTML/CSS/JS), A0.1.2. Onay bekliyor. |
| 2 | Engel görsel yüksekliği 1,0 m, "görselleştirme ayarı" olarak işaretli. | ✅ Karar verildi |
| 3 | Yalnızca üretici betik commit edilir; `worlds/*.sdf` `.gitignore`'da. | ✅ Karar verildi |
| 4 | CBBA öncesi: 2D harita + panel, temel dünya, sabit kamera, performans ölçümü. Gerisi sonraya. | ✅ Karar verildi |
| 5 | 23 görev konusu risk değil: şeritler engel kenarları boyunca; engeller 0,5 m içeriden çizilir. | ✅ Karar verildi, doğrulandı |
| 6 | Görselleştirme, görev atamasını (`{iha_id: [görev_id sırası]}`) ve görev başladı/bitti olaylarını genel bir arayüzden alır (A0.0.5). Elle verilen atama "Manuel atama", CBBA çıktısı "CBBA" olarak etiketlenir; CBBA eklendiğinde görselleştirme kodu değişmez. | ✅ Karar verildi |
| 7 | Panel özellikleri A0.1.1 tablosundaki gibi; görev tamamlama ve fiziksel kapsama (yaklaşık, A0.6) ayrı kartlarda; panel İHA'ya komut göndermez; pil A4'e kadar boş. | ⏳ Onay bekliyor (maket: `docs/design/panel_maket.html`) |

### Daha sonra (isteğe bağlı, A0 kapsamı dışında)

- x500 modellerine farklı renklerde LED (model SDF'ini kopyalayıp renk ekleme; PX4 modeli değiştirilmez).
- Neon benzeri ışıklı rota efektleri.
- Gerçekçi arazi dokuları; ağaçlar yalnızca alan dışında, dekor olarak.
- ~~React + FastAPI + WebSocket kontrol paneli.~~ Hafif hâli A0.1.2'de öneriliyor (izleme paneli; kontrol yok).
- A4 enerji modelinden sonra pil ve enerji göstergeleri.

---

# CBBA — Dağıtık görev atama

> Durum: **K1 (Choi 2009 PDF'iyle doğrulama) dışında kararlar alındı.** K7 25 Kasım 2026'da kaynaklarıyla onaylandı. K16 aynı gün onaylandı (deney tasarımı, kaynak değil). CBBA kodu henüz yazılmadı.

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
| **A7** Kişi tespiti (sensör modeli) | HERIDAL; ResNet/DenseNet/ViT transfer öğrenme karşılaştırması; Grad-CAM; veri setine dayalı sensör simülasyonu; doğrulama görevi (A7 bölümü) | Sınıflandırma metrikleri raporlandı; simülasyonda `person_detected` → doğrulama görevi → CBBA ile atandı ve uçuldu. **Entegrasyon A3'ten sonra; eğitim yan hat.** |

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
- `swarm_core/models.py`: `Task` ve `UAV` (başlangıç konumu) kullanılır. `UAV.battery` ve `UAV.is_leader` silinmez. CBBA'nın iç durumu `cbba.py` içinde tutulur. A7'de `Task`'a `kind` alanı (`"sweep"` / `"confirm"`, varsayılan `"sweep"`) eklenmesi planlandı (A7.4).
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
| **K16** | İHA arızası (D5) | ✅ **Onaylandı (25 Kasım 2026): belirlenmiş senaryo.** ⚠️ **Deney tasarımı — kaynak değil, bizim seçimimiz.** | **Arıza anı:** kapasitenin (`L_t`) **%25, %50, %75**'i (erken / orta / geç arıza). Kapasiteye oransal olduğu için D2'deki farklı `L_t` değerlerinde (1500/750/600/500 s) karşılaştırılabilir. **Düşen İHA:** (1) **en etkili durum:** arıza anında en çok kalan görevi olan İHA (kalan görev = yolunda olup henüz başlanmamış görevler; eşitlikte küçük kimlik, K1/K8 ile tutarlı — bu eşitlik kuralı da bizim seçimimiz); (2) **rastgele seçilen İHA**, 10 tohum: **test ayarı.** Olasılıklı arıza modeli kullanılmıyor; Aznar 2026'nın olasılıkları (adım süresi tanımsız) kullanılmadı, yalnızca C9'da ilgili çalışma olarak anılıyor. |
| **K17** | Doğrulama görevinin ödülü ve bekleme süresi (A7) | ⏳ Açık | Tarama görevlerinde `c̄_j = 1` (K3). Doğrulama görevi için kaynak aranacak; bulunamazsa deney tasarımı olarak işaretlenir. |

## C9. Kaynak notları

- **Yazar adı:** Makale PDF'inde yazarlar "Kasper A. R. Grøntved, **Ulrik P. S. Lundquist**, Anders Lyhne Christensen". CLAUDE.md §12 ve `scenarios/README.md` buna göre düzeltildi (24 Kasım 2026). CoverageTasks README'sindeki BibTeX'te hâlâ "Schultz, Ulrik Pagh" yazıyor.
- Elimizdeki makale yazarların kabul edilmiş son taslağı (SDU Research Portal). Bölüm ve denklem numaraları buna göre.
- trajallocpy klonu: `~/makaleler/trajallocpy/` (güncel sürüm) ve `~/makaleler/trajallocpy_2023/` (`git worktree`, commit `13b7bb3`). İkisi de repo dışında; yalnızca okumak için.
- **Eksik PDF'ler:**
  - Choi 2009: MIT DSpace 429 hatası verdi; kullanıcı tarayıcıdan İndirilenler'e indirecek, `~/makaleler/Choi2009.pdf` olarak kopyalanıp K1 doğrulanacak.
  - Turner 2017: K5 koddan çözüldüğü için şimdilik gerekmiyor.
  - Zeng 2019 ve Rodrigues 2021: A4'ten önce gerekli.
- **K7 kaynakları** (arXiv'den indirildi, 25 Kasım 2026):
  - **[Aznar 2026]** = Aznar, Pujol, Díez, "Event-Triggered Adaptive Consensus for Multi-Robot Task Allocation", arXiv:2604.06813 (v1, 2026), `~/makaleler/Aznar2026_EventTriggeredCBBA.pdf`.
  - **[Liu 2026]** = Liu, Zhang, "CC-OPI: Online Distributed Task Allocation for UAV Swarms under Communication Constraints", arXiv:2609.19208 (v1, 2026), `~/makaleler/Liu2026_CCOPI.pdf`.
  - İkisi de arXiv ön baskısı (hakem onayından geçmemiş olabilir); raporda bu belirtilir.
- **İlgili çalışma (arıza, K16 kaynağı değil):** Aznar 2026 kalıcı ajan arızasını olasılıklı modelliyor: "0.01% and 0.1% per step after an initial 500s grace period" (§5.1, §6.4.2). "Adım" süresi tanımlı değil (SimPy ayrık olay simülasyonu) ve 500 s bekleme bizim kapasitelerimizle (500–1500 s) uyumsuz; bu yüzden D5'te kullanılmadı.
- **İlgili çalışma (K7 kaynağı değil):** Sao, Ho, Bhore, Sujit, "Event Driven CBBA with Reduced Communication", arXiv:2509.06481 (2025), `~/makaleler/Sao2025_EventDrivenCBBA.pdf`. Olay tetiklemeli CBBA ile yayın sayısını %52'ye kadar azaltıyor (§IV: 100 m × 100 m, 5–50 İHA, 100 Monte Carlo). Paket kaybı deneyi yok; kayıp yalnızca motivasyon (§III) ve gelecek çalışma (§V) olarak geçiyor.

- **A7 kaynakları** (25 Kasım 2026 web araması; PDF'ler henüz indirilmedi):
  - **[HERIDAL]** Božić-Štulić, Marušić, Gotovac, IJCV 127(9):1256–1278, 2019, DOI 10.1007/s11263-019-01177-1 (dblp + Springer).
  - Pyrrö (Aalto), Zenodo DOI 10.5281/zenodo.5662351 (HERIDAL türevi, CC BY 3.0).
  - Pyrrö vd., arXiv:2111.09406 (2021) — etiket sayıları.
  - Gotovac vd., *Remote Sensing* 12(20):3295 (2020) — parça sayısı.
  - IPSAR sayfası okunamadı (ECONNRESET); lisans A7.1'de açık.

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

---

## A7 — Derin öğrenme tabanlı kişi tespiti: İHA'nın sensör modeli

> Durum: **plan, onay bekliyor (25 Kasım 2026).** Kod yok. Entegrasyon CBBA A3'ten sonra; veri hazırlığı ve eğitim yan hat (A7.6).

### A7.0 Amaç ve projedeki yeri

- Grøntved vd. 2023'te sensör **soyuttur**: bir şerit uçulunca 3 m genişliğindeki alan "taranmış" sayılır (CoverageTasks README: "sweep-width of 3 meters"). Taramanın neyi aradığı modellenmez.
- A7 bu soyut sensörün yerine **gerçek görüntü + gerçek model kararı** koyar ve taramanın amacını somutlaştırır: arama-kurtarmada kişi bulmak.
- **Ayrı bir proje değildir.** Tespit, CBBA'nın dinamik görev ekleme/yeniden atama mekanizmasını (A5) gerçek bir tetikleyiciyle çalıştırır: tespit → doğrulama görevi → dağıtık atama.
- Danışmanın alanıyla bağlantı: CNN/ViT, transfer öğrenme, açıklanabilir YZ.

### A7.1 Veri seti: HERIDAL

| | Durum | Bilgi |
|---|---|---|
| Künye | ✅ Doğrulandı (dblp, Springer DOI) | Božić-Štulić, D., Marušić, Ž., Gotovac, S. (2019). "Deep Learning Approach in Aerial Imagery for Supporting Land Search and Rescue Missions". *International Journal of Computer Vision*, 127(9), 1256–1278. DOI: 10.1007/s11263-019-01177-1. Not: CROSBI kaydı sayfaları 1–23 veriyor (çevrimiçi ön yayın numaralandırması olabilir); kaynakçada dblp/Springer'deki 1256–1278 kullanılır. |
| Makaledeki sonuç (yalnız bağlam) | ✅ Arama özetinden | Önerdikleri yöntem (görsel dikkat ile arama alanını daraltma + CNN) %88,9 tespit oranı, %34,8 kesinlik; Faster R-CNN biraz daha düşük. **PDF bu oturumda okunmadı**; rapora girmeden önce makaleden doğrulanacak. |
| Barındırma | ⚠️ Okunamadı | IPSAR (FESB, Split Üniversitesi): `http://ipsar.fesb.unist.hr/HERIDAL%20database.html`. 25 Kasım 2026'da iki denemede bağlantı sıfırlandı (ECONNRESET). |
| **Erişim / lisans** | ❌ **Doğrulanmadı** | Orijinal sayfa okunamadığı için HERIDAL'ın kendi kullanım koşulları bilinmiyor. Aramada "yalnızca akademik araştırma; yeniden dağıtım, değiştirme ve ticari kullanım izinsiz yasak" koşullu bir erişim formu çıktı, ama **HERIDAL'a ait olduğu doğrulanamadı.** |
| Türev kopya | ✅ Doğrulandı (Zenodo sayfası) | Pyrrö (Aalto Üniversitesi), "HERIDAL dataset in keras-retinanet PASCAL VOC format", DOI: 10.5281/zenodo.5662351, 2021, 8,3 GB, **CC BY 3.0 Unported**. Açıklama: "Modified version of the HERIDAL dataset". Bu lisans **türev için** verilmiş; orijinal HERIDAL'ın lisansını belirtmiyor. |
| İçerik | ⚠️ Kısmen | 3.229 kişi etiketi (2.892 eğitim, 337 test) [Pyrrö vd., "Rethinking Drone-Based Search and Rescue with Aerial Person Detection", arXiv:2111.09406, 2021 — sayı arama özetinden, yazar listesi sayfadan okunmadı]. "68.750'den fazla görüntü parçası" [Gotovac vd., *Remote Sensing* 12(20):3295, 2020 — arama özetinden]. **Parça boyutu, pozitif/negatif parça sayıları ve görüntü çözünürlüğü doğrulanmadı**; IJCV makalesinden alınacak. |

**Kararlar (öneri):**
1. Kullanıcı IPSAR sayfasını tarayıcıdan açar (bizim bağlantımız sıfırlandı); koşullar okunur ve buraya alıntılanır. Sayfa açılmazsa yazarlara e-posta.
2. **Koşullar netleşmeden veri indirilmez.** Repoya hiçbir HERIDAL görüntüsü ve model ağırlığı konmaz; yalnızca dosya yolları/kimlikleri (`.gitignore`).
3. Zenodo türevi (CC BY 3.0) yedek seçenektir; orijinal koşullarla çelişmediği doğrulanmadan kullanılmaz.

### A7.2 Yöntem: parça sınıflandırma, transfer öğrenme, açıklanabilirlik

- **Görev:** görüntü parçasında kişi **var / yok** ikili sınıflandırması. Nesne tespiti (kutu) yerine sınıflandırma, çünkü sensör modeli hücre başına bir karar ister (A7.3) ve hesap maliyeti düşüktür.
- **Modeller (karşılaştırma):** ImageNet ön eğitimli **ResNet-50**, **DenseNet-121** ve **ViT-B/16**. Seçim **bizim seçimimiz** (yaygın, hazır ağırlıkları var); HERIDAL üzerinde sınıflandırma yapan çalışmalar ayrıca taranıp ilgili çalışma olarak eklenecek.
- **Transfer öğrenme:** iki düzey karşılaştırılır: (1) gövde dondurulur, yalnız sınıflandırıcı eğitilir; (2) ince ayar (tüm ağ). Öğrenme oranı, dönem sayısı, veri artırma: **test ayarı** (kaynaklı değer bulunursa güncellenir).
- **Değerlendirme kümeleri:** HERIDAL'ın kendi eğitim/test ayrımı; doğrulama kümesi eğitimden ayrılır (oran test ayarı). Test kümesi model seçiminde kullanılmaz. Sınıf dengesizliği raporlanır.
- **Açıklanabilirlik:** CNN'ler için **Grad-CAM** (Selvaraju vd., ICCV 2017); ViT için Grad-CAM uyarlaması ya da attention rollout (Abnar & Zuidema, 2020). *Künyeler bu oturumda doğrulanmadı.* Amaç: modelin kişiye mi arka plana mı baktığını göstermek ve yanlış alarmların nedenini incelemek.
- **Ortam:** eğitim Google Colab (GPU); simülasyonda çıkarım yerel CPU'da (yeterli hız ölçülecek). Kütüphaneler yalnızca bu modülde: PyTorch, torchvision, timm (ViT), pytorch-grad-cam.
- **Modül:** `detection/` (repo içinde, ayrı paket). `swarm_core` `detection`'ı import etmez; `detection` da `swarm_core`'u import etmez. Planlanan dosyalar: `detection/heridal.py` (parça yükleyici), `train.py`, `evaluate.py`, `explain.py` (Grad-CAM), `sensor.py` (`classify(parça) → (etiket, güven)`), `notebooks/train_colab.ipynb`.

### A7.3 Simülasyona bağlama: veri setine dayalı sensör simülasyonu

1. **Hücreler:** alan hücrelere bölünür. Hücre boyutu tarama genişliğiyle (3 m) uyumlu seçilir. ⚠️ HERIDAL parçasının yerde kapladığı alan (yer örnekleme aralığı × piksel) ve çekim irtifası bilinmeden kesinleşmez; uçuş irtifamız 2,5 m (PX4 varsayılanı) HERIDAL'ın çekim irtifasından çok farklı olabilir → **sınırlılık olarak yazılır.** Hücre boyutu şimdilik test ayarı.
2. **Parça eşleme:** her hücreye HERIDAL **test** kümesinden gerçek bir parça eşlenir: kişi yerleştirilen hücrelere pozitif, diğerlerine negatif parça. Eğitimde görülen parçalar kullanılmaz (veri sızıntısı olmaması için).
3. **Kişi yerleşimi:** ⚠️ **Deney tasarımı — kaynak değil, bizim seçimimiz.** Kişi sayısı ve konumları tohumla rastgele (engel içi hariç); tohum ve sayı test ayarı.
4. **Tarama:** İHA'nın 3 m tarama izi bir hücreyle kesiştiğinde o hücrenin parçası gerçek modele verilir. Her hücre bir kez değerlendirilir.
5. **Karar:** güven ≥ eşik ise (eşik doğrulama kümesinin ROC eğrisinden seçilir; test ayarı) `person_detected` olayı gönderilir ve o nokta için bir **doğrulama görevi** oluşturulur (`confirm_task_created`, A0.0.5). Görev CBBA'ya **dinamik görev** olarak eklenir ve A5'teki dinamik ekleme/yeniden atama mekanizmasıyla atanır. Yer gerçeği bilindiği için her tespit doğru/yanlış alarm olarak işaretlenir.
6. Python deneyleri (Gazebo'suz) ve Gazebo gösterimi **aynı sensör modülünü** kullanır.
- **Neden Gazebo kamerası değil:** Gazebo sahnesinde kişi modeli ve gerçekçi arazi yok; sentetik kamera görüntüsü modeli anlamlı biçimde sınamaz. Veri setine dayalı sensör, gerçek hava görüntüsü kullanır. **Sınırlılık:** parçalar sahnenin geometrisi ve aydınlatmasıyla tutarlı değildir.

### A7.4 Görev modeli: doğrulama görevi (nokta görev)

- `swarm_core/models.py`'deki `Task`'a **tür** alanı planlanır: `kind = "sweep"` (varsayılan; mevcut kod değişmeden çalışır) veya `"confirm"`.
- Doğrulama görevinin `waypoints` listesi tek noktadır (başlangıç = bitiş). K11 ("sıfır uzunluklu görev nokta görev gibi işlenir") sayesinde CBBA'da ayrı bir yol gerekmez.
- Kimlikler 1000'den başlar (A0.0.5; arayüz ayarı).
- **Açık karar (K17, MAKALEDE YOK):** doğrulama görevinin ödülü (`c̄_j`; tarama görevleri için 1, K3) ve noktada bekleme süresi.
- Kod A7 entegrasyonunda (A3 sonrası) yazılır; şimdi `models.py` değişmez.

### A7.5 Metrikler

- **Sınıflandırma** (HERIDAL test kümesi, model başına): doğruluk, kesinlik, duyarlılık, F1; ek olarak karışıklık matrisi, ROC-AUC, parametre sayısı ve parça başına çıkarım süresi.
- **Görev düzeyi** (simülasyon):
  - **İlk tespit süresi:** görev başlangıcından ilk doğru `person_detected` olayına kadar geçen süre.
  - **Yanlış alarm başına boşa giden uçuş süresi:** yanlış alarm için oluşturulan doğrulama görevine harcanan geçiş + bekleme süresi, yanlış alarm sayısına bölünür.
  - Ek: bütün kişilerin bulunma süresi, kaçırılan kişi sayısı, toplam görev süresine etkisi.
- Kesin tanımlar A5 metrikleriyle birlikte yazılır.

### A7.6 Sıra ve süre

| İş | Ne zaman | Bağımlılık |
|---|---|---|
| HERIDAL erişim/lisans netleştirme | **Hemen** (yan hat) | Kullanıcı: IPSAR sayfası / yazarlara e-posta |
| Literatür: HERIDAL'da sınıflandırma çalışmaları; Grad-CAM ve ViT açıklanabilirlik künyeleri | Yan hat | — |
| Veri hazırlığı, eğitim, model karşılaştırması, Grad-CAM (Colab) | Yan hat, CBBA A1–A3 ile paralel | Lisans |
| Sensör simülasyonu, doğrulama görevi, `person_detected` / `confirm_task_created` gönderimi | **CBBA A3'ten sonra**, A5 dinamik ekleme ile birlikte | A3, A5 |
| Panelde "Tespitler" sekmesi/kartı | Entegrasyonla | A0.1 |

**Kaba süre tahmini:** yan hat ≈ 5–7 iş günü (Colab GPU süresine bağlı), entegrasyon ≈ 2–3 iş günü.

### A7.7 Açık kararlar

| # | Konu |
|---|---|
| 1 | HERIDAL kullanım koşulları (A7.1) — **engelleyici** |
| 2 | Hücre boyutu ve HERIDAL çekim irtifası / yer örnekleme aralığı uyumu |
| 3 | Kişi sayısı ve yerleşim (deney tasarımı) |
| 4 | Karar eşiği |
| 5 | Doğrulama görevi ödülü ve bekleme süresi (K17) |
| 6 | Kesin model listesi ve eğitim ayarları |
