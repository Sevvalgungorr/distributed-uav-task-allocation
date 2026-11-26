"""Engellerden kaçınan en kısa yol (docs/cbba_plan.md, K13).

Yöntem yazarların koduyla aynıdır [T23 = trajallocpy, commit 13b7bb3]:
- Alan sınırı, sınır kutusunun merkezine göre %101 büyütülür   [T23 main.py:71]
- Her engel kendi ağırlık merkezine göre %95 küçültülür         [T23 main.py:73-77]
- En kısa yol görünürlük grafiği üzerinde aranır: extremitypathfinder.PolygonEnvironment,
  find_shortest_path(verify=False)                              [T23 CoverageProblem.py:20-27, CBBA.py:141]

Neden ölçekleme: CoverageTasks şeritlerinin bir kısmı engel kenarlarının ve alan sınırının
tam üzerinden geçer. Küçültme/büyütme olmadan şerit uçları "engelin içinde" ya da "alanın
dışında" sayılır ve yol bulunamaz.

Sürüm farkı: yazarlar extremitypathfinder'ın eski API'sini (`store`) kullanıyor; burada 4.0
sürümünün `from_shapely` yöntemi kullanılıyor. Görünürlük grafiğinde en kısa yol geometrik
olarak tektir; sonucun düz çizgi / elle hesaplanmış yollarla aynı olduğu testlerde kontrol edilir.

Bu modül Gazebo, MAVSDK veya arayüz kütüphanesi import etmez.
"""

import math

from extremitypathfinder import PolygonEnvironment
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon

BOUNDARY_SCALE = 1.01   # [T23 main.py:71]
OBSTACLE_SCALE = 0.95   # [T23 main.py:76], origin="centroid"
SNAP_CLEARANCE_M = 1e-3  # Test ayarı: engel içinde kalan noktanın kenardan dışarı taşınma payı (snap_out)


class NoPathError(ValueError):
    """İki nokta arasında engellerden kaçınan bir yol yok (ör. nokta engel içinde)."""


class Environment:
    """Alan sınırı + engeller; iki nokta arasındaki engelden kaçınan en kısa yolu verir."""

    def __init__(self, boundary, obstacles, boundary_scale=BOUNDARY_SCALE, obstacle_scale=OBSTACLE_SCALE):
        self.boundary = scale(Polygon(boundary), xfact=boundary_scale, yfact=boundary_scale)  # origin="center"
        self.obstacles = [
            scale(Polygon(o), xfact=obstacle_scale, yfact=obstacle_scale, origin="centroid") for o in obstacles
        ]
        self._env = PolygonEnvironment.from_shapely(self.boundary, self.obstacles or None, validate=True)
        self._cache = {}

    def shortest_path(self, start, goal):
        """(yol, uzunluk) döner. Yol, start ve goal dahil köşe noktaları listesidir [(x, y), ...].

        Uzunluk metredir. Yol yoksa NoPathError verir.
        """
        start, goal = (float(start[0]), float(start[1])), (float(goal[0]), float(goal[1]))
        key = (start, goal)
        if key in self._cache:
            return self._cache[key]
        if math.dist(start, goal) < 1e-9:
            result = ([start, goal], 0.0)
        else:
            s, g = self.snap_out(start), self.snap_out(goal)
            path, length = self._env.find_shortest_path(s, g, verify=False)
            if not path or length is None:
                raise NoPathError(f"{start} -> {goal} arasinda yol yok")
            path = [tuple(map(float, p)) for p in path]
            # Taşınan uçları gerçek noktalara bağla (en fazla birkaç cm'lik parça)
            if s != start:
                path, length = [start] + path, length + math.dist(start, s)
            if g != goal:
                path, length = path + [goal], length + math.dist(g, goal)
            result = (path, float(length))
        self._cache[key] = result
        return result

    def snap_out(self, point, clearance=SNAP_CLEARANCE_M):
        """Nokta küçültülmüş bir engelin içindeyse, en yakın engel kenarının `clearance` dışına taşır.

        Neden: içbükey engeller ağırlık merkezine göre %95 küçültülünce girintideki kenarlar dışarı
        kayabilir; AC10_0000'da görev 61 ve 105'in başlangıcı engel 1'in 3,4 cm içinde kalıyor.
        verify=False ile kütüphane böyle bir noktadan engelin İÇİNDEN geçen yol döndürüyor
        (26 Kasım 2026 kontrolü: 21,9 m). Yazarların kodunda bu düzeltme yok (K14 ile ilgili fark).
        """
        p = Point(point)
        for o in self.obstacles:
            if o.contains(p):
                edge = o.exterior.interpolate(o.exterior.project(p))
                dx, dy = edge.x - p.x, edge.y - p.y
                n = math.hypot(dx, dy) or 1.0
                return (edge.x + dx / n * clearance, edge.y + dy / n * clearance)
        return point

    def path_is_free(self, path):
        """Yolun hiçbir parçası (ölçeklenmiş) engellerin içinden geçmiyor mu? (test ve kontrol için)"""
        # Engel kenarına değmek serbesttir (en kısa yol köşelerden geçer); içine girmek yasak.
        line = LineString(path)
        inside_free = all(not line.intersects(o.buffer(-1e-6)) for o in self.obstacles)
        in_area = all(self.boundary.buffer(1e-9).contains(Point(p)) for p in path)
        return inside_free and in_area
