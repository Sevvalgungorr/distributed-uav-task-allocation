"""CoverageTasks veri seti (GeoJSON) yükleyicisi.

Kaynak ve lisans bilgisi için: scenarios/README.md
Not: swarm_core simülasyondan bağımsızdır; burada MAVSDK kullanılmaz.
"""

import json

from swarm_core.models import Task


def _load_features(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {feature["id"]: feature for feature in data["features"]}


def load_boundary(path):
    """Alanın sınır poligonunu [(x, y), ...] listesi olarak döndürür."""
    features = _load_features(path)
    outer_ring = features["boundary"]["geometry"]["coordinates"][0]
    return [(x, y) for x, y in outer_ring]


def load_tasks(path):
    """Her tarama çizgisini bir Task olarak döndürür.

    task_id dosyadaki sıraya göre 1'den başlar.
    Task.x, Task.y çizginin orta noktasıdır; Task.waypoints çizginin iki ucudur.
    """
    features = _load_features(path)
    lines = features["tasks"]["geometry"]["coordinates"]

    tasks = []
    for task_id, ((x1, y1), (x2, y2)) in enumerate(lines, start=1):
        tasks.append(
            Task(
                task_id=task_id,
                x=(x1 + x2) / 2,
                y=(y1 + y2) / 2,
                waypoints=[(x1, y1), (x2, y2)],
            )
        )
    return tasks
