import asyncio

from mavsdk.asyncio import ComponentType, Configuration, Mavsdk

CONNECTION_URL = "udpin://0.0.0.0:14540"
CONNECTION_TIMEOUT_S = 30.0


async def main():
    config = Configuration.create_with_component_type(ComponentType.GROUND_STATION)

    async with Mavsdk(config) as mavsdk:
        print("IHA'ya baglaniliyor...")
        await mavsdk.add_any_connection(CONNECTION_URL)

        drone = await mavsdk.first_autopilot(timeout_s=CONNECTION_TIMEOUT_S)

        if drone is None:
            print(f"Zaman asimi: {CONNECTION_TIMEOUT_S:.0f} saniye icinde baglanti kurulamadi.")
            print("PX4'un calistigini ve UDP 14540 portunun acik oldugunu kontrol edin.")
            return

        print("IHA baglantisi basarili!")
        print(f"Sistem ID: {await drone.get_system_id()}")


if __name__ == "__main__":
    asyncio.run(main())
