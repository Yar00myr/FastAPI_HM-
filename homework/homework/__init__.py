import time
import logging
from fastapi import FastAPI, Request, Response
import uvicorn

app = FastAPI()

logger = logging.getLogger("middleware_logger")

logging.basicConfig(level=logging.INFO)
requests_logger = logging.getLogger("requests")
requests_handler = logging.FileHandler("requests.log")
requests_formatter = logging.Formatter("%(message)s")
requests_handler.setFormatter(requests_formatter)
requests_logger.addHandler(requests_handler)


@app.middleware("http")
async def log_request_details(request: Request, call_next):
    method = request.method
    url = str(request.url)
    received_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    requests_logger.info(f"[{received_time}] {method} {url}")
    response = await call_next(request)
    return response


@app.middleware("http")
async def check_custom_header(request: Request, call_next):
    if request.url.path not in ["/docs", "/openapi.json", "/favicon.ico"]:
        if "X-Custom-Header" not in request.headers:
            logger.error(f"Missing X-Custom-Header in request to {request.url.path}")

            return Response(content="X-Custom-Header is required.", status_code=400)
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f"Processed {request.method} request to {request.url} in {process_time:.4f} seconds"
    )
    return response


@app.get("/")
async def root(resp: Response):
    resp.headers["X-Custom-Header"] = "Hello World"
    return "Hello world"


@app.get("/items")
async def items():
    return {"items": ["foo", "bar"]}


def main():
    uvicorn.run("homework:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
