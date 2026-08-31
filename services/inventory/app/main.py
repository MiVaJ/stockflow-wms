from fastapi import FastAPI

app = FastAPI(title="StockFlow WMS - Inventory")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
