# Anlatım Notları

Her özellik için dört madde: **ne yapıyor**, **neden**, **veri nereden**, **hocaya nasıl anlatırım**.
Yeni özellikler eklendikçe bu dosyanın sonuna yazılır.

---

## Adım 1 — AC10_0000 Gazebo sahnesi (25 Kasım 2026)

### 1.1 Senaryodan otomatik Gazebo dünyası (`swarm_viz/make_world.py`)
- **Ne yapıyor:** `scenarios/AC10_0000.json` dosyasını okuyup Gazebo dünyası üretiyor: koyu zemin, beyaz alan sınırı ve her görev için zeminde ince gri bir tarama şeridi (107 şerit).
- **Neden:** Hoca İHA'nın 3D görüntüde nereye gittiğini görmek istiyor. Bunun için önce görevlerin sahnede görünmesi gerekiyor. Elle çizilmiş bir sahne yerine veri setinden üretildiği için her senaryo aynı komutla yeniden üretilebilir.
- **Veri nereden:** Şeritler ve sınır CoverageTasks veri setinden (Grøntved vd., ICAR 2023), `swarm_core/dataset.py` ile okunuyor. Fizik, GPS başlangıç noktası, manyetik alan ve ışık PX4'ün kendi `default.sdf` dosyasından okunarak kopyalanıyor; PX4 dosyasına yazılmıyor.
- **Hocaya nasıl anlatırım:** "Gazebo'daki gri çizgiler, makalede kullanılan veri setindeki görevlerin kendisi. Program veri setini okuyup sahneyi otomatik kuruyor; ben elle bir şey çizmedim. Veri setinin (0,0) noktası Gazebo'nun (0,0) noktasıyla aynı, bu yüzden İHA bir şeridi uçtuğunda tam o gri çizginin üzerinden geçiyor."

### 1.2 Engeller: 1 m beton bloklar, 0,5 m içeriden, çarpışmasız
- **Ne yapıyor:** Veri setindeki 10 engeli 1 m yüksekliğinde beton blok olarak çiziyor. Bloklar 0,5 m içeriden çiziliyor ve çarpışma (collision) tanımları yok.
- **Neden:** Şeritlerin bir kısmı engel kenarlarının tam üzerinden geçiyor; blok tam boyutta çizilseydi o şeritler bloğun altında kalırdı. 1 m, uçuş irtifasının (2,5 m) altında. Çarpışma olmadığı için bloklar uçuşu etkilemiyor, yalnızca görsel. Bu üç değer "görselleştirme ayarı" olarak işaretli (`swarm_viz/viz_config.py`), deney parametresi değil.
- **Veri nereden:** Engel poligonları veri setinden. Küçültme `shapely` ile yapılıyor (`buffer(-0,5)`). Veri setinin geometrisi değişmiyor, yalnızca çizim küçük.
- **Hocaya nasıl anlatırım:** "Bloklar veri setindeki engellerin yeri ve şekli. Biraz küçük çizdim ki kenarlarındaki görev şeritleri görünsün. Fiziksel engel değiller; engelden kaçınma bir sonraki adımda yol planlamasıyla yapılıyor, Gazebo'daki çarpışmayla değil."

### 1.3 Sabit çapraz-üst kamera (`worlds/ac10_0000.gui.config`)
- **Ne yapıyor:** Gazebo açıldığında kamera alanın güneybatısında, 80 m yükseklikte durup alanın merkezine bakıyor; 100 × 100 m alanın tamamı görünüyor. PX4'ün kamerayı İHA'ya kilitlemesi `PX4_GZ_NO_FOLLOW=1` ile kapatılıyor.
- **Neden:** PX4 varsayılan olarak kamerayı İHA'nın arkasına kilitliyor; o zaman tarama düzeni ve İHA'ların alandaki yeri görünmüyor. Sunumda bütün alanın aynı anda görünmesi gerekiyor.
- **Veri nereden:** Kamera konumu alan sınırından hesaplanıyor (merkez + `CAMERA_OFFSET_M`, görselleştirme ayarı). GUI'nin geri kalanı Gazebo'nun kendi varsayılan ayar dosyasından aynen alınıyor.
- **Hocaya nasıl anlatırım:** "Kamera sabit ve bütün alanı gösteriyor. İHA'yı takip etmediği için hangi İHA'nın alanın neresinde olduğu tek bakışta görünüyor."

### 1.4 PX4'ü bozmadan kendi dünyamızı yükleme
- **Ne yapıyor:** Önce Gazebo bizim dünyamızla başlatılıyor, sonra PX4 her zamanki komutla çalıştırılıyor. PX4 çalışan dünyayı bulup İHA'yı o dünyanın (0,0) noktasına yerleştiriyor.
- **Neden:** PX4'ün başlatma betiği dünya klasörünü kendi klasörüne sabitliyor. PX4 dosyalarını değiştirmek yerine betiğin "Gazebo zaten çalışıyorsa ona bağlan" davranışını kullanıyoruz. Eski yöntem (`make px4_sitl gz_x500`, varsayılan dünya) hiç değişmeden çalışmaya devam ediyor.
- **Veri nereden:** PX4'ün `px4-rc.gzsim` betiği ("gazebo already running world" dalı) ve `gz_env.sh` dosyası (PX4 eklentilerinin yolu). İkisi de yalnızca okunuyor.
- **Hocaya nasıl anlatırım:** "PX4'ün kaynak koduna dokunmadım. Gazebo'yu kendi sahnemle başlatıyorum, PX4 de çalışan sahneye bağlanıyor. Bu, PX4'ün desteklediği bir yöntem."

### 1.5 Hizalama doğrulaması (26 Kasım 2026)
- **Ne yapıyor:** AC10_0000 görev 1–4 uçuşunun PX4 logundan (`rootfs/fs/log/2026-11-26/10_00_36.ulg`), İHA'nın her şeritten yanal sapmasını (çizgiye dik uzaklık) ölçüyor. İki konum karşılaştırıldı: Gazebo'nun gerçek konumu (groundtruth) ve PX4'ün kendi tahmini (EKF).
- **Neden:** Kameradan İHA birkaç piksel göründüğü için "şeridin üstünde mi?" sorusu gözle cevaplanamıyordu. Sayıyla gösterince sahnedeki çizgilerin İHA'nın uçtuğu yerle aynı koordinatta olduğu kanıtlanmış oluyor.
- **Veri nereden:** PX4 uçuş logu (`vehicle_global_position_groundtruth`, `vehicle_local_position`); şerit çizgileri veri setinden. Kalkıştan önce gerçek konum (0,000, 0,000) m, yani İHA tam veri setinin (0,0) noktasında başlıyor.

  | Görev | Uzunluk | Ort. yanal sapma (gerçek) | En büyük (gerçek) | İlk 1 m sonrası en büyük |
  |---|---|---|---|---|
  | 1 | 10,72 m | 0,092 m | 0,174 m | 0,096 m |
  | 2 | 28,70 m | 0,047 m | 0,093 m | 0,079 m |
  | 3 | 26,06 m | 0,074 m | 0,424 m | 0,092 m |
  | 4 | 23,42 m | 0,033 m | 0,061 m | 0,061 m |

  En büyük değerler şeridin ilk 0,5 m'sinde: İHA şerit başına 0,3 m varış toleransıyla (`fly_task.py`, test ayarı) varıyor, sonra çizgiye oturuyor.
- **Hocaya nasıl anlatırım:** "Uçuş kaydından ölçtüm: İHA şerit çizgisinden ortalama 3–9 cm, en fazla 42 cm sapıyor; en büyük sapma da yalnızca şeridin başında. Tarama genişliği 3 m olduğu için bu sapma kapsamayı etkilemiyor. Sahnedeki çizgiler ile İHA'nın gerçek yolu aynı koordinat sisteminde."
