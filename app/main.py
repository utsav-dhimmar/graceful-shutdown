import asyncio
import logging
import random
from contextlib import asynccontextmanager
from types import CoroutineType
from typing import Any

from fastapi import FastAPI

logger = logging.getLogger(__name__)


class WorkerException(Exception): ...


async def worker() -> CoroutineType[Any, Any, None]:
    while True:
        print("working...")
        await asyncio.sleep(1)


async def worker_two() -> CoroutineType[Any, Any, None]:
    while True:
        guess = random.randint(1, 10)
        print(f"this is worker two {guess}")
        if guess == 5:
            raise WorkerException("got magic number ")
        await asyncio.sleep(delay=guess)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup")
    async with asyncio.TaskGroup() as tg:
        task_2 = tg.create_task(coro=worker_two(), name="worker_2")
        task_1 = tg.create_task(coro=worker(), name="worker_1")

    yield
    loop = asyncio.get_running_loop()
    # print(loop)

    logger.info("Shutdown complete.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/work")
async def work():
    await asyncio.sleep(10)
    return {"status": "done"}
