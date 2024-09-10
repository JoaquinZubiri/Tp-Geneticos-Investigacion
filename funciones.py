from random import *
import pandas as pd
import numpy as np
import tkinter as tk
import ta
import matplotlib.pyplot as plt

# Ruleta
def ruleta(indice, intervalo):
    x = randint(0, len(intervalo)-1)
    inter = intervalo[indice[x]]
    y = uniform(inter[0], inter[1])
    return y


#Funcion para mostrar la comparativa fractal
def getHistoricalData(asset, timeframe, start, end, client):
    data = client.get_historical_klines(asset, timeframe, start, end)
    df = pd.DataFrame(data)
    df=df.iloc[:,:6]
    df.columns=["Date","Open","High","Low","Close","Volume"]
    df=df.set_index("Date")
    df.index=pd.to_datetime(df.index,unit="ms")
    df=df.astype("float")
    return df

def probAlcBaj(df: pd.DataFrame):
    probAlcista = 0
    probBajista = 0
    for i in range(0, len(df["Close"].values)):
        # print("--------")
        xDif = df["Close"].values[i] - df["Open"].values[i] # Los di vuelta, es el close - el open
        if(xDif >= 0):
            # print("Vela Alcista")
            probAlcista += xDif
        elif(xDif < 0):
            # print("Vela bajista")
            probBajista += abs(xDif)

    return probAlcista, probBajista

def probPrecio(df: pd.DataFrame):
    intervaloPrecio = []
    indicePrecio = []

    closeDf = df["Close"].values[0]
    openDf = df["Open"].values[0]
    p = abs(closeDf - openDf)    #Agregue el valor absoluto de p. Esto xq si p era negativo, quedaba un intervalo de un numero negativo y positivo. Esto hacia que por mas que sea una vela Alcista, si en la ruleta daba en un intervalo negativo, se le sumaba x lo que terminaba siendo negativo, y viceversa lo mismo.
    intervaloPrecio.append([p-p*0.0001, p + p*0.0001])
    indicePrecio.append(0)

    for i in range(1, len(df["Close"].values)):
        bandera = False
        closeDf = df["Close"].values[i]
        openDf = df["Open"].values[i]
        p = abs(closeDf - openDf)
        hayCero = False
        if p == 0 and hayCero:
            continue
        if(p == 0) and not hayCero:
            hayCero = True
        for j in range(0, len(intervaloPrecio)):
            # print("entro")
            if(p > intervaloPrecio[j][0] and p < intervaloPrecio[j][1]):
                indicePrecio.append(j)
                bandera = True
                break
        if(bandera == False):
            intervaloPrecio.append([p-p*0.0001, p + p*0.0001]) #DEFAULT: 0.0004
            indicePrecio.append(j)

    # Ordenar intervaloPrecio de menor a mayor
    intervaloPrecio, indicePrecio = zip(*sorted(zip(intervaloPrecio, indicePrecio), key=lambda x: x[0][0]))
    intervaloPrecio = list(intervaloPrecio)
    indicePrecio = list(indicePrecio)

    return intervaloPrecio, indicePrecio


def calculoEMA(df, periodo1, periodo2):
    df['EMA' + str(periodo1)] = ta.trend.ema_indicator(df['Close'], window=periodo1)
    df['EMA' + str(periodo2)] = ta.trend.ema_indicator(df['Close'], window=periodo2)
    df['Pendiente_EMA' + str(periodo1)] = df['EMA' + str(periodo1)].diff()
    df['Pendiente_EMA' + str(periodo2)] = df['EMA' + str(periodo2)].diff()

    df['Cruce Próximo'] = ((df['Pendiente_EMA' + str(periodo1)] > 0) & (df['Pendiente_EMA' + str(periodo2)] < 0)) | ((df['Pendiente_EMA' + str(periodo1)] < 0) & (df['Pendiente_EMA' + str(periodo2)] > 0))
    return df

def nuevoIndice(alcista, signoPositivo, indicePrecio, intervaloPrecio, puntoRecorte):
    if(alcista and signoPositivo):
        coleccion_indices = []
        for i in range(0, puntoRecorte):
            coleccion_indices.append(i)
    elif(alcista and not signoPositivo):
        coleccion_indices = []
        for i in range(0, len(intervaloPrecio)-puntoRecorte):
            coleccion_indices.append(i)
    elif(not alcista and signoPositivo):
        coleccion_indices = []
        for i in range(0, len(intervaloPrecio)-puntoRecorte):
            coleccion_indices.append(i)
    elif(not alcista and not signoPositivo):
        coleccion_indices = []
        for i in range(0, puntoRecorte):
            coleccion_indices.append(i)

    nuevo_arreglo = []
    for indice in coleccion_indices:
        conteo = indicePrecio.count(indice)
        nuevo_arreglo.extend([indice] * conteo)

    return nuevo_arreglo


def rectasEMA(arr,):
    ## Calculo de rectas por regresion lineal por minimos cuadrados
    x_inicial = arr.iloc[-1]["Date"].timestamp()

    coleccion_x = []
    for i in range(1, 5):
        coleccion_x.append(arr.iloc[-i]["Date"].timestamp())
    coleccion_y_200 = []
    for i in range(1, 5):
        coleccion_y_200.append(arr.iloc[-i]["EMA200"])
    coleccion_y_50 = []
    for i in range(1, 5):
        coleccion_y_50.append(arr.iloc[-i]["EMA50"])

    n = len(coleccion_x)
    sum_x_y_200 = sum([coleccion_x[i] * coleccion_y_200[i] for i in range(n)])
    sum_x = sum(coleccion_x)
    sum_y_200 = sum(coleccion_y_200)
    sum_x_squared = sum([coleccion_x[i] ** 2 for i in range(n)])

    m2 = (n*sum_x_y_200 - sum_x*sum_y_200)/(n*sum_x_squared - sum_x**2) ## Pendiente
    b2 = (sum_y_200 - m2*sum_x)/n ## Ordenada al origen

    sum_x_y_50 = sum([coleccion_x[i] * coleccion_y_50[i] for i in range(n)])
    sum_y_50 = sum(coleccion_y_50)

    m50 = (n*sum_x_y_50 - sum_x*sum_y_50)/(n*sum_x_squared - sum_x**2) ## Pendiente
    b50 = (sum_y_50 - m50*sum_x)/n ## Ordenada al origen


    x_intersect = (b50 - b2) / (m2 - m50)
    y_intersect = m2 * x_intersect + b2

    x_intersect = pd.to_datetime(x_intersect, unit='s').floor('min')

    # Generar los valores de x para graficar
    x_values = np.linspace(x_inicial, x_inicial+7200, 120)

    # Ecuaciones de las rectas
    y_values200 = m2 * x_values + b2
    y_values50 = m50 * x_values + b50
    x_values = pd.to_datetime(x_values, unit='s').floor('min')

    return x_values, y_values200, y_values50, x_intersect



def prediccionCorrida(arr, muestraRan, probAlcista, probBajista, indicePrecio, intervaloPrecio):

    x_values, y_values200, y_values50, x_intersect = rectasEMA(arr)

    ema_referencia = y_values200
    if(x_intersect > arr.iloc[-1]['Date']):
        interseccion = True
    else:
        interseccion = False

    for i in range(0, muestraRan):

        if(arr['Cruce Próximo'].iloc[-1]):
            aux = probAlcista
            probAlcista = probBajista
            probBajista = aux

        if(x_intersect < arr.iloc[-1]['Date'] and interseccion):
            ema_referencia = y_values50

        z = randint(1, 100)
        ultima_fila = arr.iloc[-1]
        nueva_fecha = ultima_fila['Date'] + pd.Timedelta(minutes=1)

        distancia = (arr.iloc[-1]["Close"] - ema_referencia[i]) / ema_referencia[i]

        ### RANGO 2hs
        # # print("distancia: ", distancia)
        # if abs(distancia) < 0.0015:
        #     recorte = 0.8  # Recortar al 80%
        # elif abs(distancia) < 0.0025:
        #     recorte = 0.7   # Recortar al 70%
        # elif abs(distancia) < 0.0055:
        #     recorte = 0.6  # Recortar al 60%
        # elif abs(distancia) < 0.015:
        #     recorte = 0.4  # Recortar al 40%
        # else:
        #     recorte = 0.2  # Recortar al 10%
        
        ### RANGO 1h
        # print("distancia: ", distancia)
        if abs(distancia) < 0.0015:
            recorte = 0.95  # Recortar al 95%
        elif abs(distancia) < 0.0025:
            recorte = 0.8   # Recortar al 80%
        elif abs(distancia) < 0.0055:
            recorte = 0.7  # Recortar al 70%
        elif abs(distancia) < 0.015:
            recorte = 0.6  # Recortar al 40%
        else:
            recorte = 0.5  # Recortar al 10%


        long_intervaloPrecio = len(intervaloPrecio)
        puntoRecorte = int(long_intervaloPrecio * recorte)
        signoPositivo = distancia>0

        if z <= probAlcista*100:
            # Probabilidad Alcista
            if(signoPositivo):
                intervalo_nuevo = intervaloPrecio[:puntoRecorte]
            else:
                intervalo_nuevo = intervaloPrecio[puntoRecorte:]

            indice_nuevo = nuevoIndice(True, signoPositivo,indicePrecio, intervaloPrecio, puntoRecorte)

            nuevo_precio = arr.iloc[-1]["Close"] + ruleta(indice_nuevo, intervalo_nuevo)

        else:
            # Probabilidad Bajista
            if(signoPositivo):
                intervalo_nuevo = intervaloPrecio[puntoRecorte:]
            else:
                intervalo_nuevo = intervaloPrecio[:puntoRecorte]

            indice_nuevo = nuevoIndice(False, signoPositivo, indicePrecio, intervaloPrecio, puntoRecorte)
            nuevo_precio = arr.iloc[-1]["Close"] - ruleta(indice_nuevo, intervalo_nuevo)


        nueva_fila = pd.DataFrame({'Date': [nueva_fecha], 'Close': [nuevo_precio]})
        arr = pd.concat([arr, nueva_fila])
        arr = calculoEMA(arr, 50, 200)

    grafica200 = pd.DataFrame({'Date': x_values})
    grafica200['Value'] = y_values200
    grafica50 = pd.DataFrame({'Date': x_values})
    grafica50['Value'] = y_values50
    return arr, grafica200, grafica50




### ANALISIS POSTERIOR ###
# Función para calcular el error relativo de las predicciones
def calcu_error_rela(data, arr2):
    error_rela = 0
    for i in range(0, len(arr2)):
        error_rela += abs((arr2.iloc[i]["Close"] - data.iloc[i]["Close"])/arr2.iloc[i]["Close"])
    return error_rela * 100

def mejorResultado(corridas,original):
    error_rela = 100
    for i in range (0, len(corridas)):
        error_local = calcu_error_rela(corridas[i],original)
        if error_local < error_rela:
            error_rela = error_local
            mejor_corrida = corridas[i]

    return mejor_corrida

def peorResultado(corridas,original):
    error_rela = 0
    for i in range (0, len(corridas)):
        error_local = calcu_error_rela(corridas[i],original)
        if error_local > error_rela:
            error_rela = error_local
            peor_corrida = corridas[i]
    return peor_corrida

