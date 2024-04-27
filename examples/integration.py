import asyncio

import mode


class MyService(mode.Service):
    async def on_started(self) -> None:
        self.log.info("Service started (hit ctrl+C to exit).")

    @mode.Service.task
    async def _background_task(self) -> None:
        print("BACKGROUND TASK STARTING")
        t = 0.0
        while not self.should_stop and t < 5.0:
            await self.sleep(1.0)
            t += 1.0
            print(f"BACKGROUND SERVICE WAKING UP, current {t=}")


async def main():
    worker = mode.Worker(
        MyService(),
        log_level="INFO",
        log_file=None,  # stderr
        # when daemon the worker must be explicitly stopped to end.
        # daemon=True,
    )
    worker.start_system()
    await worker.join()


if __name__ == "__main__":
    asyncio.run(main())
