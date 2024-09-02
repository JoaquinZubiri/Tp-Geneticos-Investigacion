from binance import Client
import pandas as pd
import datetime as dt
import tkinter as tk
import mplfinance as mpl
import matplotlib.pyplot as plt
from boxCounting import fractal_dimension
import config as cfg
from random import *

#Config API
api_key = cfg.api_key
api_secret = cfg.api_secret
client = Client(api_key, api_secret)
price = client.get_symbol_ticker(symbol="BTCUSDT")

#Parametros para las salidas
tiempo_referencia = 1                                            # Tamaño de la vela
añopredict = 2024               
horaInicioprincipal = 15                                         # Hora en la que se inicia la grafica principal a predecir
horaIniciopredict = 20 
horasDePredict = 1                                               # Tiempo de prediccion
horaFinpredict = horaIniciopredict + horasDePredict              # Horario fin de la prediccion

tiempo_init = dt.time(horaInicioprincipal,0,0) #Formato HIPP:00:00
tiempo_current = dt.time(horaIniciopredict,0,0) #Formato HIP:00:00
tiempo_fin_predict = dt.time(horaFinpredict,0,0) #Formato HFP:00:00

print("precio", price)
asset="BTCUSDT"
start= str(añopredict) + ".07.15" + " " + str(tiempo_init)
end= str(añopredict) + ".07.15" + " " + str(tiempo_current)
startPredict= str(añopredict) + ".07.15"+ " " + str(tiempo_current)
endPredict= str(añopredict) + ".07.15" + " " + str(tiempo_fin_predict)
timeframe= str(tiempo_referencia) + "m"
data = client.get_historical_klines(asset, timeframe, start, end)
df= pd.DataFrame(client.get_historical_klines(asset, timeframe, start, end))
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

#GRAFICO DE VELAS INICIO
mpl.plot(df, type='candle', volume=False, mav=7, title="Gráfico de Velas - " + asset)

#Funcion para mostrar la comparativa fractal
def get_historical_data(asset, timeframe, start, end):
  data = client.get_historical_klines(asset, timeframe, start, end)
  df = pd.DataFrame(data)
  df=df.iloc[:,:6]
  df.columns=["Date","Open","High","Low","Close","Volume"]
  df=df.set_index("Date")
  df.index=pd.to_datetime(df.index,unit="ms")
  df=df.astype("float")
  return df

#Seteo de los datos de cada intervalo
data_1m = get_historical_data(asset, Client.KLINE_INTERVAL_1MINUTE, start, end)
data_5m = get_historical_data(asset, Client.KLINE_INTERVAL_5MINUTE, start, end)
data_15m = get_historical_data(asset, Client.KLINE_INTERVAL_15MINUTE, start, end)

#GRAFICAS COMPARATIVAS PARA VER COMPOSICION FRACTAL
plt.figure(figsize=(12, 9))

plt.subplot(3, 1, 1)
plt.plot(data_1m["Close"], label="1 minutos")
plt.title("BTCUSDT - Intervalo de 1 minuto")
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(data_5m["Close"], label="5 min")
plt.title("BTCUSDT - Intervalo de 5 min")
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(data_15m["Close"], label="15 min")
plt.title("BTCUSDT - Intervalo de 15 min")
plt.legend()

plt.tight_layout()
plt.show()

# #Podemos hacer este calculo de dimension fractal para ver como difieren en el valor final segun el intervalo. Serviria para la parte teorica un poco
# dim_5m = fractal_dimension(data_5m["Close"].values, 10)
# dim_1h = fractal_dimension(data_1h["Close"].values, 10)

# print(f"Dimension fractal (5 minutos): {dim_5m}")
# print(f"Dimension fractal (1 hora): {dim_1h}")


# #Comparar las dimensiones fractales
# diff = dim_5m - dim_1h

# print(f"Diferencia de dimensiones fractales: {diff}")
#Inicializacion de probabilidades

probAlcista = 0
probBajista = 0
acumVolumen = 0

for i in range(0, len(df["Close"].values)):
    # print("--------")
    xDif = df["Close"].values[i] - df["Open"].values[i] # Los di vuelta, es el close - el open 
    if(xDif >= 0):
        # print("Vela Alcista")
        probAlcista += xDif
    elif(xDif < 0):
        # print("Vela bajista")
        probBajista += abs(xDif)
acumVolumen += df["Volume"].values[i]

promVolumen = acumVolumen/len(df["Close"].values)
intervaloVolumen = []
indiceVolumen = []

v = df["Volume"].values[0]
intervaloVolumen.append([v-v*0.5, v + v*0.5])
indiceVolumen.append(0)

for i in range(1, len(df["Close"].values)):
    bandera = False
    v = df["Volume"].values[i]
    for j in range(0, len(intervaloVolumen)):
        # print("entro")
        if(v > intervaloVolumen[j][0] and v < intervaloVolumen[j][1]):
            indiceVolumen.append(j)
            bandera = True
            break
    if(bandera == False):
        intervaloVolumen.append([v-v*0.5, v + v*0.5])
        indiceVolumen.append(j)

## CALCULO DE PROBABILIDADES DE AUMENTO DE PLATA
#Seteo de los arreglos para los intervalos
intervaloPrecio = []
indicePrecio = []

closeDf = df["Close"].values[0]
openDf = df["Open"].values[0]
p = abs(closeDf - openDf)    #Agregue el valor absoluto de p. Esto xq si p era negativo, quedaba un intervalo de un numero negativo y positivo. Esto hacia que por mas que sea una vela Alcista, si en la ruleta daba en un intervalo negativo, se le sumaba x lo que terminaba siendo negativo, y viceversa lo mismo.
intervaloPrecio.append([p-p*0.0004, p + p*0.0004])
indicePrecio.append(0)

for i in range(1, len(df["Close"].values)):
    bandera = False
    closeDf = df["Close"].values[i]
    openDf = df["Open"].values[i]
    p = abs(closeDf - openDf)
    for j in range(0, len(intervaloPrecio)):
        # print("entro")
        if(v > intervaloPrecio[j][0] and v < intervaloPrecio[j][1]):
            indicePrecio.append(j)
            bandera = True
            break
    if(bandera == False):
        intervaloPrecio.append([p-p*0.0004, p + p*0.0004]) #DEFAULT: 0.0004
        indicePrecio.append(j)

print("intervaloPrecio")
print(intervaloPrecio)
print("indicePrecio")
print(indicePrecio)
print("----------")
    
xtotal = probAlcista + probBajista

probAlcista = probAlcista/xtotal
probBajista = probBajista/xtotal

print("Probabilidad Alcista: ", probAlcista)
print("Probabilidad Bajista: ", probBajista)
print("Promedio Volumen: ", promVolumen)

#uncion Ruleta
def RuletaVolumen():
    x = randint(0, len(indiceVolumen))
    intervalo = intervaloVolumen[indiceVolumen[x]]
    y = randint(intervalo[0], intervalo[1])
    return y

#Ruleta para elegir el nuevo valor de la vela
def RuletaPrecio():  
    x = randint(0, len(indicePrecio)-1)
    intervalo = intervaloPrecio[indicePrecio[x]]
    y = uniform(intervalo[0], intervalo[1])
    print("Precio: ", y)
    return y 

# Ajuste de salida para cualquier tiempo de referencia y hora (Sirve para un mismo dia, ajustar para todos los dias parametrizando los mismos) 
muestraRan=0
horaspredict = horaFinpredict - horaIniciopredict
if horaspredict <= 0:
    horaspredict +=24
if tiempo_referencia == 1:
    muestraRan = 60*horaspredict
elif tiempo_referencia == 5:
    muestraRan = 12*horaspredict
elif tiempo_referencia == 15:
    muestraRan = 4*horaspredict
elif tiempo_referencia == 30:
    muestraRan = 2*horaspredict

### Corridas prediccion
# CORRIDA 1
arr = df["Close"].values.tolist()
print(arr)
  
current = len(arr) - 1

for i in range(0, muestraRan): 
    z = randint(1, 100)
    volumen = 0
    # Probabilidad Alcista
    if z <= probAlcista*100: 
        print("ultimo", arr[-1])
        arr.append(arr[-1] + RuletaPrecio())
    else:
        # Probabilidad Bajista   
        print("ultimo", arr[-1])  
        arr.append(arr[-1] - RuletaPrecio()) 

# CORRIDA 2
arr3 = df["Close"].values.tolist()
print(arr3)
  
current = len(arr3) - 1

for i in range(0, muestraRan): 
    z = randint(1, 100)
    volumen = 0
    # Probabilidad Alcista
    if z <= probAlcista*100: 
        print("ultimo", arr3[-1])
        arr3.append(arr3[-1] + RuletaPrecio())
    else:
        # Probabilidad Bajista   
        print("ultimo", arr3[-1])  
        arr3.append(arr3[-1] - RuletaPrecio()) 

# CORRIDA 3
arr4 = df["Close"].values.tolist()
print(arr4)
  
current = len(arr4) - 1

for i in range(0, muestraRan): 
    z = randint(1, 100)
    volumen = 0
    # Probabilidad Alcista
    if z <= probAlcista*100: 
        print("ultimo", arr4[-1])
        arr4.append(arr4[-1] + RuletaPrecio())
    else:
        # Probabilidad Bajista   
        print("ultimo", arr4[-1])  
        arr4.append(arr4[-1] - RuletaPrecio()) 

#Tramo real de la moneda que queremos predecir (Para comparar resultados)
data = client.get_historical_klines(asset, timeframe, startPredict, endPredict)
df2= pd.DataFrame(client.get_historical_klines(asset, timeframe, startPredict, endPredict))
df2=df2.iloc[:,:6]
df2.columns=["Date","Open","High","Low","Close","Volume"]
df2=df2.set_index("Date")
df2.index=pd.to_datetime(df2.index,unit="ms")
df2=df2.astype("float")
print(df2)
print("--------")
print(df2["Close"].values[0])

print("----------------------------------")
print(max(df2["Volume"].values))

arr2 = df2["Close"].values.tolist()

plt.figure(figsize=(12, 7))
plt.plot(arr[:current+1], color='blue') #Close
plt.plot(range(current, len(arr)), arr[current:], color='thistle', label="Corrida 1")
plt.plot(range(current, len(arr3)), arr3[current:], color='pink', label="Corrida 2")
plt.plot(range(current, len(arr4)), arr4[current:], color='burlywood', label="Corrida 3")
plt.legend()
plt.plot(range(current, current + len(arr2)), arr2, label="Close arr2", color='blue')
plt.suptitle('Prediccion de ' + asset)
horaestudio = horaIniciopredict - horaInicioprincipal # ESTO NO ES EFICIENTE. SIRVE PARA 1 DIA NOMAS. SE PODRIAN PARAMETRIZAR LOS DIAS Y AHI SERIA, O BORRARLO A LA MIERDA. VER SI PODEMOS HACERLO PARA CUALQUIER FECHA.
if horaIniciopredict - horaInicioprincipal == 0:
    horaestudio = 24

plt.title("Tiempo de estudio: " + str(horaestudio) + "hs. Tiempo de prediccion: " + str(horaspredict) + "hs. Tamaño de velas: " + str(tiempo_referencia) + "min")
plt.axvline(x=current, color='green')
plt.show()

#Analisis posterior. 
c1 = (arr[-1]/arr2[-1]) 
c1a = (arr[-1]/df["Close"].values[-1])
c2 = (arr3[-1]/arr2[-1]) 
c2a = (arr3[-1]/df["Close"].values[-1])
c3 = (arr4[-1]/arr2[-1]) 
c3a = (arr4[-1]/df["Close"].values[-1])

cEsp = (arr2[-1]/df["Close"].values[-1])

porcEsperado = arr2[-1] - df["Close"].values[-1]

if (porcEsperado > 0):
    sentidoesperado = ' Positivo'
else:
    sentidoesperado = ' Negativo'
#Variacion esperada
if (cEsp > 1):
    cEsp -=1
else:
    cEsp = 1 - cEsp
# Variaciones obtenidas en cada corrida respecto al valor inicial
if (c1a > 1): 
    c1a -=1
    c1obtenido = " Positivo"
else:
    c1a = 1 - c1a
    c1obtenido = " Negativo"
if (c2a > 1): 
    c2a -=1
    c2obtenido = " Positivo"
else:
    c2a = 1 - c2a
    c2obtenido = " Negativo"

if (c3a > 1): 
    c3a -=1
    c3obtenido = " Positivo"
else:
    c3a = 1 - c3a
    c3obtenido = " Negativo"

ventana = tk.Tk()
ventana.geometry('1100x300')
lbl_titulo = tk.Label(ventana, text='Análisis Resultados', font=('Arial', 24))
lbl_precioEsperado = tk.Label(ventana, text='Precio de salida: $' + str(df["Close"].values[-1]) + ' - Precio esperado: $' + str(arr2[-1]), font=('Arial', 17))
lbl_variacionEsperada = tk.Label(ventana, text='Variacion esperada: %' + str(round((cEsp*100),5)) + sentidoesperado, font=('Arial', 17))
if (c1 > 1):
    c1 -=1
    lbl_impresion = tk.Label(ventana, text="Prediccion 1: $" + str(round(arr[-1],2)) + " - Variacion obtenida: %" + str(round((c1a*100),3)) + c1obtenido + " - Porcentaje de acierto respecto a la esperada: " + str(100-round((c1*100),3)) + "% +", font=('Arial',15))
elif(0 < c1 <= 1): 
    c1 = 1 - c1
    lbl_impresion = tk.Label(ventana, text="Prediccion 1: $" + str(round(arr[-1],2)) + " - Variacion obtenida: %" + str(round((c1a*100),3)) + c1obtenido + " - Porcentaje de acierto respecto a la esperada: " + str(100-round((c1*100),3)) + "% -", font=('Arial',15))

if (c2 > 1):
    c2 -= 1
    lbl_impresion2 = tk.Label(ventana, text="Prediccion 2: $" + str(round(arr3[-1],2)) + " - Variacion obtenida: %" + str(round((c2a*100),3)) + c2obtenido + " - Porcentaje de acierto respecto a la esperada: " + str(100-round((c2*100),3)) + "% +", font=('Arial',15))
elif(0 < c2 <= 1): 
    c2 = 1 - c2
    lbl_impresion2 = tk.Label(ventana, text="Prediccion 2: $" + str(round(arr3[-1],2)) + " - Variacion obtenida: %" + str(round((c2a*100),3)) + c2obtenido + " - Porcentaje de acierto respecto a la esperada: " + str(100-round((c2*100),3)) + "% -", font=('Arial',15))

if (c3 > 1):
    c3 -= 1
    lbl_impresion3 = tk.Label(ventana, text="Prediccion 3: $" + str(round(arr4[-1],2)) + " - Variacion obtenida: %" + str(round((c3a*100),3)) + c3obtenido + " - Porcentaje de acierto respecto a la esperada: " + str(100-round((c3*100),3)) + "% +", font=('Arial',15))
elif(0 < c3 <= 1): 
    c3 = 1 - c3
    lbl_impresion3 = tk.Label(ventana, text="Prediccion 3: $" + str(round(arr4[-1],2)) + " - Variacion obtenida: %" + str(round((c3a*100),3)) + c3obtenido + " - Porcentaje de acierto respecto a la esperada: " + str(100-round((c3*100),3)) + "% -", font=('Arial',15))

lbl_titulo.pack()
lbl_precioEsperado.pack()
lbl_variacionEsperada.pack()
lbl_impresion.pack()
lbl_impresion2.pack()
lbl_impresion3.pack()

lbl_impresion.place(x=2, y=120)
lbl_impresion2.place(x=2, y=150)
lbl_impresion3.place(x=2, y=180)

ventana.mainloop()

print("alcista")
print(probAlcista)
print("bajista")
print(probBajista)
# print(f"Diferencia de dimensiones fractales: {diff}")

## REGLAS
#Para las reglas podriamos definir la suba o bajada en cuestion de probabilidad de ocurrecnicas de las mismas gracias al historial sacado de la API
#Por ejemplo si el precio de cierre de la vela anterior fue mayor al de la vela actual, la probabilidad de que la vela actual sea bajista es mayor
#Por otro lado si el precio de cierre de la vela anterior fue menor al de la vela actual, la probabilidad de que la vela actual sea alcista es mayor    

#Sino se puede hacer en un espectro mas grande, calculando porencta de suba o baja en un periodo de tiempo mas grande 