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
price = client.get_symbol_ticker(symbol="BTCUSDT")

print("precio", price)
asset="BTCUSDT"
start="2024.08.14"
end="2024.08.15"
timeframe="1m"
data = client.get_historical_klines(asset, timeframe, start, end)
print("--------")
# print(data)
print("--------")
df= pd.DataFrame(client.get_historical_klines(asset, timeframe,start,end))
df=df.iloc[:,:6]
df.columns=["Date","Open","High","Low","Close","Volume"]
df=df.set_index("Date")
df.index=pd.to_datetime(df.index,unit="ms")
df=df.astype("float")
print(df)
print("--------")
print(df["Close"].values[0])

print("----------------------------------")
print(max(df["Volume"].values))

import mplfinance as mpl
mpl.plot(df, type='candle', volume=True, mav=7)


##### GRAFICAS MEJORADAS LUCHO

# #Funcion para obtener datos historicos
# def get_historical_data(asset, timeframe, start, end):
#   data = client.get_historical_klines(asset, timeframe, start, end)
#   df = pd.DataFrame(data)
#   df=df.iloc[:,:6]
#   df.columns=["Date","Open","High","Low","Close","Volume"]
#   df=df.set_index("Date")
#   df.index=pd.to_datetime(df.index,unit="ms")
#   df=df.astype("float")
#   return df


# #Obtener datos historicos de BTCUSDT
# asset="BTCUSDT"

# start_5m="2024.07.20"
# end_5m="2024.07.27"
# data_5m = get_historical_data(asset, Client.KLINE_INTERVAL_5MINUTE, start_5m, end_5m)

# start_1h="2024.07.01"
# end_1h="2024.07.31"
# data_1h = get_historical_data(asset, Client.KLINE_INTERVAL_1HOUR, start_1h, end_1h)



# #Graficar datos con mplfinance
# mpl.plot(data_5m, type='candle', volume=True, mav=7, title="BTCUSDT - Intervalo de 5 minutos (MPL)")
# mpl.plot(data_1h, type='candle', volume=True, mav=7, title="BTCUSDT - Intervalo de 1 hora (MPL)")


# #Graficar datos de cierre para comparar
# plt.figure(figsize=(12, 7))
# plt.subplot(2, 1, 1)
# plt.plot(data_5m["Close"], label="5 minutos")
# plt.title("BTCUSDT - Intervalo de 5 minutos (PLT)")
# plt.legend()

# plt.subplot(2, 1, 2)
# plt.plot(data_1h["Close"], label="1 hora")
# plt.title("BTCUSDT - Intervalo de 1 hora (PLT)")
# plt.legend()

# plt.tight_layout()
# plt.show()


# #Calcular dimension fractales
# dim_5m = fractal_dimension(data_5m["Close"].values, 10)
# dim_1h = fractal_dimension(data_1h["Close"].values, 10)

# print(f"Dimension fractal (5 minutos): {dim_5m}")
# print(f"Dimension fractal (1 hora): {dim_1h}")


# #Comparar las dimensiones fractales
# diff = dim_5m - dim_1h

# print(f"Diferencia de dimensiones fractales: {diff}")



probAlcista = 0
probBajista = 0
probNeutra = 0
acumVolumen = 0

for i in range(0, len(df["Close"].values)):
    # print("--------")
    xDif = df["Open"].values[i] - df["Close"].values[i]
    if(xDif > df["Close"].values[i]*0.0004):
        # print("Vela Alcista")
        probAlcista += xDif
    elif(xDif < df["Close"].values[i]*0.0004*-1):
        # print("Vela bajista")
        probBajista += abs(xDif)
    else:
        # print("Vela neutra")
        probNeutra += abs(xDif) 
    
    acumVolumen += df["Volume"].values[i]

    # print(xDif)

promVolumen = acumVolumen/len(df["Close"].values)
# count1 = 0
# count2 = 0
# count3 = 0
# count4 = 0
# count5 = 0

# for i in range(0, len(df["Close"].values)):
#     if(df["Volume"].values[i]> promVolumen*1.2):
#         count1 += 1
#     elif(df["Volume"].values[i]> promVolumen*0.8):
#         count2 += 1
#     elif(df["Volume"].values[i]> promVolumen*0.5):
#         count3 += 1
#     elif(df["Volume"].values[i]> promVolumen*0.2):
#         count4 += 1

# probVol1 = count1/len(df["Close"].values)
# probVol2 = count2/len(df["Close"].values)
# probVol3 = count3/len(df["Close"].values)
# probVol4 = count4/len(df["Close"].values)

intervaloVolumen = []
indiceVolumen = []

v = df["Volume"].values[0]
intervaloVolumen.append([v-v*0.5, v + v*0.5])
print("intervaloVolumen", intervaloVolumen)
indiceVolumen.append(0)

for i in range(1, len(df["Close"].values)):
    bandera = False
    v = df["Volume"].values[i]
    for j in range(0, len(intervaloVolumen)):
        print("entro")
        if(v > intervaloVolumen[j][0] and v < intervaloVolumen[j][1]):
            indiceVolumen.append(j)
            bandera = True
            break
    if(bandera == False):
        intervaloVolumen.append([v-v*0.5, v + v*0.5])
        indiceVolumen.append(j)

print("intervaloVolumen")
print(intervaloVolumen)
print("indiceVolumen")
print(indiceVolumen)
print("----------")
    
    
        

xtotal = probAlcista + probBajista + probNeutra

probAlcista = probAlcista/xtotal
probBajista = probBajista/xtotal
probNeutra = probNeutra/xtotal

print("Probabilidad Alcista: ", probAlcista)
print("Probabilidad Bajista: ", probBajista)
print("Probabilidad Neutra: ", probNeutra)
print("Promedio Volumen: ", promVolumen)
        


import matplotlib.pyplot as plt 
from random import randint 
  
# initializing the list 
x = [] 
y = [] 
arr = df
print(arr)
  
# setting first element to 0 
x.append(0) 
y.append(0) 
  
current = 0
  
for i in range(1, 50000): 
    z = randint(1, 100)
    volumen = 0
    # if z <= probVol1*100:
    #     volumen = arr["Volume"].values[i]*1.5 
    # elif z> probVol1*100 and z<= probVol1*100 + probVol2*100:
    #     volumen = arr["Volume"].values[i]
    # elif z > probVol1*100 +probVol2*100 and z<= probVol1*100 + probVol2*100 + probVol3*100:
    #     volumen = arr["Volume"].values[i]*0.5
    # else:
    #     volumen = arr["Volume"].values[i]*0.2
  
    # generates a random integer between 1 and 100 
    z = randint(1, 100) 
  
    # the x and y coordinates of the equations 
    # are appended in the lists respectively. 
      
    # Probabilidad Alcista
    if z <= probAlcista*100:
        mutacion = randint(1, 100)

        arr= arr[current]
      
    # Probabilidad Bajista    
    if z> probAlcista*100 and z<= probAlcista*100 + probBajista*100: 
        # x.append(0.85*(x[current]) + 0.04*(y[current])) 
        # y.append(-0.04*(x[current]) + 0.85*(y[current])+1.6) 
        arr.append(promVolumen*-1)
      
    # Probabilidad Neutra    
    if z > probAlcista*100 +probBajista*100 : 
        # x.append(0.2*(x[current]) - 0.26*(y[current])) 
        # y.append(0.23*(x[current]) + 0.22*(y[current])+1.6) 
        arr.append(0)
      
          
    current = current + 1
   
plt.scatter(x, y, s = 0.2, edgecolor ='green') 
  



plt.figure(figsize=(12, 7))
plt.plot(df["Close"], label="Close")
plt.title("BTCUSDT")
plt.show()


plt.show()  






## REGLAS
#Para las reglas podriamos definir la suba o bajada en cuestion de probabilidad de ocurrecnicas de las mismas gracias al historial sacado de la API
#Por ejemplo si el precio de cierre de la vela anterior fue mayor al de la vela actual, la probabilidad de que la vela actual sea bajista es mayor
#Por otro lado si el precio de cierre de la vela anterior fue menor al de la vela actual, la probabilidad de que la vela actual sea alcista es mayor    

#Sino se puede hacer en un espectro mas grande, calculando porencta de suba o baja en un periodo de tiempo mas grande 