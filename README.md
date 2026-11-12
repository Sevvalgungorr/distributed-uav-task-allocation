
# Sürü İHA'lar İçin Dağıtık Görev Paylaşımı

## 1. Proje Hakkında

Bu proje, birden fazla insansız hava aracının (İHA) merkezi bir görev dağıtım sistemine ihtiyaç duymadan görevleri kendi aralarında paylaşabilmesini amaçlayan bir bilgisayar mühendisliği bitirme projesidir.

Proje kapsamında sürü hâlindeki İHA'ların arama-kurtarma ve alan tarama gibi görevlerde dağıtık karar verme mekanizmalarıyla koordineli çalışması hedeflenmektedir.

Görev dağılımında İHA'ların konumları, görev noktalarına uzaklıkları, enerji seviyeleri ve görev öncelikleri dikkate alınacaktır. Ayrıca iletişim kesintisi, lider kaybı ve düşük pil seviyesi gibi durumlarda sistemin görevleri yeniden düzenleyebilmesi amaçlanmaktadır.

Geliştirilen yöntemlerin simülasyon ortamında test edilmesi ve performanslarının değerlendirilmesi planlanmaktadır.

## 2. Projenin Amaçları

- Merkezi bir görev dağıtım mekanizmasına bağımlı olmayan sürü İHA sistemi geliştirmek.
- CBBA (Consensus-Based Bundle Algorithm) kullanarak dağıtık görev paylaşımı gerçekleştirmek.
- İHA'ların konum, mesafe, enerji ve görev önceliklerine göre karar vermesini sağlamak.
- Yeni görevlerin sisteme dinamik olarak eklenebilmesini sağlamak.
- Düşük pil veya İHA kaybı durumunda görevlerin yeniden dağıtılmasını sağlamak.
- Lider seçimi ve iletişim kesintisi senaryolarını incelemek.
- Formasyon kontrolü ve çarpışma önleme yöntemleri geliştirmek.
- Sistemi ROS 2 ve Gazebo tabanlı simülasyon ortamında test etmek.
- Görev tamamlama süresi, alan kapsama oranı, enerji tüketimi ve iletişim performansı gibi ölçütleri değerlendirmek.

## 3. Planlanan Sistem Mimarisi

Proje, birbirinden bağımsız geliştirilebilen ve birlikte çalışabilen modüllerden oluşacak şekilde tasarlanmaktadır.

### 3.1. İHA Veri Modeli

Her İHA için aşağıdaki bilgilerin tutulması planlanmaktadır:

- İHA kimliği
- Konum bilgisi
- Enerji seviyesi
- Liderlik durumu
- Atanan görevler
- Görev ve uçuş durumu

### 3.2. Dağıtık Görev Paylaşımı

CBBA algoritması kullanılarak İHA'ların görevler için teklif oluşturması ve kendi aralarında bilgi paylaşarak görev dağılımında uzlaşması hedeflenmektedir.

Görev paylaşımında mesafe, enerji durumu ve görev önceliği gibi parametreler değerlendirilecektir.

### 3.3. Dinamik Görev Yönetimi

Sistem çalışırken yeni görevlerin eklenmesi, mevcut görevlerin güncellenmesi ve gerektiğinde görevlerin başka İHA'lara aktarılması planlanmaktadır.

### 3.4. Lider Seçimi ve İletişim Yönetimi

Sürü içerisindeki koordinasyon işlemleri için lider seçimi mekanizması geliştirilecektir.

Lider, merkezi görev dağıtım noktası olarak kullanılmayacak; görev paylaşımının dağıtık yapısı korunacaktır.

Lider kaybı ve iletişim kesintisi gibi durumların sistem üzerindeki etkileri test edilecektir.

### 3.5. Enerji Yönetimi

İHA'ların pil seviyeleri takip edilerek görev dağılımında enerji durumu dikkate alınacaktır.

Enerjisi azalan bir İHA'nın görevlerini uygun başka bir İHA'ya devredebilmesi hedeflenmektedir.

### 3.6. Formasyon ve Çarpışma Önleme

İHA'ların koordineli hareket edebilmesi için formasyon kontrolü ve çarpışma önleme yöntemleri değerlendirilecektir.

### 3.7. Simülasyon ve Haberleşme

Geliştirilen algoritmaların ROS 2 ve Gazebo ortamına entegre edilmesi planlanmaktadır.

MAVLink protokolü üzerinden İHA kontrolü ve haberleşme süreçlerinin simülasyon ortamında incelenmesi hedeflenmektedir.

## 4. Başlangıç Görev Senaryosu

İlk geliştirme ve test aşamalarında aşağıdaki senaryo esas alınacaktır:

| Parametre | Değer |
|-----------|-------|
| İHA sayısı | 5 |
| Görev alanı | 500 × 400 metre |
| Bölge sayısı | 20 |
| Bölge boyutu | 100 × 100 metre |
| Görev türü | Alan tarama |
| Görev paylaşımı | Dağıtık (CBBA - planlanan) |

Görev alanı 20 bölgeye ayrılarak İHA'ların bu bölgeleri paylaşması ve taraması hedeflenmektedir.

İlerleyen aşamalarda farklı İHA sayıları, dinamik görevler, enerji kısıtları ve iletişim kesintileri kullanılarak ek testler gerçekleştirilecektir.

Senaryo parametrelerinin algoritmalardan bağımsız olarak değiştirilebilir olması hedeflenmektedir.

## 5. Kullanılacak Teknolojiler

| Teknoloji | Kullanım Amacı |
|-----------|----------------|
| Python | Temel algoritmalar ve sistem geliştirme |
| ROS 2 | Robotik yazılım bileşenleri ve haberleşme |
| Gazebo | Simülasyon ortamı |
| MAVLink | İHA haberleşmesi ve kontrolü |
| Git / GitHub | Sürüm kontrolü ve proje takibi |
| Ubuntu | Geliştirme ortamı |

**Not:** Python tabanlı geliştirme ortamı hazırlanmıştır. ROS 2, Gazebo ve MAVLink entegrasyonları ilerleyen aşamalarda gerçekleştirilecektir.

## 6. Mevcut Proje Yapısı

```text
suruiha/
│
├── swarm_core/
│   └── models.py           # İHA modeli ve mesafe hesaplama
│
├── swarm_sim/              # Simülasyon bileşenleri için ayrılan klasör
│
├── scenarios/              # Görev senaryoları için ayrılan klasör
│
├── tests/                  # Test dosyaları için ayrılan klasör
│
├── docs/                   # Teknik dokümantasyon için ayrılan klasör
│
├── main.py                 # Ana uygulama
├── README.md               # Proje dokümantasyonu
└── .gitignore              # Git tarafından hariç tutulan dosyalar
```

Proje yapısı geliştirme sürecinde yeni modüller eklenerek genişletilecektir.

## 7. Geliştirme Aşamaları

### v0.1 - Temel Veri Modelleri
- [x] Geliştirme ortamının hazırlanması
- [x] Proje klasör yapısının oluşturulması
- [x] Temel İHA sınıfının oluşturulması
- [x] İki İHA arasındaki mesafenin hesaplanması
- [ ] Görev veri modelinin oluşturulması

### v0.2 - Alan Tarama
- [ ] Görev alanının bölgelere ayrılması
- [ ] Tek İHA ile alan tarama algoritmasının geliştirilmesi
- [ ] Zigzag tarama rotasının oluşturulması

### v0.3 - Dağıtık Görev Paylaşımı
- [ ] CBBA algoritmasının geliştirilmesi
- [ ] Birden fazla İHA arasında görev paylaşımı
- [ ] Görev dağılımının doğrulanması

### v0.4 - Dinamik Olaylar ve Koordinasyon
- [ ] Yeni görevlerin sisteme eklenmesi
- [ ] Düşük enerji durumunda görev devri
- [ ] Lider seçimi ve lider kaybı senaryoları
- [ ] İletişim kesintisi senaryoları

### v0.5 - Sürü Hareketi
- [ ] Formasyon kontrolü
- [ ] Çarpışma önleme
- [ ] Koordineli hareket testleri

### v0.6 - Simülasyon Entegrasyonu
- [ ] ROS 2 entegrasyonu
- [ ] Gazebo simülasyon ortamının hazırlanması
- [ ] MAVLink haberleşme entegrasyonu
- [ ] Çoklu İHA simülasyon testleri

### v1.0 - Test ve Performans Değerlendirmesi
- [ ] Farklı İHA sayılarıyla testler
- [ ] Görev tamamlama süresi analizi
- [ ] Alan kapsama oranının ölçülmesi
- [ ] Enerji tüketiminin değerlendirilmesi
- [ ] Çarpışma ve iletişim senaryolarının incelenmesi
- [ ] Alternatif görev paylaşım yöntemleriyle karşılaştırma
- [ ] Sonuçların raporlanması

Bu sürümler geliştirme hedeflerini temsil etmektedir. Uygulama sırası ve kapsamı test sonuçlarına göre güncellenebilir.

## 8. Kurulum ve Çalıştırma

### Gereksinimler

- Ubuntu 24.04 LTS
- Python 3.12

### Sanal Ortamın Etkinleştirilmesi

Proje ana dizininde:

```bash
source .venv/bin/activate
```

Sanal ortam henüz oluşturulmamışsa:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Uygulamayı Çalıştırma

```bash
python main.py
```

Mevcut uygulama, temel İHA nesnelerini oluşturarak aralarındaki Öklid uzaklığını hesaplamaktadır.

Geliştirme ilerledikçe kurulum ve çalıştırma adımları güncellenecektir.

## 9. Performans Değerlendirmesi

Projenin başarısını değerlendirmek amacıyla aşağıdaki ölçütlerin kullanılması planlanmaktadır:

- Görev tamamlama süresi
- Alan kapsama oranı
- Görev paylaşımının doğruluğu
- İHA başına enerji tüketimi
- Görev yeniden dağıtım süresi
- Çarpışma sayısı
- İletişim kesintilerine dayanıklılık
- Farklı sürü büyüklüklerindeki performans

CBBA tabanlı yöntemin performansının, merkezi veya alternatif görev paylaşım yaklaşımlarıyla karşılaştırılması hedeflenmektedir.

## 10. Proje Durumu

**Aktif geliştirme aşamasındadır.**

Şu anda temel İHA veri modeli ve mesafe hesaplama işlemleri tamamlanmıştır. Sonraki aşamada görev modelinin oluşturulması ve alan tarama algoritmasının geliştirilmesi planlanmaktadır.

Bu README dosyası, proje geliştikçe güncellenecektir.

## 11. Akademik Bilgiler

**Proje Türü:** Bilgisayar Mühendisliği Bitirme Projesi

**Üniversite:** Kırıkkale Üniversitesi

**Danışman:** Enes Ayan

**Akademik Yıl:** 2026-2027
