from binance import Client
import pandas as pd
import datetime as dt
import mplfinance as mpl
import matplotlib.pyplot as plt
import config as cfg

api_key = cfg.api_key
api_secret = cfg.api_secret

client = Client(api_key, api_secret)
price = client.get_symbol_ticker(symbol="BTCUSDT")

print("precio", price)
asset="BTCUSDT"
start="2024.07.26"
end="2024.07.27"
timeframe="30m"
data = client.get_historical_klines(asset, timeframe, start, end)
print("--------")
print(data)
print("--------")
df= pd.DataFrame(client.get_historical_klines(asset, timeframe,start,end))
df=df.iloc[:,:6]
df.columns=["Date","Open","High","Low","Close","Volume"]
df=df.set_index("Date")
df.index=pd.to_datetime(df.index,unit="ms")
df=df.astype("float")
print(df)
import mplfinance as mpl
mpl.plot(df, type='candle', volume=True, mav=7)


plt.figure(figsize=(12, 7))
plt.plot(df["Close"], label="Close")
plt.title("BTCUSDT")
plt.show()

