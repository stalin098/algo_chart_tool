import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import asyncio

class MT5Bridge:
    def __init__(self):
        self.connected = False
        self._connect()

    def _connect(self):
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            self.connected = False
        else:
            print("MetaTrader5 package version: ", mt5.version())
            self.connected = True

    def get_account_info(self):
        if not self.connected:
            self._connect()
        if not self.connected:
            return None
        
        account_info = mt5.account_info()
        if account_info is None:
            print("failed to get account info")
            return None
        return account_info._asdict()

    def get_historical_data(self, symbol: str, timeframe: int, num_candles: int = 1000):
        """
        Fetch historical data for a symbol.
        timeframe: e.g., mt5.TIMEFRAME_H1
        """
        if not self.connected:
            self._connect()
        if not self.connected:
            return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
        if rates is None:
            print(f"Failed to get rates for {symbol}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_latest_tick(self, symbol: str):
        if not self.connected:
            self._connect()
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        return tick._asdict()

    def shutdown(self):
        mt5.shutdown()
        self.connected = False

# Global instance
mt5_bridge = MT5Bridge()
