from random import *
import pandas as pd
import numpy as np
import tkinter as tk

# Ruleta
def ruleta(indice, intervalo):
    x = randint(0, len(indice)-1)
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

def probVolumen(df: pd.DataFrame):
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

    return intervaloVolumen, indiceVolumen

def probPrecio(df: pd.DataFrame):
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
            if(p > intervaloPrecio[j][0] and p < intervaloPrecio[j][1]):
                indicePrecio.append(j)
                bandera = True
                break
        if(bandera == False):
            intervaloPrecio.append([p-p*0.0004, p + p*0.0004]) #DEFAULT: 0.0004
            indicePrecio.append(j)

    return intervaloPrecio, indicePrecio

def hurst_exponent(time_series):
    N = len(time_series)
    T = np.arange(1, N + 1)
    mean_series = np.mean(time_series)
    # Retorno acumulado
    X = np.cumsum(time_series - mean_series)
    # Rango rescalado (R/S)
    R = np.max(X) - np.min(X)
    S = np.std(time_series)
    # Evitar división por cero
    if S == 0:
        return 0
    R_S = R / S
    # Hurst exponent (H)
    hurst_exp = np.log(R_S) / np.log(N)
    return hurst_exp

def prediccionCorrida(arr, muestraRan, probAlcista, indicePrecio, intervaloPrecio):
    for i in range(0, muestraRan): 
        z = randint(1, 100)
        # Probabilidad Alcista
        if z <= probAlcista*100: 
            arr.append(arr[-1] + ruleta(indicePrecio, intervaloPrecio))
        else:
            # Probabilidad Bajista    
            arr.append(arr[-1] - ruleta(indicePrecio, intervaloPrecio)) 

    return arr


### ANALISIS POSTERIOR ###
# Función para calcular el error relativo de las predicciones
def calcu_error_rela(data, arr2):
    error_rela = 0
    for i in range(0, len(arr2)):
        error_rela += abs((arr2[i] - data[i])/arr2[i])
    return error_rela * 100


def analisisPosterior(df, df2, arr, arr2, arr3, arr4):
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
