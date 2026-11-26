"""CoverageTasks senaryosundan Gazebo Harmonic dünyası üretir (docs/cbba_plan.md, A0.2–A0.3).

Üretilenler (commit edilmez, .gitignore):
  worlds/<ad>.sdf         Dünya: zemin, sınır çizgisi, ince gri tarama şeritleri, 1 m beton engeller
  worlds/<ad>.gui.config  Gazebo GUI ayarı: alanın tamamını gösteren sabit çapraz-üst kamera

Kurallar:
- Fizik, yerçekimi, manyetik alan, atmosfer, sahne, güneş ışığı, spherical_coordinates ve
  zemin modeli PX4'ün default.sdf dosyasından OKUNARAK kopyalanır; PX4 dosyasına yazılmaz.
  Böylece PX4'ün sensör eklentileri (GPS, manyetometre, barometre) aynı değerlerle çalışır.
- Şeritler, sınır ve engellerde <collision> yoktur: yalnızca görseldir, uçuşu etkilemez.
- Engeller, veri setindeki poligonun 0,5 m içeriden hâli ile yol planlayıcının %95 hâlinin
  kesişimi olarak çizilir (inset_obstacle); veri setinin geometrisi değişmez.
- Koordinatlar: veri seti (x doğu, y kuzey, metre) = Gazebo dünyası (x, y). Dünya (0,0) = veri seti (0,0).

Kullanım:
  python -m swarm_viz.make_world scenarios/AC10_0000.json
"""

import argparse
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from shapely.affinity import scale
from shapely.geometry import MultiPolygon, Polygon

from swarm_core.dataset import load_boundary, load_obstacles, load_tasks
from swarm_core.environment import OBSTACLE_SCALE
from swarm_viz import viz_config as cfg

PX4_DEFAULT_WORLD = Path.home() / "PX4-Autopilot/Tools/simulation/gz/worlds/default.sdf"
GZ_DEFAULT_GUI = Path("/usr/share/gz/gz-sim8/gui/gui.config")
WORLDS_DIR = Path(__file__).resolve().parent.parent / "worlds"

# PX4 default.sdf'ten aynen kopyalanan dünya öğeleri
COPIED_WORLD_TAGS = ("physics", "gravity", "magnetic_field", "atmosphere", "scene", "light", "spherical_coordinates")


def world_name_for(scenario_path):
    """scenarios/AC10_0000.json -> ac10_0000 (Gazebo konu adlarında kullanılır)."""
    return re.sub(r"[^a-z0-9_]", "_", Path(scenario_path).stem.lower())


def inset_obstacle(points, inset_m=cfg.OBSTACLE_INSET_M):
    """Gazebo'da çizilecek engel şekli; parça listesi döner (boş olabilir).

    Çizilen şekil iki şeklin KESİŞİMİDİR (26 Kasım 2026 kararı):
    - her kenarı inset_m içeri çekilmiş engel  -> engel kenarındaki şeritler bloğun altında kalmaz
    - yol planlayıcının engeli (ağırlık merkezine göre OBSTACLE_SCALE, swarm_core/environment.py)
      -> planlanan geçiş yolu hiçbir zaman çizilen bloğun üstünden geçmez
    Yalnızca birini kullanmak sivri köşelerde görüntü ile planı uyumsuz yapıyordu (engel 5, logla ölçüldü).
    Çok ince bir engel küçültülünce ikiye bölünebilir (MultiPolygon) ya da yok olabilir.
    """
    original = Polygon(points)
    planner = scale(original, xfact=OBSTACLE_SCALE, yfact=OBSTACLE_SCALE, origin="centroid")
    shrunk = original.buffer(-inset_m, join_style="mitre").intersection(planner)
    if shrunk.is_empty:
        return []
    parts = shrunk.geoms if isinstance(shrunk, MultiPolygon) else [shrunk]
    return [list(p.exterior.coords)[:-1] for p in parts if not p.is_empty]


def _f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _color(rgb):
    return " ".join(_f(c) for c in rgb) + " 1"


def _material(parent, rgb):
    mat = ET.SubElement(parent, "material")
    for tag in ("ambient", "diffuse"):
        ET.SubElement(mat, tag).text = _color(rgb)
    ET.SubElement(mat, "specular").text = "0.1 0.1 0.1 1"


def _box_visual(link, name, x0, y0, x1, y1, width, height, rgb):
    """İki nokta arasında, zemine yatırılmış ince bir kutu (çizgi) görseli. Collision yok."""
    length = math.hypot(x1 - x0, y1 - y0)
    yaw = math.atan2(y1 - y0, x1 - x0) if length > 0 else 0.0
    length = max(length, cfg.MIN_STRIP_LENGTH_M)
    vis = ET.SubElement(link, "visual", name=name)
    ET.SubElement(vis, "pose").text = f"{_f((x0 + x1) / 2)} {_f((y0 + y1) / 2)} {_f(height / 2)} 0 0 {_f(yaw)}"
    box = ET.SubElement(ET.SubElement(vis, "geometry"), "box")
    ET.SubElement(box, "size").text = f"{_f(length)} {_f(width)} {_f(height)}"
    ET.SubElement(vis, "cast_shadows").text = "false"
    _material(vis, cfg.STRIP_COLOR if rgb is None else rgb)
    return vis


def build_world(scenario_path, px4_world=PX4_DEFAULT_WORLD):
    """Dünya SDF'ini ElementTree olarak oluşturur (dosyaya yazmadan; testler bunu kullanır)."""
    name = world_name_for(scenario_path)
    boundary = load_boundary(scenario_path)
    obstacles = load_obstacles(scenario_path)
    tasks = load_tasks(scenario_path)

    px4_root = ET.parse(px4_world).getroot()
    px4 = px4_root.find("world")

    sdf = ET.Element("sdf", version="1.9")
    world = ET.SubElement(sdf, "world", name=name)
    for tag in COPIED_WORLD_TAGS:
        for elem in px4.findall(tag):
            world.append(elem)

    # Zemin: PX4'ün zemin modeli (çarpışma dahil) aynen; yalnızca görsel renk ve boyut değişir
    ground = px4.find("model[@name='ground_plane']")
    gvis = ground.find("link/visual")
    gvis.find("geometry/plane/size").text = f"{_f(cfg.GROUND_SIZE_M)} {_f(cfg.GROUND_SIZE_M)}"
    gvis.remove(gvis.find("material"))
    _material(gvis, cfg.GROUND_COLOR)
    world.append(ground)

    # Alan: tek statik model, tek link; her şerit/sınır/engel bir görsel (varlık sayısı az kalsın)
    area = ET.SubElement(world, "model", name="coverage_area")
    ET.SubElement(area, "static").text = "true"
    link = ET.SubElement(area, "link", name="link")

    ring = boundary if boundary[0] != boundary[-1] else boundary[:-1]
    for i, (p, q) in enumerate(zip(ring, ring[1:] + ring[:1])):
        _box_visual(link, f"boundary_{i}", *p, *q, cfg.BOUNDARY_WIDTH_M, cfg.BOUNDARY_HEIGHT_M, cfg.BOUNDARY_COLOR)

    for task in tasks:
        (x0, y0), (x1, y1) = task.waypoints
        _box_visual(link, f"strip_{task.task_id}", x0, y0, x1, y1, cfg.STRIP_WIDTH_M, cfg.STRIP_HEIGHT_M, None)

    skipped = []
    for i, obstacle in enumerate(obstacles, start=1):
        parts = inset_obstacle(obstacle)
        if not parts:
            skipped.append(i)
            continue
        for k, part in enumerate(parts):
            vis = ET.SubElement(link, "visual", name=f"obstacle_{i}" + (f"_{k}" if len(parts) > 1 else ""))
            poly = ET.SubElement(ET.SubElement(vis, "geometry"), "polyline")
            for x, y in part:
                ET.SubElement(poly, "point").text = f"{_f(x)} {_f(y)}"
            ET.SubElement(poly, "height").text = _f(cfg.OBSTACLE_HEIGHT_M)
            _material(vis, cfg.OBSTACLE_COLOR)

    return ET.ElementTree(sdf), {"name": name, "tasks": len(tasks), "obstacles": len(obstacles), "skipped": skipped}


def _screen_extent(cam, target, points, hfov_deg, aspect):
    """Noktaların ekrandaki en büyük |x| veya |y| değeri (1 = tam ekran kenarı).

    Basit iğne deliği kamera modeli: kamera `target`a bakar, ufuk yataydır.
    """
    f = [t - c for t, c in zip(target, cam)]
    n = math.sqrt(sum(v * v for v in f))
    f = [v / n for v in f]
    r = [f[1], -f[0], 0.0]                      # f × z (sağ vektör)
    rn = math.hypot(r[0], r[1])
    r = [r[0] / rn, r[1] / rn, 0.0]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]  # r × f
    th = math.tan(math.radians(hfov_deg) / 2)
    tv = th / aspect
    worst = 0.0
    for p in points:
        v = [p[i] - cam[i] for i in range(3)]
        depth = sum(v[i] * f[i] for i in range(3))
        if depth <= 0:
            return math.inf
        sx = sum(v[i] * r[i] for i in range(3)) / depth / th
        sy = sum(v[i] * u[i] for i in range(3)) / depth / tv
        worst = max(worst, abs(sx), abs(sy))
    return worst


def camera_pose(boundary):
    """Alanın tamamını gösteren EN YAKIN sabit kamera: 'x y z roll pitch yaw'.

    Kamera alan merkezine bakar; yönü ve eğimi viz_config'ten gelir. Uzaklık, sınırın bütün
    köşeleri her iki ekran oranında da CAMERA_FIT_MARGIN içine sığana kadar 0,5 m adımla artırılır.
    """
    xs, ys = [p[0] for p in boundary], [p[1] for p in boundary]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    az, el = math.radians(cfg.CAMERA_AZIMUTH_DEG), math.radians(cfg.CAMERA_ELEVATION_DEG)
    corners = [(x, y, 0.0) for x, y in boundary]
    d = 1.0
    while True:
        cam = (cx - d * math.cos(az), cy - d * math.sin(az), d * math.tan(el))
        if all(_screen_extent(cam, (cx, cy, 0.0), corners, cfg.CAMERA_HFOV_DEG, a) <= cfg.CAMERA_FIT_MARGIN
               for a in cfg.CAMERA_ASPECTS):
            break
        d += 0.5
    yaw = az                     # merkeze doğru bak
    pitch = el                   # aşağı eğim (Gazebo'da pozitif = aşağı)
    return f"{_f(cam[0])} {_f(cam[1])} {_f(cam[2])} 0 {_f(pitch)} {_f(yaw)}"


def build_gui_config(scenario_path, base_gui=GZ_DEFAULT_GUI):
    """Gazebo'nun varsayılan GUI ayarını okur; yalnızca kamera konumunu ve görüş açısını değiştirir."""
    text = Path(base_gui).read_text()
    pose = camera_pose(load_boundary(scenario_path))
    camera = f"<camera_pose>{pose}</camera_pose>\n  <horizontal_fov>{_f(cfg.CAMERA_HFOV_DEG)}</horizontal_fov>"
    new, n = re.subn(r"<camera_pose>.*?</camera_pose>", camera, text, count=1)
    if n != 1:
        raise ValueError(f"{base_gui} icinde <camera_pose> bulunamadi")
    return new


def main():
    parser = argparse.ArgumentParser(description="CoverageTasks senaryosundan Gazebo dunyasi uretir.")
    parser.add_argument("scenario", help="ornek: scenarios/AC10_0000.json")
    parser.add_argument("--out-dir", default=str(WORLDS_DIR))
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tree, info = build_world(args.scenario)
    ET.indent(tree, space="  ")
    world_path = out / f"{info['name']}.sdf"
    tree.write(world_path, encoding="utf-8", xml_declaration=True)
    gui_path = out / f"{info['name']}.gui.config"
    gui_path.write_text(build_gui_config(args.scenario))

    print(f"Dunya: {world_path}  (dunya adi: {info['name']})")
    print(f"  {info['tasks']} serit, {info['obstacles']} engel ({cfg.OBSTACLE_INSET_M} m iceriden, "
          f"planlayicinin %{OBSTACLE_SCALE * 100:g} engeliyle kesisim, {cfg.OBSTACLE_HEIGHT_M} m yukseklik, collision yok)")
    if info["skipped"]:
        print(f"  UYARI: kucultulunce yok olan engeller cizilmedi: {info['skipped']}")
    print(f"GUI ayari: {gui_path}  (kamera: {camera_pose(load_boundary(args.scenario))})")


if __name__ == "__main__":
    main()
