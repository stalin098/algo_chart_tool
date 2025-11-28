# Algo Trading Chart Analysis Tool

A professional-grade algorithmic trading analysis tool built with Python and Streamlit. This application connects directly to **MetaTrader 5 (MT5)** to provide real-time market data, interactive charting, and a powerful backtesting engine for custom strategies.

## Features

- **Real-Time Data Streaming**: Live price updates from your local MT5 terminal.
- **Interactive Charting**: Advanced candlestick charts powered by Plotly with zoom, pan, and hover details.
- **Technical Indicators**: Built-in support for SMA, RSI, MACD, Bollinger Bands, and more via `pandas-ta`.
- **Strategy Lab**: A dedicated environment to write, edit, and backtest custom trading strategies using Python.
- **Backtesting Engine**:
    - Simulates trades based on your custom logic.
    - Calculates Total Return and Trade Count.
    - Visualizes Equity Curve.
    - Displays Buy/Sell signals directly on the chart.
- **Price Overlays**: Manually add Support/Resistance lines.

## Prerequisites

Before running this application, ensure you have the following installed:

1.  **MetaTrader 5 (MT5)**: The terminal must be installed and **running** on your machine.
    - Ensure "Algo Trading" is enabled in MT5 settings (optional but recommended).
2.  **Python 3.9+**: [Download Python](https://www.python.org/downloads/)

## Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/yourusername/algo-chart-tool.git
    cd algo-chart-tool
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r backend/requirements.txt
    pip install streamlit plotly
    ```

## Usage

1.  **Start MetaTrader 5**: Open your MT5 terminal and login to your account.
2.  **Run the App**:
    ```bash
    python -m streamlit run app.py
    ```
3.  **Access the GUI**: The application will automatically open in your default web browser (usually at `http://localhost:8501`).

## How to Use

### 1. Dashboard & Connection
- The sidebar displays the **MT5 Connection Status**.
- If disconnected, ensure MT5 is running and click the **Reconnect** button.

### 2. Charting
- **Symbol**: Enter the symbol exactly as it appears in your MT5 Market Watch (e.g., `EURUSD`, `BTCUSD`, `XAUUSD`).
- **Timeframe**: Select your desired timeframe (M1, H1, D1, etc.).
- **Candles**: Adjust the number of historical candles to load.

### 3. Strategy Lab (Backtesting)
- Navigate to the **Strategy Lab** section below the chart.
- Write your strategy logic in the code editor. You must define a `generate_signals(df)` function that returns:
    - `1` for Buy
    - `-1` for Sell
    - `0` for Hold
- Click **Run Backtest** to see performance metrics and visualize trade signals on the chart.

### 4. Price Limits
- Use the **Chart Overlays** section in the sidebar to add horizontal lines for price levels (e.g., support or resistance).

## Project Structure

```
algo_chart_tool/
├── app.py                 # Main Streamlit application (Frontend & UI Logic)
├── backend/
│   ├── main.py            # FastAPI backend (Optional/Alternative entry point)
│   ├── mt5_bridge.py      # MetaTrader 5 connection handler
│   ├── analysis_engine.py # Backtesting and Indicator logic
│   └── requirements.txt   # Project dependencies
└── README.md              # Documentation
```

## Disclaimer

**Trading carries a high level of risk.** This tool is for educational and analytical purposes only. Past performance is not indicative of future results. The authors are not responsible for any financial losses incurred while using this software.
