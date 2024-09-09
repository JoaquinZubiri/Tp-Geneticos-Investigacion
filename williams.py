import yfinance as yf
import ta
import numpy as np
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt

# Descargar datos históricos de BTC-USD
df_15m = yf.download("BTC-USD", start="2024-08-10", end="2024-08-12",interval="1m")

print(df_15m)

# Calcular los fractales de Williams superiores e inferiores
df_15m["wf_Top"] = np.nan
df_15m["wf_Bottom"] = np.nan

rolling_high = df_15m["Close"].rolling(10, center=True)
rolling_low = df_15m["Open"].rolling(10, center=True)


# Calcular medias móviles
df_15m['EMA20'] = ta.trend.ema_indicator(df_15m['Close'], window=20)
df_15m['EMA50'] = ta.trend.ema_indicator(df_15m['Close'], window=50)
df_15m['EMA100'] = ta.trend.ema_indicator(df_15m['Close'], window=100)
df_15m['EMA200'] = ta.trend.ema_indicator(df_15m['Close'], window=200)

# Definir la tendencia del mercado
def determine_trend(df):
    if df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1] and df['EMA50'].iloc[-1] > df['EMA100'].iloc[-1]:
        return 'bullish'
    elif df['EMA20'].iloc[-1] < df['EMA50'].iloc[-1] and df['EMA50'].iloc[-1] < df['EMA100'].iloc[-1]:
        return 'bearish'
    else:
        return 'neutral'

# Calcular la tendencia del mercado
market_trend = determine_trend(df_15m)
   
        
for i in range(4, len(df_15m) - 4):
    high_val = df_15m["Close"].iloc[i]
    low_val = df_15m["Open"].iloc[i]
    
    is_high_fractal = high_val == rolling_high.max().iloc[i]
    is_low_fractal = low_val == rolling_low.min().iloc[i]
    
    if is_high_fractal and is_low_fractal:
        # Aplicar criterios para decidir cuál fractal tomar
        # Ejemplo: Priorizar fractal superior si la tendencia es alcista
        if market_trend == 'bullish':
            df_15m.loc[df_15m.index[i], "wf_Top"] = high_val
            df_15m.loc[df_15m.index[i], "wf_Bottom"] = None
        else:
            df_15m.loc[df_15m.index[i], "wf_Top"] = None
            df_15m.loc[df_15m.index[i], "wf_Bottom"] = low_val
    else:
        if is_high_fractal:
            df_15m.loc[df_15m.index[i], "wf_Top"] = high_val
        if is_low_fractal:
            df_15m.loc[df_15m.index[i], "wf_Bottom"] = low_val


# Preparar los datos para mplfinance
df_15m.index.name = 'Date'
df_15m.index = pd.to_datetime(df_15m.index)
df_15m = df_15m[['Open', 'High', 'Low', 'Close', 'Volume', 'wf_Top', 'wf_Bottom', 'EMA20', 'EMA50', 'EMA100', 'EMA200']]

# Crear las listas de anotaciones para los fractales
ap = [
    mpf.make_addplot(df_15m['wf_Top'], scatter=True, markersize=100, marker='^', color='g'),
    mpf.make_addplot(df_15m['wf_Bottom'], scatter=True, markersize=100, marker='v', color='r'),
    mpf.make_addplot(df_15m['EMA20'], color='blue'),
    mpf.make_addplot(df_15m['EMA50'], color='orange'),
    mpf.make_addplot(df_15m['EMA100'], color='red' ),
    mpf.make_addplot(df_15m['EMA200'], color='violet' )
    

]

# Graficar las velas con los fractales
mpf.plot(df_15m, type='candle', style='binance', addplot=ap,
        title='Fractales de Williams en BTC-USD',
        ylabel='Precio',
        volume=True)


# Filtrar los valores no nulos
top_points = df_15m[['wf_Top']].dropna()
bottom_points = df_15m[['wf_Bottom']].dropna()

# Combinar los puntos en un solo DataFrame
combined_points = pd.concat([top_points, bottom_points]).sort_index()

print(combined_points)

intercalated_df = combined_points.stack().reset_index(level=1, drop=True).to_frame('value')

print(intercalated_df)

plt.plot(intercalated_df.index, intercalated_df['value'])
plt.show()