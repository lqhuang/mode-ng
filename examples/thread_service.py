import asyncio

from mode import Service
from mode.threads import ServiceThread
from mode import Worker


class T(ServiceThread):
    @Service.task
    async def poll_thread(self):
        while not self.should_stop:
            await asyncio.sleep(0)
            print("hello")


class S(Service):
    def on_init_dependencies(self):
        return [T()]


async def run():
    # t = T()
    # await t.start()
    # await t.stop()
    # await t._shutdown_thread()

    s = S()
    await s.start()
    await s.stop()


if __name__ == "__main__":
    for _ in range(3):
        asyncio.run(run())

    # worker = Worker(S(), daemon=False)
    # worker.execute_from_commandline()
