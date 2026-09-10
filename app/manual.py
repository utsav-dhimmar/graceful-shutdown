import asyncio
import logging
import os
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger("uvicorn")


def custom_signal_handler(signum, frame):
    logger.info(f"===> Custom handler received signal: {signum}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: registering signal handlers...")

    if os.name != "nt":
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, custom_signal_handler, sig, None)
    else:
        for sig in (signal.SIGINT, signal.SIGBREAK):
            signal.signal(sig, custom_signal_handler)

    yield

    logger.info("Shutdown complete.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/work")
async def work():
    await asyncio.sleep(10)
    return {"status": "done"}
