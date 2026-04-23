from fastapi import FastAPI
from app.api.routes.estimate import router as estimate_router
from app.api.routes.catalog import router as catalog_router

app = FastAPI()

app.include_router(estimate_router)
app.include_router(catalog_router)

@app.get("/")
def root():
    return {"message": "API is running"}
