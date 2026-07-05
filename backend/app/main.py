import logging
from rich.logging import RichHandler
from rich.console import Console
from fastapi import FastAPI
from app.api.routes.estimate import router as estimate_router
from app.api.routes.catalog import router as catalog_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="%H:%M:%S",
    handlers=[RichHandler(
        console=Console(stderr=True),
        rich_tracebacks=True,
        show_path=False,
    )]
)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.WARNING)

app = FastAPI()

app.include_router(estimate_router)
app.include_router(catalog_router)

@app.get("/")
def root():
    return {"message": "API is running"}
