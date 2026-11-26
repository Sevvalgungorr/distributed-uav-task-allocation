import math

import pytest

from swarm_viz.reset_camera import move_to_request, read_camera_pose, rpy_to_quaternion


def test_read_camera_pose(tmp_path):
    cfg = tmp_path / "x.gui.config"
    cfg.write_text("<plugin>\n  <camera_pose>50 -56.5 106.5 0 0.7854 1.5708</camera_pose>\n</plugin>")
    assert read_camera_pose(cfg) == (50.0, -56.5, 106.5, 0.0, 0.7854, 1.5708)


def test_read_camera_pose_missing(tmp_path):
    cfg = tmp_path / "x.gui.config"
    cfg.write_text("<plugin/>")
    with pytest.raises(ValueError):
        read_camera_pose(cfg)


def test_quaternion_known_values():
    assert rpy_to_quaternion(0, 0, 0) == pytest.approx((0, 0, 0, 1))
    s = math.sqrt(0.5)
    assert rpy_to_quaternion(0, 0, math.pi / 2) == pytest.approx((0, 0, s, s))   # 90° yaw
    assert rpy_to_quaternion(0, math.pi / 2, 0) == pytest.approx((0, s, 0, s))   # 90° pitch


def test_quaternion_rotates_camera_axis_toward_area():
    # Kamera ekseni (x ekseni) 45° aşağı ve kuzeye bakmalı: (0, cos45, -sin45)
    qx, qy, qz, qw = rpy_to_quaternion(0, 0.7854, 1.5708)
    fx = 1 - 2 * (qy * qy + qz * qz)
    fy = 2 * (qx * qy + qz * qw)
    fz = 2 * (qx * qz - qy * qw)
    assert (fx, fy, fz) == pytest.approx((0, math.cos(0.7854), -math.sin(0.7854)), abs=1e-4)


def test_request_text():
    req = move_to_request((50, -56.5, 106.5, 0, 0, 0))
    assert req == ("pose: {position: {x: 50, y: -56.5, z: 106.5}, "
                   "orientation: {x: 0.000000, y: 0.000000, z: 0.000000, w: 1.000000}}")
