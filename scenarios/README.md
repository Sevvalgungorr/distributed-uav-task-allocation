# Senaryolar

## h1.json

13 tarama görevi (her görev iki noktadan oluşan bir tarama çizgisi) içeren başlangıç senaryosu.

**Kaynak:** CoverageTasks veri seti
- Depo: https://github.com/kasperg3/CoverageTasks
- Lisans: MIT
- Veri seti DOI: [10.5281/zenodo.7763104](https://doi.org/10.5281/zenodo.7763104)

**Veri setini tanıtan makale:**
Grøntved, Lundquist, Christensen,
"Decentralized Multi-UAV Trajectory Task Allocation in Search and Rescue Applications",
*International Conference on Advanced Robotics (ICAR)*, 2023.
DOI: [10.1109/icar58858.2023.10406912](https://doi.org/10.1109/icar58858.2023.10406912)

**Orijinal kaynak:**
W. H. Huang, "Optimal Line-sweep-based Decompositions for Coverage Algorithms",
*IEEE International Conference on Robotics and Automation (ICRA)*, 2001.

## AC10_0000.json

AC300 problem ailesinden bir problem: 100 × 100 m alan (10.000 m²), 10 engel, 107 tarama görevi.
Koordinatlar metre cinsindendir.

**Kaynak:** Aynı CoverageTasks veri seti (yukarıdaki depo, MIT lisansı, DOI 10.5281/zenodo.7763104).
- Dosya: `AC300/AC10_0000.json`, depo commit'i `1208372ee9f170ffa3e10cc2e08982e6eff30b0f`
- Grøntved vd. (ICAR 2023) deneylerinde kullanılan problem ailesi AC300'dür.
- AC300 problemlerinin orijinal kaynağı: https://github.com/ethz-asl/polygon_coverage_planning
- CoverageTasks README'sine göre tarama görevleri 3 metrelik tarama genişliği (sweep width) ile üretilmiştir.

**Not:** Engeller Gazebo dünyasında fiziksel olarak yoktur; bu senaryoyla yapılan uçuşlar yalnızca gösterim amaçlıdır.
