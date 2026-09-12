import asyncio
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi import status as HttpStatusCode
from fastapi.responses import JSONResponse
from httpx import Response
from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)


class WorkerException(Exception): ...


class Worker(BaseModel):
    http_url: HttpUrl


class WorkerResponse(BaseModel):
    message: str
    url: HttpUrl
    response: str


class WorkerFailedResponse(BaseModel):
    message: str = "something went wrong"
    error: str | None


async def get_httpx_async_client(timeout: int = 10) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup")

    client = await get_httpx_async_client()
    app.state.client = client

    yield

    await client.aclose()

    logger.info("Shutdown complete.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/work")
async def work():
    await asyncio.sleep(10)
    return {"status": "done"}


@app.post(
    "/worker",
    response_model=WorkerResponse,
    responses={
        HttpStatusCode.HTTP_200_OK: {"model": WorkerResponse},
        HttpStatusCode.HTTP_400_BAD_REQUEST: {"model": WorkerFailedResponse},
    },
)
async def worker(data: Worker):
    async with app.state.client as client:
        try:
            response: Response = await client.get(
                data.http_url.encoded_string()
            )

            response.raise_for_status()
        except httpx.HTTPError as e:
            # raise WorkerException(f"Failed to fetch URL: {e}")
            return JSONResponse(
                status_code=HttpStatusCode.HTTP_400_BAD_REQUEST,
                content={"message": "something went wrong", "error": f"{e}"},
            )
    return {
        "message": "Worker is running",
        "url": data.http_url,
        "response": str(response.content),
    }
