from binance import Client
import pandas as pd
import datetime as dt
import mplfinance as mpl
import matplotlib.pyplot as plt
from boxCounting import fractal_dimension
import config as cfg

#Config API
api_key = cfg.api_key
api_secret = cfg.api_secret
client = Client(api_key, api_secret)


#Funcion para obtener datos historicos
def get_historical_data(asset, timeframe, start, end):
  data = client.get_historical_klines(asset, timeframe, start, end)
  df = pd.DataFrame(data)
  df=df.iloc[:,:6]
  df.columns=["Date","Open","High","Low","Close","Volume"]
  df=df.set_index("Date")
  df.index=pd.to_datetime(df.index,unit="ms")
  df=df.astype("float")
  return df


#Obtener datos historicos de BTCUSDT
asset="BTCUSDT"

start_5m="2024.07.20"
end_5m="2024.07.27"
data_5m = get_historical_data(asset, Client.KLINE_INTERVAL_5MINUTE, start_5m, end_5m)

start_1h="2024.07.01"
end_1h="2024.07.31"
data_1h = get_historical_data(asset, Client.KLINE_INTERVAL_1HOUR, start_1h, end_1h)



#Graficar datos con mplfinance
mpl.plot(data_5m, type='candle', volume=True, mav=7, title="BTCUSDT - Intervalo de 5 minutos (MPL)")
mpl.plot(data_1h, type='candle', volume=True, mav=7, title="BTCUSDT - Intervalo de 1 hora (MPL)")


#Graficar datos de cierre para comparar
plt.figure(figsize=(12, 7))
plt.subplot(2, 1, 1)
plt.plot(data_5m["Close"], label="5 minutos")
plt.title("BTCUSDT - Intervalo de 5 minutos (PLT)")
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(data_1h["Close"], label="1 hora")
plt.title("BTCUSDT - Intervalo de 1 hora (PLT)")
plt.legend()

plt.tight_layout()
plt.show()


#Calcular dimension fractales
dim_5m = fractal_dimension(data_5m["Close"].values, 10)
dim_1h = fractal_dimension(data_1h["Close"].values, 10)

print(f"Dimension fractal (5 minutos): {dim_5m}")
print(f"Dimension fractal (1 hora): {dim_1h}")


#Comparar las dimensiones fractales
diff = dim_5m - dim_1h

print(f"Diferencia de dimensiones fractales: {diff}")
