from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from mt5_bridge import mt5_bridge
from analysis_engine import analysis_engine
import pandas as pd

app = FastAPI(title="Algo Chart Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Connection is handled in MT5Bridge init, but we can re-check here
    if not mt5_bridge.connected:
        mt5_bridge._connect()

@app.on_event("shutdown")
async def shutdown_event():
    mt5_bridge.shutdown()

@app.get("/")
def read_root():
    return {"status": "online", "mt5_connected": mt5_bridge.connected}

@app.get("/account")
def get_account():
    info = mt5_bridge.get_account_info()
    if not info:
        raise HTTPException(status_code=503, detail="MT5 not connected or failed to fetch account info")
    return info

@app.get("/history/{symbol}")
def get_history(symbol: str, timeframe: int = 16385, num_candles: int = 1000):
    # 16385 is mt5.TIMEFRAME_H1 (1 hour) default. 
    # In a real app, map string "H1" to int constants.
    df = mt5_bridge.get_historical_data(symbol, timeframe, num_candles)
    if df is None:
        raise HTTPException(status_code=404, detail="Symbol not found or data unavailable")
    
    # Convert to dict for JSON response
    return df.to_dict(orient="records")

@app.post("/backtest")
def run_backtest(symbol: str, strategy_code: str):
    # Fetch data
    df = mt5_bridge.get_historical_data(symbol, 16385, 1000) # Default H1
    if df is None:
        raise HTTPException(status_code=404, detail="Data not found for backtest")
    
    # Run backtest
    result = analysis_engine.run_backtest(df, strategy_code)
    return result

@app.websocket("/ws/price/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        while True:
            tick = mt5_bridge.get_latest_tick(symbol)
            if tick:
                await websocket.send_json(tick)
            else:
                # If symbol invalid, maybe send error once and close? 
                # Or just wait.
                pass
            
            await asyncio.sleep(0.1) 
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
