"""İki İHA ile eşzamanlı kalkış - havada bekleme - iniş testi (PX4 SITL + MAVSDK 4.x).

Ön koşul: İki PX4 örneği çalışıyor olmalı (CLAUDE.md, Aşama 2):
    -i 0 -> x500_0, Gazebo (0, 0), MAVSDK portu 14540, Sistem ID 1
    -i 1 -> x500_1, Gazebo (0, 3), MAVSDK portu 14541, Sistem ID 2
PX4 portları: px4-rc.mavlink (14540 + örnek_no), Sistem ID: rcS (örnek_no + 1).

TEST AYARI (CLAUDE.md bölüm 14, kural 2): İHA'lar arası 3 m başlangıç mesafesi.
Gazebo konumları PX4 başlatma komutunda PX4_GZ_MODEL_POSE ile verilir ("0,0" ve "0,3").
Grøntved vd. (2023) bütün İHA'ları ortak bir başlangıç noktasından (depot) başlatır;
Gazebo'da iki model aynı noktada duramadığı için 3 m seçilmiştir. Akademik kaynağı yoktur,
deney parametresi değildir.

Her İHA için ayrı bir Mavsdk nesnesi ve ayrı bağlantı kullanılır.
Adımlar aşama aşama ilerler: bir aşama iki İHA için de bitmeden sonrakine geçilmez.
Bir İHA'da bir adım başarısız olursa diğerinin o aşamadaki işi iptal edilir ve
iki İHA için de güvenli durdurma çalışır.
"""

import asyncio
from contextlib import AsyncExitStack
from dataclasses import dataclass

from mavsdk.asyncio import ComponentType, Configuration, Mavsdk
from mavsdk.asyncio.plugins.action import ActionAsync
from mavsdk.asyncio.plugins.telemetry import TelemetryAsync

from swarm_sim.takeoff_land import (
    HOVER_DURATION_S,
    STEP_TIMEOUT_S,
    StepFailed,
    hover_and_report,
    leave_offboard_on_ground,
    run_step,
    safe_stop,
    wait_for_altitude,
    wait_for_disarm,
    wait_for_health,
)

# (isim, PX4 örnek numarası). Port ve Sistem ID PX4'ün kendi kuralından hesaplanır.
UAV_INSTANCES = [("IHA1", 0), ("IHA2", 1)]


@dataclass
class UavLink:
    name: str
    instance: int
    drone: object = None
    action: ActionAsync = None
    telemetry: TelemetryAsync = None
    takeoff_alt: float = None

    @property
    def prefix(self):
        return f"[{self.name}] "

    @property
    def url(self):
        return f"udpin://0.0.0.0:{14540 + self.instance}"

    @property
    def expected_system_id(self):
        return self.instance + 1


async def connect(uav, mavsdk):
    print(f"{uav.prefix}Baglaniliyor: {uav.url} (beklenen Sistem ID: {uav.expected_system_id})")
    await mavsdk.add_any_connection(uav.url)
    drone = await mavsdk.first_autopilot(timeout_s=STEP_TIMEOUT_S)
    if drone is None:
        raise StepFailed(f"{uav.prefix}{STEP_TIMEOUT_S:.0f} saniye icinde baglanti kurulamadi.")
    system_id = await drone.get_system_id()
    if system_id != uav.expected_system_id:
        raise StepFailed(
            f"{uav.prefix}Yanlis IHA: Sistem ID {system_id}, beklenen {uav.expected_system_id}."
        )
    uav.drone = drone
    uav.action = ActionAsync(drone)
    uav.telemetry = TelemetryAsync(drone)
    print(f"{uav.prefix}Baglanti basarili, Sistem ID: {system_id}")


async def run_phase(title, uavs, make_step):
    """Bir aşamayı iki İHA için aynı anda çalıştırır; biri hata verirse diğeri iptal edilir."""
    print(f"\n########## {title} ##########")
    try:
        async with asyncio.TaskGroup() as group:
            for uav in uavs:
                group.create_task(make_step(uav))
    except* Exception as errors:
        raise StepFailed(" | ".join(str(e) for e in errors.exceptions)) from None


async def prepare(uav):
    await run_step("Ucus modu kontrolu", leave_offboard_on_ground(uav.action, uav.telemetry, uav.prefix), uav.prefix)
    await run_step("Saglik kontrolleri", wait_for_health(uav.telemetry, uav.prefix), uav.prefix)
    uav.takeoff_alt = await run_step("PX4 varsayilan kalkis irtifasi", uav.action.get_takeoff_altitude(), uav.prefix)
    print(f"  {uav.prefix}PX4 kalkis irtifasi: {uav.takeoff_alt:.2f} m")


async def arm(uav):
    await run_step("Arm", uav.action.arm(), uav.prefix)
    print(f"  {uav.prefix}Arm edildi.")


async def takeoff(uav):
    await run_step("Kalkis komutu", uav.action.takeoff(), uav.prefix)
    await run_step("Kalkis irtifasina yukselme", wait_for_altitude(uav.telemetry, uav.takeoff_alt, uav.prefix), uav.prefix)


async def hover(uav):
    await run_step(f"Havada bekleme ({HOVER_DURATION_S} s)", hover_and_report(uav.telemetry, uav.prefix), uav.prefix)


async def land(uav):
    await run_step("Inis komutu", uav.action.land(), uav.prefix)
    await run_step("Inis ve disarm", wait_for_disarm(uav.telemetry, uav.prefix), uav.prefix)


async def main():
    uavs = [UavLink(name, instance) for name, instance in UAV_INSTANCES]

    async with AsyncExitStack() as stack:
        mavsdks = []
        for _ in uavs:
            config = Configuration.create_with_component_type(ComponentType.GROUND_STATION)
            mavsdks.append(await stack.enter_async_context(Mavsdk(config)))

        try:
            print("########## 1. Baglanti ##########")
            await asyncio.gather(*(connect(u, m) for u, m in zip(uavs, mavsdks)))
        except StepFailed as e:
            print(f"\nHATA: {e}\nBaglanti asamasinda hata; hicbir IHA arm edilmedi.")
            return

        try:
            await run_phase("2. Hazirlik (ucus modu, saglik, kalkis irtifasi)", uavs, prepare)
            await run_phase("3. Arm (iki IHA birlikte)", uavs, arm)
            await run_phase("4. Kalkis (iki IHA birlikte)", uavs, takeoff)
            await run_phase(f"5. Havada bekleme ({HOVER_DURATION_S} s)", uavs, hover)
            await run_phase("6. Inis ve disarm", uavs, land)
            print("\nIki IHA ile ucus testi basariyla tamamlandi.")

        except StepFailed as e:
            print(f"\nHATA: {e}")
            await asyncio.gather(*(safe_stop(u.action, u.telemetry, u.prefix) for u in uavs))


if __name__ == "__main__":
    asyncio.run(main())
