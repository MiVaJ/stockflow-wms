from fastapi import FastAPI

from app.api.inventory import router as inventory_router

app = FastAPI(title="StockFlow WMS - Inventory")

app.include_router(inventory_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
