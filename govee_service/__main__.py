import asyncio
import logging

from scanner import Scanner, DEVICE_DISCOVERED

logging.basicConfig(level=logging.INFO)


async def color_callback(data):
    await data['device'].set_color((255, 255, 255))


async def run():
    scanner = Scanner()
    scanner.on(DEVICE_DISCOVERED,
               color_callback)
    await scanner.start()
    await asyncio.sleep(120)
    await scanner.stop()
    # await scanner.known_devices[0].set_color((255, 255, 255))

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
