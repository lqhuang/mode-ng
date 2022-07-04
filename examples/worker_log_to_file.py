from logging import FileHandler

from mode import Service, Worker
from mode.utils.logging import DEFAULT_FORMAT, DefaultFormatter


class TestService(Service):
    async def on_started(self) -> None:
        self.log.info(
            "I'm started.",
            extra={"id": [1, 2, 3]},
        )

    @Service.task
    async def job(self) -> None:
        self.log.error(
            "Error happens.",
            extra={"user_id": 1111, "host": "localhost"},
        )


if __name__ == "__main__":
    file_handler = FileHandler("demo.log")
    file_handler.setFormatter(DefaultFormatter(DEFAULT_FORMAT))
    Worker(
        TestService(), log_handlers=(file_handler,)
    ).execute_from_commandline()
