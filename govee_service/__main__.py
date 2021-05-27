import asyncio

from scanner import Scanner


async def run():
    scanner = Scanner()
    await scanner.start()
    await asyncio.sleep(120)
    await scanner.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
