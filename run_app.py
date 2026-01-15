from fastapi import FastAPI
from src.library_catalog.api.v1.routers.books import router as books_router
from src.library_catalog.api.v1.routers.health_simple import router as health_router

app = FastAPI(title="Library API")

app.include_router(books_router, prefix="/api/v1")
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": "API работает"}
