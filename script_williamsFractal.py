import ta.trend
import yfinance as yf
import pandas as pd
import numpy as np
import ta

import matplotlib.pyplot as plt
import mplfinance as mpf

buys, sells = [], []

#Obtener datos historicos de BTC-USD
df_15m = yf.download("MSFT", start="2024-07-01", interval="15m")

#Calcular medias moviles
df_15m["EMA200"] = ta.trend.ema_indicator(df_15m["Close"], window=200)

#Calcular Williams Fractal (usando Rolling max y min function)
df_15m["wf_Top_Bool"] = np.where(df_15m["High"] == df_15m["High"].rolling(9, center=True).max(), True, None)

df_15m["wf_Top"] = np.where(df_15m["High"] == df_15m["High"].rolling(9, center=True).max(), df_15m["High"], None)

df_15m["wf_Bottom"] = np.where(df_15m["Low"] == df_15m["Low"].rolling(9, center=True).min(), df_15m["Low"], None)

#Llenar las celdas vacias con el ultimo valor valido (en la columna wf_Top y wf_Bottom)
df_15m["wf_Top"] = df_15m["wf_Top"].ffill()
df_15m["wf_Bottom"] = df_15m["wf_Bottom"].ffill()



#Elimina las filas con valores nulos
df_15m.dropna(inplace=True)


#Condicion de compra
df_15m["Buy"] = np.where((df_15m.Close > df_15m.wf_Top) & (df_15m.Close > df_15m.EMA200),True, False)

#Condicion de StopLoss
df_15m["StopLoss"] = np.where(df_15m.Buy == True , df_15m.Close - (df_15m.Close - df_15m.Low), False)

#Condicion de Beneficio Objetivo (TargetProfit)
df_15m["TargetProfit"] = np.where(df_15m.Buy == True , df_15m.Close + (df_15m.Close - df_15m.Low)*1.5, False)

#Encontrar fechas de compra y venta
for i in range(len(df_15m)):
  if df_15m.Buy.iloc[i]:
    buys.append(df_15m.iloc[i].name)
    for j in range(len(df_15m) - i):
      if df_15m.TargetProfit.iloc[i] < df_15m.Close.iloc[i+j] or df_15m.StopLoss.iloc[i] > df_15m.Close.iloc[i+j]:
        sells.append(df_15m.iloc[i+j].name)
        break
    
#Listar las fechas de compra y venta
frame = pd.DataFrame([buys, sells]).T.dropna()
frame.columns = ["Buys", "Sells"]

actualTrades = frame[frame.Buys > frame.Sells.shift(1)]

#Calcular profit
profits = ((df_15m.loc[actualTrades.Sells].Close.values - df_15m.loc[actualTrades.Buys].Close.values) / df_15m.loc[actualTrades.Buys].Close.values)


# print(frame.head(20))
# print(actualTrades)
# print(profits)

#Media de los beneficios
# print(profits.mean()) 

#Beneficio si se hubiera comprado al inicio
# print((df_15m.Close.pct_change() + 1).cumprod()) 

plt.figure(figsize=(14,7))
plt.plot(df_15m['Close'], label='Precio de Cierre')
plt.plot(df_15m['EMA200'], label='EMA200')
plt.scatter(df_15m.index, df_15m['wf_Top'], color='green', marker='^', label='Fractal Superior')
plt.scatter(df_15m.index, df_15m['wf_Bottom'], color='red', marker='v', label='Fractal Superior')
plt.scatter(df_15m.index[df_15m['Buy']], df_15m['Close'][df_15m['Buy']], color='violet', marker='o', label='Compra')
plt.scatter(df_15m.index[df_15m['TargetProfit'] != False], df_15m['TargetProfit'][df_15m['TargetProfit'] != False], color='blue', marker='o', label='Target Profit')

plt.legend()
plt.show()


# Crear las listas de anotaciones para los fractales
ap = [
    mpf.make_addplot(df_15m['wf_Top'], scatter=True, markersize=50, marker='^', color='g'),
    mpf.make_addplot(df_15m['wf_Bottom'], scatter=True, markersize=50, marker='v', color='r')
]

# Graficar las velas con los fractales
mpf.plot(df_15m, type='candle', style='charles', addplot=ap,
        title='Fractales de Williams en BTC-USD',
        ylabel='Precio',
        volume=True)