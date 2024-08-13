import yfinance as yf
import ta
import numpy as np
import mplfinance as mpf
import pandas as pd

# Descargar datos históricos de BTC-USD
df_15m = yf.download("BTC-USD", start="2024-07-01", interval="15m")

# Calcular los fractales de Williams superiores e inferiores
df_15m["wf_Top"] = np.nan
df_15m["wf_Bottom"] = np.nan

rolling_high = df_15m["High"].rolling(9, center=True)
rolling_low = df_15m["Low"].rolling(9, center=True)

for i in range(4, len(df_15m) - 4):
    if df_15m["High"].iloc[i] == rolling_high.max().iloc[i]:
        df_15m["wf_Top"].iloc[i] = df_15m["High"].iloc[i]
    if df_15m["Low"].iloc[i] == rolling_low.min().iloc[i]:
        df_15m["wf_Bottom"].iloc[i] = df_15m["Low"].iloc[i]

# Preparar los datos para mplfinance
df_15m.index.name = 'Date'
df_15m.index = pd.to_datetime(df_15m.index)
df_15m = df_15m[['Open', 'High', 'Low', 'Close', 'Volume', 'wf_Top', 'wf_Bottom']]

# Crear las listas de anotaciones para los fractales
ap = [
    mpf.make_addplot(df_15m['wf_Top'], scatter=True, markersize=100, marker='^', color='g'),
    mpf.make_addplot(df_15m['wf_Bottom'], scatter=True, markersize=100, marker='v', color='r')
]

# Graficar las velas con los fractales
mpf.plot(df_15m, type='candle', style='charles', addplot=ap,
        title='Fractales de Williams en BTC-USD',
        ylabel='Precio',
        volume=True)


