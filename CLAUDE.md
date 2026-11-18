# Sürü İHA Bitirme Projesi — Claude İçin Proje Devam Notları
**Son durum: 18 Kasım 2026**

## 1. Projenin amacı

Kırıkkale Üniversitesi Bilgisayar Mühendisliği 4. sınıf öğrencisiyim. Bitirme projemin konusu:

**Sürü İHA'lar İçin Dağıtık Görev Paylaşımı Algoritması**

Projenin amacı, birden fazla insansız hava aracının (İHA) merkezi bir kontrol birimine bağlı olmadan, kendi aralarında haberleşerek görevleri paylaşmasıdır.

Örnek uygulama alanları:
- Arama-kurtarma
- Alan tarama
- Keşif ve gözetleme
- Bir İHA devre dışı kaldığında görevlerin yeniden dağıtılması

Temel hedef yalnızca İHA'ları uçurmak değil, **dağıtık görev atama algoritması geliştirmek ve bunu simülasyonda göstermek.**

Planlanan temel algoritma: **CBBA (Consensus-Based Bundle Algorithm)**. Bu algoritma, İHA'ların görevler için teklif oluşturmasını ve dağıtık şekilde uzlaşarak görevleri paylaşmasını sağlar.

Ayrıca lider seçimi ve iletişim kesintisi gibi durumları incelemek istiyoruz. Ancak bunların ayrıntılı tasarımı henüz tamamlanmadı.

## 2. Danışman hocanın beklentileri

Danışmanım Enes Ayan.

Hocanın özellikle üzerinde durduğu iki konu var:

**1. Görsel simülasyon:** Projenin yalnızca terminalde çalışan bir Python uygulaması olmasını istemiyor. İHA'ların gerçekten hareket ettiğinin görülebildiği bir simülasyon bekliyor. Bunun için Gazebo ve PX4 kullanmaya başladık.

**2. Görevlerin akademik dayanağı:** Hoca, görevleri neden bizim belirlediğimizi ve literatürde tanımlı görev türleri veya standart senaryolar olup olmadığını sordu.

Bu nedenle görev tanımlarını ve senaryo parametrelerini rastgele seçmek istemiyorum. Akademik yayınlara dayalı, gerekçelendirilebilir bir yapı oluşturmak istiyorum.

İncelenmesi önerilen temel çalışmalar:
- Gerkey & Matarić (2004): *A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems*
- Choi, Brunet & How (2009): *Consensus-Based Decentralized Auctions for Robust Task Allocation*

Bu çalışmaların kullanacağımız görev tanımları ve deney parametreleriyle ilişkisi ayrıca doğrulanmalı.

**Önemli:** Mevcut 20 görev, 5 İHA, 500 × 400 metre alan ve 20 metre tarama aralığı henüz akademik olarak doğrulanmış standartlar değil. İlk prototip için seçilmiş örnek değerler.

## 3. GitHub ve geliştirme ortamı

GitHub deposu:
https://github.com/Sevvalgungorr/distributed-uav-task-allocation

Geliştirme ortamı:
- Windows 11
- WSL2 üzerinde Ubuntu 24.04.5 LTS
- Visual Studio Code, WSL bağlantısıyla
- Python 3.12
- Python sanal ortamı: `.venv`
- Git
- CMake
- Gazebo Harmonic
- PX4-Autopilot
- MAVSDK Python 4.2.0

Ana proje dizini: `/home/sevval/suruiha`

PX4 dizini: `/home/sevval/PX4-Autopilot`

PX4, bitirme projesinin dışında ayrı bir klasöre kuruldu.

## 4. Mevcut proje dosyaları

```text
suruiha/
├── swarm_core/
│   ├── models.py
│   ├── coverage.py
│   └── tasks.py
├── swarm_sim/
├── scenarios/
│   └── h1.json
├── docs/
├── tests/
│   ├── test_coverage.py
│   └── test_task.py
├── main.py
├── CLAUDE.md
├── README.md
├── .gitignore
└── .venv/
```

### models.py

İki temel veri modeli oluşturuldu:

**UAV**
- `uav_id`
- `x`
- `y`
- `battery = 100.0`
- `is_leader = False`
- `distance_to()` fonksiyonu

**Task**
- `task_id`
- `x`
- `y`
- `priority = 1`
- `status = "OPEN"`
- `waypoints = []`

### tasks.py

`create_tasks()` fonksiyonu oluşturuldu.

Mevcut örnek senaryo:
- 500 × 400 metre alan
- 100 × 100 metrelik bölgeler
- 5 sütun, 4 satır
- Toplam 20 görev

Bölge merkezleri örneğin `(50,50)`, `(150,50)` şeklinde hesaplanıyor.

### coverage.py

`generate_zigzag()` fonksiyonu oluşturuldu.

Bir bölgeyi zikzak şeklinde taramak için waypoint noktaları üretiyor.

Mevcut örnek:
- Bölge boyutu: 100 metre
- Tarama çizgileri arası mesafe: 20 metre
- 5 paralel tarama çizgisi
- Toplam 10 waypoint

Bu tarama aralığının gerçek sensör özelliklerine göre gerekçelendirilmesi gerekiyor.

### main.py

Şu anda:
- 5 İHA oluşturuyor.
- 20 görev oluşturuyor.
- Görevleri terminalde gösteriyor.

Henüz gerçek CBBA görev atama algoritması tamamlanmadı.

### Testler

`pytest` kullanıyoruz. Son bilinen durumda 5 test başarıyla geçti.

Test komutu:

```bash
cd ~/suruiha
source .venv/bin/activate
python -m pytest tests/ -v
```

Son bilinen Git commit: `f357ce3` — `refactor: organize task generation and improve coverage paths`

Bu commit GitHub'a gönderildi. Daha sonraki yerel değişiklikler varsa Git durumuyla kontrol edilmeli.

## 5. Gazebo kurulumu — TAMAMLANDI

Gazebo Harmonic, Ubuntu WSL2 üzerine kuruldu. Windows üzerinde WSLg sayesinde Gazebo'nun grafik arayüzü açılabiliyor.

`gz sim -v 4 empty.sdf` komutuyla Gazebo arayüzünün çalıştığı doğrulandı. Ardından PX4 ile Gazebo bağlantısı kuruldu.

## 6. PX4 kurulumu — ÇALIŞIYOR

PX4-Autopilot GitHub'dan indirildi. Kurulum sırasında eksik bağımlılıklar nedeniyle hatalar alındı ve sırayla giderildi (`ccache`, `cyclonedds-tools`, `python3-kconfiglib`, `python3-empy`, `pyros-genmsg`, `libopencv-dev`, Python `lark` modülü). Bazı `apt` işlemlerinde IPv4 zorlaması kullanıldı.

PX4'ü çalıştıran komut:

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

**Bu komut başarıyla çalıştı.** Gazebo'da `x500_0` isimli bir quadcopter göründü ve PX4 terminalinde `pxh>` komut ekranı açıldı.

Görülen uyarılar:
- `Preflight Fail: No connection to the GCS`
- `Preflight Fail: No heading reference`
- `Preflight Fail: height estimate not stable`

Bu uyarılar henüz tamamen incelenmedi. Güvenli arm/takeoff henüz doğrulanmadı.

**Önemli:** `pxh>` terminali Ubuntu Bash terminali değildir. `cd`, `python3` gibi Linux komutları burada çalışmaz. Bunun için VS Code'da yeni Bash terminali açılmalıdır.

## 7. MAVSDK kurulumu — TAMAMLANDI

MAVSDK proje sanal ortamına kuruldu (`python -m pip install mavsdk`), sürüm **4.2.0**. `python -c "import mavsdk; print('MAVSDK hazir')"` komutu başarılı.

**MAVSDK ile PX4 arasında gerçek bağlantı testi henüz yapılmadı.**

## 8. TAM OLARAK NEREDE KALDIK?

Sıradaki işlem: `swarm_sim/connect_uav.py` dosyasını oluşturmak.

İlk bağlantı testi için planlanan kod:

```python
import asyncio
from mavsdk import System


async def main():
    drone = System()

    print("IHA'ya baglaniliyor...")
    await drone.connect(system_address="udp://:14540")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("IHA baglantisi basarili!")
            break


if __name__ == "__main__":
    asyncio.run(main())
```

Çalıştırılması planlanan komut:

```bash
cd ~/suruiha
source .venv/bin/activate
python -m swarm_sim.connect_uav
```

Amaç, Gazebo'daki `x500` İHA'sının PX4 üzerinden MAVSDK'ye bağlanabildiğini doğrulamak. Bağlantı kurulmazsa MAVLink UDP portları ve PX4 yapılandırması kontrol edilmeli.

## 9. Bundan sonraki teknik yol haritası

**Aşama 1 — Tek İHA bağlantısı:** PX4 ve Gazebo'yu yeniden başlatmak, MAVSDK bağlantısını test etmek, konum ve sağlık durumunu okumak, kontrollü kalkış ve iniş.

**Aşama 2 — Çoklu İHA simülasyonu:** Gazebo'da birden fazla x500, her İHA için ayrı PX4 örneği, Python'dan her İHA'yı ayrı kontrol. Önce 2–3 İHA, sonra 5 İHA.

**Aşama 3 — Dağıtık görev atama:** CBBA'yı Python'da geliştirmek, teklif ve maliyet fonksiyonları, görev çakışmalarını engellemek, merkezi karar verici olmadan paylaşım, birim testleri.

**Aşama 4 — Gazebo entegrasyonu:** CBBA sonucunu İHA'lara aktarmak, waypoint noktalarına gitmek, görev tamamlanma durumunu izlemek.

**Aşama 5 — Deneyler:** Görev tamamlama süresi, alan kapsama oranı, İHA başına görev dağılımı, tahmini enerji tüketimi, iletişim kesintisinin etkisi, İHA devre dışı kalınca yeniden paylaşım. Metriklerin kesin tanımları ve deney koşulları henüz belirlenmedi.

## 10. Çalışma şeklimle ilgili önemli bilgiler

1. **Adım adım ilerle.** Aynı anda çok fazla komut veya işlem verme.
2. Bir komut verdiğinde önce çıktısını göndermemi bekle.
3. Kodları VS Code'a doğrudan yapıştırabileceğim şekilde, doğru dosya yollarıyla ver.
4. Gereksiz karmaşık mimariler kurma. Kararlı ve anlaşılır çözümler tercih et.
5. Mevcut proje dosyalarını ve GitHub geçmişini koru.
6. Kodları GitHub'a göndermeden önce test et.
7. Akademik konularda kaynak göster; görevleri ve senaryo parametrelerini uydurma.
8. Açıklamaları Türkçe, anlaşılır ve bilgisayar mühendisliği öğrencisine uygun yap.
9. Bitirme projesinin ana konusu **dağıtık görev paylaşımıdır**. Sadece İHA uçurma veya formasyon uçuşu projesine dönüşmemeli.
10. Mevcut Gazebo/PX4 kurulumunu gereksiz yere silme veya baştan kurdurma.

## 11. Danışman hocanın beklentisi

Hocanın akademik görev tanımlarıyla ilgili beklentisi sonraki aşamalarda mutlaka ele alınmalı.

## 12. Görev veri seti kararı (18 Kasım 2026)

Hocanın "görevlerin akademik dayanağı" sorusu için görevleri CoverageTasks veri setinden alıyoruz:
- Kaynak: Grøntved, Schultz, Christensen, "Decentralized Multi-UAV Trajectory Task Allocation in Search and Rescue Applications", ICAR 2023. DOI: 10.1109/icar58858.2023.10406912
- Veri seti: https://github.com/kasperg3/CoverageTasks (MIT lisansı, DOI: 10.5281/zenodo.7763104)
- Her görev bir tarama çizgisidir (iki nokta). İHA'nın çizgiyi hangi yönde uçacağı da atama sırasında seçilir.
- Başlangıç senaryosu: `scenarios/h1.json` (13 görev). Asıl deneyler için daha sonra AC300 kullanılacak.
- Eski 20 bölgelik örnek senaryo (`tasks.py`) silinmeyecek, şimdilik kalacak.
- Projenin katkısı: makalede olmayan iletişim kaybı, İHA arızası sonrası yeniden atama, lider seçimi ve batarya ile görev devri.