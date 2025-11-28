import pandas as pd
import pandas_ta as ta

class AnalysisEngine:
    def __init__(self):
        pass

    def calculate_indicators(self, df: pd.DataFrame, indicators: list):
        """
        Calculate technical indicators on the dataframe.
        indicators: list of dicts, e.g., [{"name": "rsi", "length": 14}, {"name": "sma", "length": 20}]
        """
        if df is None or df.empty:
            return df

        # Ensure we have a working copy
        df = df.copy()

        for ind in indicators:
            name = ind.get("name").lower()
            try:
                if name == "rsi":
                    length = ind.get("length", 14)
                    df.ta.rsi(length=length, append=True)
                elif name == "sma":
                    length = ind.get("length", 20)
                    df.ta.sma(length=length, append=True)
                elif name == "ema":
                    length = ind.get("length", 20)
                    df.ta.ema(length=length, append=True)
                elif name == "macd":
                    fast = ind.get("fast", 12)
                    slow = ind.get("slow", 26)
                    signal = ind.get("signal", 9)
                    df.ta.macd(fast=fast, slow=slow, signal=signal, append=True)
                elif name == "bbands":
                    length = ind.get("length", 20)
                    std = ind.get("std", 2.0)
                    df.ta.bbands(length=length, std=std, append=True)
                # Add more indicators as needed
            except Exception as e:
                print(f"Error calculating {name}: {e}")

        return df

    def run_backtest(self, df: pd.DataFrame, strategy_code: str):
        """
        Run a backtest using a custom strategy script.
        strategy_code: Python code string that defines a 'signal' function.
        """
        # Security warning: executing arbitrary code is dangerous. 
        # In a real app, this needs strict sandboxing.
        # For this tool, we assume the user is the author.
        
        local_scope = {"df": df, "pd": pd, "ta": ta}
        
        try:
            exec(strategy_code, {}, local_scope)
            
            if "generate_signals" not in local_scope:
                return {"error": "Strategy must define a 'generate_signals(df)' function."}
            
            # Run the strategy
            signals = local_scope["generate_signals"](df)
            
            # Calculate PnL (Simplified)
            # Assuming signals is a Series of 1 (Buy), -1 (Sell), 0 (Hold)
            if signals is None:
                 return {"error": "Strategy returned None"}

            df['signal'] = signals
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['signal'].shift(1) * df['returns']
            
            cumulative_return = (1 + df['strategy_returns']).cumprod()
            total_return = cumulative_return.iloc[-1] - 1
            
            # Extract Buy/Sell points for plotting
            buy_signals = df[df['signal'] == 1].copy()
            sell_signals = df[df['signal'] == -1].copy()
            
            return {
                "total_return": total_return,
                "trades": len(df[df['signal'] != 0]),
                "equity_curve": cumulative_return.tolist(),
                "buy_signals": {
                    "time": buy_signals['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "price": buy_signals['close'].tolist()
                },
                "sell_signals": {
                    "time": sell_signals['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                    "price": sell_signals['close'].tolist()
                }
            }

        except Exception as e:
            return {"error": str(e)}

analysis_engine = AnalysisEngine()
