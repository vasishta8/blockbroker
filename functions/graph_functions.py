import requests
import os
from dotenv import load_dotenv
import ccxt.async_support as ccxt
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from io import BytesIO

load_dotenv()
exchange = ccxt.binance()

periods = {
    "24H": ("15m", 96),
    "1M": ("1d", 30),
    "3M": ("1d", 90),
    "1Y": ("1w", 52),
    "YTD": ("1d", None)
}


async def graph_analysis(coin: str, period: str = "1M"):
    try:
        timeframe, limit = periods[period]
        if period == "YTD":
            start_of_year = pd.Timestamp.now().normalize().replace(month=1, day=1)
            since = int(start_of_year.timestamp() * 1000)
            bars = await exchange.fetch_ohlcv(
                f'{coin}/USDT', timeframe='1d', since=since)
            df = pd.DataFrame(
                bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        else:
            bars = exchange.fetch_ohlcv(
                f'{coin}/USDT', timeframe=timeframe, limit=limit)
            df = pd.DataFrame(
                bars, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

        df.set_index('Timestamp', inplace=True)

    except Exception as e:
        return 404, "Unable to find the requested coin"

    buf = BytesIO()

    mc = mpf.make_marketcolors(
        up='green', down='red',
        edge='inherit', wick='white',
        volume='in'
    )
    dark_style = mpf.make_mpf_style(
        base_mpl_style="dark_background",
        marketcolors=mc,
        facecolor="black", edgecolor="white",
        gridcolor="gray", gridstyle="--",
        figcolor="black"
    )

    await mpf.plot(
        df,
        type="candle",
        style=dark_style,
        title=f"{coin}/USDT - Candlestick Chart",
        ylabel="Price (USDT)",
        ylabel_lower="Volume",
        volume=True,
        figratio=(14, 7),
        figscale=1.5,
        tight_layout=True,
        savefig=dict(fname=buf, dpi=150, bbox_inches="tight")
    )
    buf.seek(0)

    dataframe_context = df.tail(10).to_markdown()
    return 200, {"context": dataframe_context, "dataframe": df}, buf
