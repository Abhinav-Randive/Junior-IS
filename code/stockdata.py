import yfinance as yf
import pandas as pd
import os

os.makedirs("data", exist_ok=True)

print("Downloading S&P 500 Data")

data = yf.download(
    "^GSPC",
    period="5d",
    interval="1m",
    progress=False
)

data.reset_index(inplace=True)

# Flatten MultiIndex columns if present
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]

print("Columns:", data.columns)

data = data[["Datetime", "Close", "Volume"]]
data.columns = ["timestamp", "price", "quantity"]

data["timestamp"] = pd.to_datetime(data["timestamp"]).astype("int64") // 10**9

data.to_csv("data/sp500.csv", index=False)

print("Saved to data/sp500.csv")
