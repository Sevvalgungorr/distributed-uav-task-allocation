"""h1.json'daki bir tarama görevini tek İHA ile uçar (PX4 SITL + MAVSDK 4.x).

Koordinat dönüşümü:
- Veri setindeki alanın sol alt köşesi (min x, min y) = İHA'nın kalktığı nokta.
- Veri seti x ekseni -> PX4 yerel doğu (east), y ekseni -> PX4 yerel kuzey (north).
- Veri seti koordinatları metre kabul edilir (1 birim = 1 m).
"""

import asyncio
import math
from pathlib import Path

from mavsdk.asyncio import ComponentType, Configuration, Mavsdk
from mavsdk.asyncio.plugins.action import ActionAsync
from mavsdk.asyncio.plugins.offboard import (
    OffboardAsync,
    OffboardError,
    PositionNedYaw,
    VelocityNedYaw,
)
from mavsdk.asyncio.plugins.telemetry import TelemetryAsync

from swarm_core.dataset import load_boundary, load_tasks
from swarm_sim.takeoff_land import (
    CONNECTION_URL,
    STEP_TIMEOUT_S,
    StepFailed,
    leave_offboard_on_ground,
    run_step,
    safe_stop,
    wait_for_altitude,
    wait_for_disarm,
    wait_for_health,
)

SCENARIO_PATH = Path(__file__).resolve().parent.parent / "scenarios" / "h1.json"
TASK_ID = 3                 # Uçulacak görev (h1.json'daki sırası, 1'den başlar)
V_MAX = 3.0                 # m/s,  Grøntved vd. 2023 (CLAUDE.md bölüm 13)
A_MAX = 1.0                 # m/s², Grøntved vd. 2023 (CLAUDE.md bölüm 13)
SETPOINT_RATE_HZ = 10       # PX4 offboard için en az 2 Hz gerekir

# Aşağıdakiler uygulama ayarlarıdır, senaryo parametresi değildir:
ARRIVAL_TOLERANCE_M = 0.3   # Hedefe varmış sayılma mesafesi
STOP_SPEED_M_S = 0.2        # Bu hızın altında "durdu" kabul edilir
CAPTURE_RADIUS_M = 0.5      # Bu mesafeden sonra PX4 konum tutmaya geçilir
ALT_GAIN = 1.0              # İrtifa tutma kazancı (1/s)
ALT_SPEED_M_S = 0.5         # İrtifa düzeltme hız sınırı


class LocalFrame:
    """Veri seti (x, y) <-> PX4 yerel NED (north, east) dönüşümü."""

    def __init__(self, origin_north, origin_east, min_x, min_y):
        self.origin_north = origin_north
        self.origin_east = origin_east
        self.min_x = min_x
        self.min_y = min_y

    def to_ned(self, x, y):
        return (self.origin_north + (y - self.min_y), self.origin_east + (x - self.min_x))

    def to_dataset(self, north, east):
        return (east - self.origin_east + self.min_x, north - self.origin_north + self.min_y)


async def print_position(telemetry, frame, label):
    pv = await telemetry.position_velocity_ned()
    p, v = pv.position, pv.velocity
    x, y = frame.to_dataset(p.north_m, p.east_m)
    speed = math.hypot(v.north_m_s, v.east_m_s)
    print(
        f"  [{label}] veri seti (x, y): ({x:5.2f}, {y:5.2f}) m | "
        f"irtifa: {-p.down_m:4.2f} m | yatay hiz: {speed:4.2f} m/s"
    )
    return speed


async def fly_to(offboard, telemetry, frame, target_ne, down_m, yaw_deg):
    """İHA'yı target_ne noktasına götürür ve orada tam olarak durdurur.

    Yatay hız komutu, makaledeki hız rampası modeline göre sınırlanır:
    - hızlanma en fazla A_MAX (m/s²),
    - hız en fazla V_MAX (m/s),
    - yavaşlama: v <= sqrt(2 * A_MAX * kalan_mesafe), böylece hedefe yavaşlayarak gelir.
    Hedefe CAPTURE_RADIUS_M kadar yaklaşınca konum komutuna geçilir ve İHA tam durur.
    """
    dt = 1.0 / SETPOINT_RATE_HZ
    v_cmd = 0.0
    tick = 0
    max_speed = 0.0
    while True:
        pv = await telemetry.position_velocity_ned()
        p, v = pv.position, pv.velocity
        dn, de = target_ne[0] - p.north_m, target_ne[1] - p.east_m
        dist = math.hypot(dn, de)
        speed = math.hypot(v.north_m_s, v.east_m_s)
        max_speed = max(max_speed, speed)

        if tick % SETPOINT_RATE_HZ == 0:
            await print_position(telemetry, frame, f"{tick * dt:4.1f} s")

        if dist < ARRIVAL_TOLERANCE_M and speed < STOP_SPEED_M_S:
            await offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_deg))
            await print_position(telemetry, frame, "varis")
            print(f"  Hedefte durdu. Olculen en yuksek yatay hiz: {max_speed:.2f} m/s")
            return

        if dist < CAPTURE_RADIUS_M:
            # Son yaklaşma: PX4'ün konum denetleyicisi noktayı kendisi tutar.
            await offboard.set_position_ned(PositionNedYaw(target_ne[0], target_ne[1], down_m, yaw_deg))
        else:
            v_cmd = min(v_cmd + A_MAX * dt, V_MAX, math.sqrt(2 * A_MAX * dist))
            un, ue = dn / dist, de / dist
            vz = max(-ALT_SPEED_M_S, min(ALT_SPEED_M_S, ALT_GAIN * (down_m - p.down_m)))
            await offboard.set_velocity_ned(VelocityNedYaw(un * v_cmd, ue * v_cmd, vz, yaw_deg))

        tick += 1
        await asyncio.sleep(dt)


async def main():
    boundary = load_boundary(SCENARIO_PATH)
    tasks = {task.task_id: task for task in load_tasks(SCENARIO_PATH)}
    task = tasks[TASK_ID]
    (sx, sy), (ex, ey) = task.waypoints
    min_x = min(x for x, _ in boundary)
    min_y = min(y for _, y in boundary)
    print(f"Senaryo: {SCENARIO_PATH.name}, {len(tasks)} gorev")
    print(
        f"Secilen gorev {TASK_ID}: ({sx}, {sy}) -> ({ex}, {ey}), "
        f"uzunluk {math.hypot(ex - sx, ey - sy):.2f} m"
    )

    config = Configuration.create_with_component_type(ComponentType.GROUND_STATION)
    async with Mavsdk(config) as mavsdk:
        print("\n=== 1. Baglanti ===")
        await mavsdk.add_any_connection(CONNECTION_URL)
        drone = await mavsdk.first_autopilot(timeout_s=STEP_TIMEOUT_S)
        if drone is None:
            print(f"Zaman asimi: {STEP_TIMEOUT_S:.0f} saniye icinde baglanti kurulamadi.")
            return
        print(f"IHA baglantisi basarili! Sistem ID: {await drone.get_system_id()}")

        action = ActionAsync(drone)
        telemetry = TelemetryAsync(drone)
        offboard = OffboardAsync(drone)

        try:
            await run_step("2a. Ucus modu kontrolu", leave_offboard_on_ground(action, telemetry))
            await run_step("2b. Saglik kontrolleri", wait_for_health(telemetry))

            # Kalkış noktası = veri setinin sol alt köşesi
            origin = (await telemetry.position_velocity_ned()).position
            frame = LocalFrame(origin.north_m, origin.east_m, min_x, min_y)
            yaw_deg = (await telemetry.heading()).heading_deg
            print(
                f"  Kalkis noktasi (PX4 yerel NED): kuzey {origin.north_m:.2f} m, "
                f"dogu {origin.east_m:.2f} m -> veri seti ({min_x}, {min_y})"
            )

            takeoff_alt = await run_step("3a. PX4 varsayilan kalkis irtifasi", action.get_takeoff_altitude())
            print(f"  PX4 kalkis irtifasi: {takeoff_alt:.2f} m")
            down_m = origin.down_m - takeoff_alt

            await run_step("3b. Arm", action.arm())
            print("  Arm edildi.")
            await run_step("3c. Kalkis komutu", action.takeoff())
            await run_step("3d. Kalkis irtifasina yukselme", wait_for_altitude(telemetry, takeoff_alt))
            await print_position(telemetry, frame, "havada")

            await offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, yaw_deg))
            await run_step("4. Offboard baslat", offboard.start())
            print("  Offboard modu aktif.")

            start_ne = frame.to_ned(sx, sy)
            end_ne = frame.to_ned(ex, ey)
            await run_step(
                f"5. Gorev baslangicina ucus ({sx}, {sy})",
                fly_to(offboard, telemetry, frame, start_ne, down_m, yaw_deg),
            )
            await run_step(
                f"6. Tarama cizgisi boyunca ucus -> ({ex}, {ey})",
                fly_to(offboard, telemetry, frame, end_ne, down_m, yaw_deg),
            )

            await run_step("7a. Offboard durdur", offboard.stop())
            await run_step("7b. Inis komutu", action.land())
            print("  Iniliyor...")
            await run_step("7c. Inis ve disarm", wait_for_disarm(telemetry))

            print("\nGorev ucusu basariyla tamamlandi.")

        except (StepFailed, OffboardError) as e:
            print(f"\nHATA: {e}")
            await safe_stop(action, telemetry)


if __name__ == "__main__":
    asyncio.run(main())
