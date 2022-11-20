import asyncio

import mode


class MyService(mode.Service):
    async def on_started(self) -> None:
        self.log.info("Service started (hit ctrl+C to exit).")

    @mode.Service.task
    async def _background_task(self) -> None:
        print("BACKGROUND TASK STARTING")
        while not self.should_stop:
            await self.sleep(1.0)
            print("BACKGROUND SERVICE WAKING UP")


async def main():
    worker = mode.Worker(
        MyService(),
        log_level="INFO",
        log_file=None,  # stderr
        # when daemon the worker must be explicitly stopped to end.
        daemon=True,
    )
    worker.start_system()
    await worker.join()


if __name__ == "__main__":
    asyncio.run(main())
