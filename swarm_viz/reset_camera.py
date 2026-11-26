"""Gazebo kamerasını GUI ayar dosyasındaki sabit konuma geri döndürür (docs/cbba_plan.md, A0.3).

Ne zaman: Gazebo'da yanlışlıkla bir varlığa "Move to"/"Follow" yapıldığında ya da kamera
elle kaydırıldığında. Gazebo'yu yeniden başlatmaya gerek kalmaz.

Nasıl:
1. worlds/<ad>.gui.config içindeki <camera_pose> okunur (make_world.py'nin yazdığı değer).
2. Kamera takibi bırakılır: /gui/follow servisine boş hedef gönderilir.
3. /gui/move_to/pose servisine (gz.msgs.GUICamera) bu konum gönderilir.

`gz service` komut satırı aracı kullanılır, çünkü gz-transport'un Python modülü .venv'de yok
(A0.0.2). Bu betik yalnızca görüntüyü değiştirir; İHA'ya ve simülasyona hiçbir şey göndermez.

Kullanım:
  python -m swarm_viz.reset_camera                      # worlds/ac10_0000.gui.config
  python -m swarm_viz.reset_camera --gui-config worlds/baska.gui.config
"""

import argparse
import math
import re
import subprocess
from pathlib import Path

from swarm_viz.make_world import WORLDS_DIR

DEFAULT_GUI_CONFIG = WORLDS_DIR / "ac10_0000.gui.config"
SERVICE_TIMEOUT_MS = 3000  # Test ayarı: servis yanıtı için bekleme süresi


def read_camera_pose(gui_config):
    """GUI ayarındaki <camera_pose> -> (x, y, z, roll, pitch, yaw)."""
    match = re.search(r"<camera_pose>([^<]+)</camera_pose>", Path(gui_config).read_text())
    if not match:
        raise ValueError(f"{gui_config} icinde <camera_pose> yok")
    values = [float(v) for v in match.group(1).split()]
    if len(values) != 6:
        raise ValueError(f"<camera_pose> 6 sayi olmali: {match.group(1)!r}")
    return tuple(values)


def rpy_to_quaternion(roll, pitch, yaw):
    """Euler açıları (Gazebo/SDF: önce roll, sonra pitch, sonra yaw) -> (x, y, z, w) dördey."""
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def move_to_request(pose):
    """gz.msgs.GUICamera isteğinin metin hâli."""
    x, y, z, roll, pitch, yaw = pose
    qx, qy, qz, qw = rpy_to_quaternion(roll, pitch, yaw)
    return (f"pose: {{position: {{x: {x}, y: {y}, z: {z}}}, "
            f"orientation: {{x: {qx:.6f}, y: {qy:.6f}, z: {qz:.6f}, w: {qw:.6f}}}}}")


def call_service(service, reqtype, request):
    cmd = ["gz", "service", "-s", service, "--reqtype", reqtype, "--reptype", "gz.msgs.Boolean",
           "--timeout", str(SERVICE_TIMEOUT_MS), "--req", request]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0 and "data: true" in result.stdout, (result.stdout + result.stderr).strip()


def main():
    parser = argparse.ArgumentParser(description="Gazebo kamerasini sabit konuma dondurur.")
    parser.add_argument("--gui-config", default=str(DEFAULT_GUI_CONFIG))
    args = parser.parse_args()

    pose = read_camera_pose(args.gui_config)
    print(f"Hedef kamera konumu ({args.gui_config}): {' '.join(f'{v:g}' for v in pose)}")

    ok, out = call_service("/gui/follow", "gz.msgs.StringMsg", 'data: ""')
    print("  Kamera takibi birakildi." if ok else f"  Uyari: takip birakilamadi ({out or 'yanit yok'}); devam ediliyor.")

    ok, out = call_service("/gui/move_to/pose", "gz.msgs.GUICamera", move_to_request(pose))
    if ok:
        print("  Kamera sabit konuma dondu.")
    else:
        print(f"HATA: /gui/move_to/pose basarisiz: {out or 'yanit yok'}")
        print("Gazebo penceresi acik mi? (Bu servis GUI tarafinda calisir.)")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
