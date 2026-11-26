import math
from xml.etree import ElementTree as ET

import pytest
from shapely.geometry import Point, Polygon

from swarm_core.dataset import load_obstacles, load_tasks
from swarm_viz import viz_config as cfg
from swarm_viz.make_world import (
    PX4_DEFAULT_WORLD,
    build_gui_config,
    build_world,
    camera_pose,
    inset_obstacle,
)

SCENARIO = "scenarios/AC10_0000.json"
pytestmark = pytest.mark.skipif(not PX4_DEFAULT_WORLD.exists(), reason="PX4 default.sdf yok")


@pytest.fixture(scope="module")
def world():
    tree, info = build_world(SCENARIO)
    return tree.getroot().find("world"), info


def _visuals(world, prefix):
    return [v for v in world.iter("visual") if v.get("name", "").startswith(prefix)]


def test_world_name_and_counts(world):
    w, info = world
    assert w.get("name") == "ac10_0000"
    assert len(_visuals(w, "strip_")) == 107
    assert len({v.get("name").split("_")[1] for v in _visuals(w, "obstacle_")}) == 10
    assert info["skipped"] == []


def test_px4_world_settings_copied(world):
    w, _ = world
    px4 = ET.parse(PX4_DEFAULT_WORLD).getroot().find("world")
    for tag in ("spherical_coordinates", "physics", "magnetic_field"):
        assert ET.tostring(w.find(tag)) == ET.tostring(px4.find(tag))
    assert w.find("model[@name='ground_plane']/link/collision") is not None  # zemin çarpışması korunur


def test_area_has_no_collision(world):
    w, _ = world
    assert w.find("model[@name='coverage_area']").find(".//collision") is None


def test_obstacle_height_below_flight_altitude(world):
    w, _ = world
    for v in _visuals(w, "obstacle_"):
        h = float(v.find("geometry/polyline/height").text)
        assert h == cfg.OBSTACLE_HEIGHT_M and h < 2.5  # 2,5 m: PX4 varsayılan kalkış irtifası


def test_obstacles_are_inset_by_half_meter():
    for points in load_obstacles(SCENARIO):
        original = Polygon(points)
        for part in inset_obstacle(points):
            shrunk = Polygon(part)
            assert original.contains(shrunk)
            # küçültülmüş poligonun her köşesi orijinal kenara en az 0,5 m uzak
            for x, y in part:
                assert original.exterior.distance(Point(x, y)) == pytest.approx(cfg.OBSTACLE_INSET_M, abs=1e-6) \
                    or original.exterior.distance(Point(x, y)) > cfg.OBSTACLE_INSET_M


def test_no_strip_enters_inset_obstacle():
    shrunk = [Polygon(p) for o in load_obstacles(SCENARIO) for p in inset_obstacle(o)]
    for task in load_tasks(SCENARIO):
        (x0, y0), (x1, y1) = task.waypoints
        n = max(2, int(math.dist((x0, y0), (x1, y1)) / 0.1))
        for k in range(n + 1):
            pt = Point(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n)
            assert not any(s.contains(pt) for s in shrunk), f"gorev {task.task_id} engele giriyor"


def test_strip_visual_matches_task_geometry(world):
    w, _ = world
    task = load_tasks(SCENARIO)[0]
    (x0, y0), (x1, y1) = task.waypoints
    v = next(v for v in _visuals(w, "strip_") if v.get("name") == f"strip_{task.task_id}")
    px, py, _, _, _, yaw = map(float, v.find("pose").text.split())
    length = float(v.find("geometry/box/size").text.split()[0])
    assert (px, py) == pytest.approx(((x0 + x1) / 2, (y0 + y1) / 2), abs=1e-3)
    assert length == pytest.approx(math.dist((x0, y0), (x1, y1)), abs=1e-3)
    assert yaw == pytest.approx(math.atan2(y1 - y0, x1 - x0), abs=1e-3)


def test_camera_looks_at_area_center():
    x, y, z, _, pitch, yaw = map(float, camera_pose([(0, 0), (100, 0), (100, 100), (0, 100)]).split())
    assert z > 0 and pitch > 0
    assert math.atan2(50 - y, 50 - x) == pytest.approx(yaw, abs=1e-3)


def test_camera_is_closest_pose_that_fits_whole_area():
    from swarm_viz.make_world import _screen_extent
    square = [(0, 0), (100, 0), (100, 100), (0, 100)]
    x, y, z, *_ = map(float, camera_pose(square).split())
    corners = [(px, py, 0.0) for px, py in square]
    for aspect in cfg.CAMERA_ASPECTS:  # bütün köşeler ekranda
        assert _screen_extent((x, y, z), (50, 50, 0), corners, cfg.CAMERA_HFOV_DEG, aspect) <= cfg.CAMERA_FIT_MARGIN
    # 1 m daha yaklaşınca en az bir ekran oranında sığmıyor: gerçekten en yakın nokta
    el, az = math.radians(cfg.CAMERA_ELEVATION_DEG), math.radians(cfg.CAMERA_AZIMUTH_DEG)
    d = math.hypot(x - 50, y - 50) - 1.0
    closer = (50 - d * math.cos(az), 50 - d * math.sin(az), d * math.tan(el))
    assert any(_screen_extent(closer, (50, 50, 0), corners, cfg.CAMERA_HFOV_DEG, a) > cfg.CAMERA_FIT_MARGIN
               for a in cfg.CAMERA_ASPECTS)


def test_gui_config_only_camera_changes():
    gui = build_gui_config(SCENARIO)
    assert gui.count("<camera_pose>") == 1 and "MarkerManager" in gui  # adım 3 için işaretçi eklentisi açık
    assert f"<horizontal_fov>{cfg.CAMERA_HFOV_DEG:g}</horizontal_fov>" in gui
