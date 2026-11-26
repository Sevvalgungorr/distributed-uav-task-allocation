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

### 1.6 Yakınlaştırılmış sabit kamera (26 Kasım 2026)
- **Ne yapıyor:** Kamerayı alanın güneyine, 45° eğimle koyuyor ve görüş açısını 60°'ye sabitliyor. Konumu elle değil hesapla seçiyor: alanın dört köşesi hem geniş ekranda (16:9) hem Gazebo'nun varsayılan pencere oranında ekrana sığacak en yakın nokta.
- **Neden:** Eski kamerada İHA birkaç piksel görünüyordu. Gazebo'nun varsayılan görüş açısı geniş (hesapla en az ~78°) ve her şeyi uzaktaymış gibi küçültüyor. Güneyden bakış kare alanı geniş ekrana daha iyi yerleştiriyor; aynı açıda çapraz bakıştan ~%30 daha yakın. Tahmini kazanç: İHA ~1,4 kat büyük. Alanın tamamı ekranda kaldıkça İHA yine küçük kalacak; asıl çözüm 3. adımdaki büyük renkli işaret.
- **Veri nereden:** Alan sınırı veri setinden; açı, eğim ve kenar payı `swarm_viz/viz_config.py`'de (görselleştirme ayarı). Basit iğne deliği kamera hesabı, testli (`test_camera_is_closest_pose_that_fits_whole_area`).
- **Hocaya nasıl anlatırım:** "Kamerayı göz kararı değil hesapla yerleştirdim: alanın tamamını gösteren en yakın nokta. Alan 100 m, İHA yarım metre; bu yüzden İHA'nın üstüne ayrıca büyük renkli bir işaret koyacağım."

### 1.7 Kamerayı sıfırlama betiği (`swarm_viz/reset_camera.py`)
- **Ne yapıyor:** Gazebo açıkken kamerayı, GUI ayar dosyasındaki sabit konuma geri götürüyor. Önce kamera takibini bırakıyor, sonra kamerayı o konuma taşıyor. Gazebo'yu yeniden başlatmak gerekmiyor.
- **Neden:** Gazebo'da bir İHA'ya yanlışlıkla "Move to" ya da "Follow" yapınca kamera İHA'ya yaklaşıyor ve sunumdaki bütün alan görünümü kayboluyor.
- **Veri nereden:** Konum, `make_world.py`'nin yazdığı `worlds/ac10_0000.gui.config` dosyasındaki `<camera_pose>`. İstek Gazebo'nun kendi servislerine (`/gui/follow`, `/gui/move_to/pose`) `gz service` aracıyla gönderiliyor. Betik İHA'ya ya da simülasyona hiçbir şey göndermiyor.
- **Hocaya nasıl anlatırım:** "Kamera bozulursa tek komutla sunum görünümüne dönüyorum; konum, dünyayı üreten programın hesapladığı değerle aynı."

---

## Adım 2 — Engellerden kaçınan geçiş yolları (K13) (26 Kasım 2026)

### 2.1 En kısa yol modülü (`swarm_core/environment.py`)
- **Ne yapıyor:** İki nokta arasında engellerin içinden geçmeyen en kısa yolu buluyor. Yol, engel köşelerinden geçen düz parçalardan oluşuyor; tıpkı bir odada masanın etrafından dolaşırken köşesine teğet geçmek gibi.
- **Neden:** CBBA'nın görev maliyetleri bu mesafeyle hesaplanacak. Makaledeki sonuçlarla karşılaştırma yapabilmek için yazarlarla aynı mesafe modelini kullanmamız gerekiyor. Uçuşta da İHA'nın engelin içinden geçmesi gerçekçi değil.
- **Veri nereden:** Yöntem yazarların kodundan [T23 main.py:71-77, CoverageProblem.py, CBBA.py:141]: alan sınırı %101 büyütülüyor, engeller %95 küçültülüyor, yol `extremitypathfinder` kütüphanesiyle (görünürlük grafiği) bulunuyor. Görünürlük grafiği, birbirini engelsiz gören köşelerin birbirine bağlandığı bir ağ; en kısa yol bu ağ üzerinde aranıyor.
- **Hocaya nasıl anlatırım:** "Mesafeyi düz çizgiyle değil, engellerden kaçınan en kısa yolla ölçüyorum; yazarlar da böyle yapmış, aynı kütüphane ve aynı ölçeklerle. Kontrol ederken yazarların yönteminde bir kusur buldum: girintili bir engelde iki görevin başlangıcı engelin birkaç cm içinde kalıyor ve kütüphane oradan engelin içinden geçen yol veriyor. Bunu düzelttim ve raporda bir bulgu olarak yazacağım."

### 2.2 Uçuşta engelden kaçınan geçişler (`swarm_sim/fly_task.py`)
- **Ne yapıyor:** İHA bir şeridi bitirip sıradakine giderken artık düz çizgi değil, engelden kaçınan yolu izliyor. Yolun her köşesinde duruyor, sonra sonraki köşeye devam ediyor. Şerit uçuşu değişmedi.
- **Neden:** Hocanın Gazebo'da görmek istediği "İHA nereye gidiyor" sorusunun cevabı bu yol. 3. adımda bu yol sahneye kesik çizgiyle çizilecek. Önceki uçuşta görev 1'den 2'ye geçerken İHA bir engelin köşesini kesiyordu (düz çizgi 38,36 m; yeni yol 39,23 m).
- **Veri nereden:** Geçişin başı bir önceki şeridin bitiş noktası (ilk geçişte kalkış noktası), sonu sıradaki şeridin başı; yol 2.1'deki modülden.
- **Hocaya nasıl anlatırım:** "Algoritmanın maliyet hesabında kullandığı yol ile İHA'nın Gazebo'da uçtuğu yol aynı fonksiyondan geliyor. Tek fark şu: gösterim uçuşunda İHA köşelerde duruyor; maliyet modelinde durmuyor. Bu yalnızca gösterimi yavaşlatıyor."

### 2.3 Geçişin uçuş logundan ölçümü (26 Kasım 2026)
- **Ne yapıyor:** Görev 1 bitişinden görev 2 başlangıcına geçişi iki uçuşta karşılaştırıyor: önceki düz çizgi (`10_00_36.ulg`) ve yeni engelden kaçınan yol (`10_36_00.ulg`). Konum Gazebo'nun gerçek konumu (groundtruth).
- **Sonuç:**

  | | Önceki (düz çizgi) | Yeni (K13) |
  |---|---|---|
  | Uçulan yol | 39,18 m, 16,7 s | 41,05 m, 21,6 s |
  | %95 küçültülmüş engelin (planlayıcının engeli) içinde kalan yol | **9,95 m** | **0,74 m** (köşede duruşta ~0,4 m yanal sapma) |
  | Planlanan köşeye en yakın geçiş | — | **0,055 m** |
  | Orijinal (veri seti) engelin içinde kalan yol | 12,49 m | 11,46 m |
  | Gazebo'da çizilen bloğun (0,5 m içeriden) içinde | 10,32 m | 4,00 m (planda 3,38 m) |

  Uçuş hatasız: arm → kalkış → offboard → iniş → "Disarmed by landing"; failsafe yok; uyarılar yalnızca arm öncesindeki bilinen açılış uyarıları.
- **Neden orijinal engelin içinde:** Görev 1 şeridi engel 5'in kenarının tam üzerinde (iki ucu engelin iki köşesi). Yazarların modelinde engel %95 küçültüldüğü için kenar boyunca ince bir izinli bant var; geçiş bu bantta, kenara paralel gidiyor. Bu, makaledeki mesafe modelinin kendisi.
- **Hocaya nasıl anlatırım:** "Yeni yolda İHA, algoritmanın kullandığı engelin içine neredeyse hiç girmiyor ve planlanan köşeden 5 cm geçiyor. Gazebo'daki blok farklı bir yöntemle küçültüldüğü için sivri köşede görüntüyle plan uyuşmuyordu; bunu çizimi planlayıcıyla aynı şekle getirerek düzelteceğim."
