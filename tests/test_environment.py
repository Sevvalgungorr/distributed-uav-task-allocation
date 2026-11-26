import math
import random

import pytest
from shapely.geometry import LineString, Point

from swarm_core.dataset import load_boundary, load_obstacles, load_tasks
from swarm_core.environment import BOUNDARY_SCALE, OBSTACLE_SCALE, Environment

SQUARE = [(0, 0), (10, 0), (10, 10), (0, 10)]
AC10 = "scenarios/AC10_0000.json"


@pytest.fixture(scope="module")
def ac10():
    return Environment(load_boundary(AC10), load_obstacles(AC10)), load_tasks(AC10)


def test_scales_come_from_authors_code():
    assert (BOUNDARY_SCALE, OBSTACLE_SCALE) == (1.01, 0.95)  # [T23 main.py:71-77]


def test_no_obstacles_gives_straight_line():
    env = Environment(SQUARE, [])
    path, length = env.shortest_path((1, 1), (9, 8))
    assert path == [(1.0, 1.0), (9.0, 8.0)]
    assert length == pytest.approx(math.dist((1, 1), (9, 8)))


def test_zero_length_query():
    env = Environment(SQUARE, [])
    assert env.shortest_path((3, 3), (3, 3)) == ([(3.0, 3.0), (3.0, 3.0)], 0.0)


def test_goes_around_square_obstacle_with_hand_computed_length():
    # Engel (4,4)-(6,6), ağırlık merkezine göre %95 -> (4,05..5,95). (5,2)'den (5,8)'e
    # en kısa yol iki köşeden geçer: 2 * |(5,2)-(4,05;4,05)| + 1,9
    env = Environment(SQUARE, [[(4, 4), (6, 4), (6, 6), (4, 6)]])
    path, length = env.shortest_path((5, 2), (5, 8))
    expected = 2 * math.hypot(0.95, 2.05) + 1.9
    assert length == pytest.approx(expected, abs=1e-9)
    assert len(path) == 4
    assert env.path_is_free(path)


def test_point_inside_scaled_concave_obstacle_is_snapped_out(ac10):
    # AC10_0000: görev 61'in başlangıcı, engel 1 (içbükey) %95 küçültüldükten sonra bile ~3,4 cm içeride
    env, tasks = ac10
    start = tasks[60].waypoints[0]
    assert any(o.contains(Point(start)) for o in env.obstacles)
    snapped = env.snap_out(start)
    assert not any(o.contains(Point(snapped)) for o in env.obstacles)
    assert math.dist(start, snapped) < 0.05
    path, length = env.shortest_path(start, (88.2502, 41.7036))
    assert path[0] == start and math.dist(path[0], path[1]) < 0.05
    assert env.path_is_free(path[1:])  # taşınan noktadan sonrası engele girmiyor


def test_ac10_paths_never_enter_obstacles_and_never_beat_straight_line(ac10):
    env, tasks = ac10
    ends = [p for t in tasks for p in t.waypoints]
    inner = [o.buffer(-1e-6) for o in env.obstacles]
    rng = random.Random(1352323)  # test ayarı
    for _ in range(500):
        a, b = rng.sample(ends, 2)
        path, length = env.shortest_path(a, b)
        assert path[0] == a and path[-1] == b
        assert length == pytest.approx(sum(math.dist(p, q) for p, q in zip(path, path[1:])), abs=1e-6)
        assert length >= math.dist(a, b) - 1e-9
        # engel içine giren parça en fazla iki uç taşıma payı kadar (iki ucu da içeride olan nokta)
        assert max(LineString(path).intersection(o).length for o in inner) < 0.1


def test_free_straight_transit_is_kept_straight(ac10):
    # görev 2 bitişi -> görev 3 başlangıcı arasında engel yok: yol düz çizgi olmalı
    env, tasks = ac10
    a, b = tasks[1].waypoints[1], tasks[2].waypoints[0]
    path, length = env.shortest_path(a, b)
    assert len(path) == 2 and length == pytest.approx(math.dist(a, b))


def test_blocked_transit_goes_around(ac10):
    # görev 1 bitişi -> görev 2 başlangıcı arasında engel var: yol düz çizgiden uzun ve köşeli
    env, tasks = ac10
    a, b = tasks[0].waypoints[1], tasks[1].waypoints[0]
    path, length = env.shortest_path(a, b)
    assert len(path) > 2 and length > math.dist(a, b) + 0.1
    assert env.path_is_free(path)
