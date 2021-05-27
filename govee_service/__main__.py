import asyncio
import logging

from scanner import Scanner, DEVICE_DISCOVERED

logging.basicConfig(level=logging.INFO)


async def run():
    scanner = Scanner()
    scanner.on(DEVICE_DISCOVERED,
               lambda data: asyncio.new_event_loop().run_until_complete(data['device'].set_color((255, 255, 255))))
    await scanner.start()
    await asyncio.sleep(120)
    await scanner.stop()
    # await scanner.known_devices[0].set_color((255, 255, 255))

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
