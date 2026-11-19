"""Tek İHA ile kalkış - havada bekleme - iniş testi (PX4 SITL + MAVSDK 4.x)."""

import asyncio
from contextlib import aclosing

from mavsdk.asyncio import ComponentType, Configuration, Mavsdk
from mavsdk.asyncio.plugins.action import ActionAsync, ActionError
from mavsdk.asyncio.plugins.telemetry import TelemetryAsync

CONNECTION_URL = "udpin://0.0.0.0:14540"
STEP_TIMEOUT_S = 60.0
HOVER_DURATION_S = 10


class StepFailed(Exception):
    """Bir adım zamanında veya başarıyla tamamlanamadı."""


async def run_step(name, coro):
    """Bir adımı 60 saniyelik zaman aşımıyla çalıştırır."""
    print(f"\n=== {name} ===")
    try:
        return await asyncio.wait_for(coro, timeout=STEP_TIMEOUT_S)
    except asyncio.TimeoutError:
        raise StepFailed(f"'{name}' adımı {STEP_TIMEOUT_S:.0f} saniyede tamamlanmadı.")
    except ActionError as e:
        raise StepFailed(f"'{name}' adımında PX4 komutu reddetti: {e.result.name}")


async def wait_for_health(telemetry):
    last = None
    async with aclosing(telemetry.subscribe_health()) as stream:
        async for health in stream:
            status = (
                health.is_local_position_ok,
                health.is_global_position_ok,
                health.is_home_position_ok,
                health.is_armable,
            )
            if status != last:
                print(
                    f"  yerel konum: {status[0]}, global konum: {status[1]}, "
                    f"home: {status[2]}, arm edilebilir: {status[3]}"
                )
                last = status
            if health.is_global_position_ok and health.is_home_position_ok:
                print("  Konum tahmini ve home position hazir.")
                return


async def wait_for_altitude(telemetry, target_m):
    async with aclosing(telemetry.subscribe_position()) as stream:
        async for pos in stream:
            if pos.relative_altitude_m >= 0.95 * target_m:
                print(f"  Kalkis irtifasina ulasildi: {pos.relative_altitude_m:.2f} m")
                return


async def hover_and_report(telemetry):
    for second in range(1, HOVER_DURATION_S + 1):
        await asyncio.sleep(1)
        pos = await telemetry.position()
        print(
            f"  [{second:2d} s] enlem: {pos.latitude_deg:.7f}, "
            f"boylam: {pos.longitude_deg:.7f}, irtifa: {pos.relative_altitude_m:.2f} m"
        )


async def wait_for_disarm(telemetry):
    async with aclosing(telemetry.subscribe_armed()) as stream:
        async for armed in stream:
            if not armed:
                print("  Disarm edildi.")
                return


async def safe_stop(action, telemetry):
    """Hata durumunda İHA'yı güvenli duruma getirmeye çalışır."""
    print("\n=== Guvenli durdurma ===")
    try:
        if await telemetry.in_air():
            print("  IHA havada, iniş komutu gonderiliyor...")
            await action.land()
        elif await telemetry.armed():
            print("  IHA yerde ve arm durumunda, disarm ediliyor...")
            await action.disarm()
        else:
            print("  IHA yerde ve disarm durumunda, ek islem gerekmiyor.")
    except Exception as e:
        print(f"  Guvenli durdurma komutu basarisiz: {e}")
        print("  PX4 terminalinden (pxh>) 'commander land' komutunu kullanin.")


async def main():
    config = Configuration.create_with_component_type(ComponentType.GROUND_STATION)

    async with Mavsdk(config) as mavsdk:
        print("=== 1. Baglanti ===")
        print("IHA'ya baglaniliyor...")
        await mavsdk.add_any_connection(CONNECTION_URL)
        drone = await mavsdk.first_autopilot(timeout_s=STEP_TIMEOUT_S)
        if drone is None:
            print(f"Zaman asimi: {STEP_TIMEOUT_S:.0f} saniye icinde baglanti kurulamadi.")
            return
        print(f"IHA baglantisi basarili! Sistem ID: {await drone.get_system_id()}")

        action = ActionAsync(drone)
        telemetry = TelemetryAsync(drone)

        try:
            await run_step("2. Saglik kontrolleri", wait_for_health(telemetry))

            takeoff_alt = await run_step(
                "3a. PX4 varsayilan kalkis irtifasi", action.get_takeoff_altitude()
            )
            print(f"  PX4 kalkis irtifasi: {takeoff_alt:.2f} m")

            await run_step("3b. Arm", action.arm())
            print("  Arm edildi.")

            await run_step("3c. Kalkis komutu", action.takeoff())
            print("  Kalkis komutu kabul edildi, yukseliyor...")
            await run_step("3d. Kalkis irtifasina yukselme", wait_for_altitude(telemetry, takeoff_alt))

            await run_step(f"4. Havada bekleme ({HOVER_DURATION_S} s)", hover_and_report(telemetry))

            await run_step("5a. Inis komutu", action.land())
            print("  Inis komutu kabul edildi, iniliyor...")
            await run_step("5b. Inis ve disarm", wait_for_disarm(telemetry))

            print("\nUcus testi basariyla tamamlandi.")

        except StepFailed as e:
            print(f"\nHATA: {e}")
            await safe_stop(action, telemetry)


if __name__ == "__main__":
    asyncio.run(main())
