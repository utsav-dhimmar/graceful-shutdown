import asyncio
import logging
import os
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logging.info(msg="startup")
    # IDK WHY THIS IS FAILING
    loop = asyncio.get_running_loop()
    if os.name != "nt":
        for signame in (signal.SIGINT, signal.SIGTERM, signal.CTRL_C_EVENT):
            loop.add_signal_handler(
                signame, lambda: logging.info(msg=f"received {signame}")
            )
            logging.info(msg=f"registering {signame}")
    else:
        signal.signal(
            signal.CTRL_C_EVENT,
            logging.info(msg="received CTRL_C_EVENT"),
        )
        logging.info(msg="registering CTRL_C_EVENT")
    yield

    logging.info(msg="shutdown")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/work")
async def work():
    await asyncio.sleep(10)
    return {"status": "done"}
