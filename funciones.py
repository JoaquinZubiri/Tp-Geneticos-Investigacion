from random import *
import pandas as pd
import numpy as np
import tkinter as tk
import ta
import matplotlib.pyplot as plt

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
        for j in range(0, len(intervaloPrecio)):
            # print("entro")
            if(p > intervaloPrecio[j][0] and p < intervaloPrecio[j][1]):
                indicePrecio.append(j)
                bandera = True
                break
        if(bandera == False):
            intervaloPrecio.append([p-p*0.0001, p + p*0.0001]) #DEFAULT: 0.0004
            indicePrecio.append(j)

    return intervaloPrecio, indicePrecio


def calculoEMA(df, periodo1, periodo2):
    df['EMA' + str(periodo1)] = ta.trend.ema_indicator(df['Close'], window=periodo1)
    df['EMA' + str(periodo2)] = ta.trend.ema_indicator(df['Close'], window=periodo2)
    df['Pendiente_EMA' + str(periodo1)] = df['EMA' + str(periodo1)].diff()
    df['Pendiente_EMA' + str(periodo2)] = df['EMA' + str(periodo2)].diff()

    df['Cruce Próximo'] = ((df['Pendiente_EMA' + str(periodo1)] > 0) & (df['Pendiente_EMA' + str(periodo2)] < 0)) | ((df['Pendiente_EMA' + str(periodo1)] < 0) & (df['Pendiente_EMA' + str(periodo2)] > 0))
    return df



def prediccionCorrida(arr, muestraRan, probAlcista, probBajista, indicePrecio, intervaloPrecio):
    # prox_cruce_aprox = (arr.iloc[-1].name - ultimo_quiebre.name)

    # if(prox_cruce_aprox < tiempo_estimado_quiebre):
    #     prox_cruce_aprox = tiempo_estimado_quiebre - prox_cruce_aprox
    x_inicial = arr.iloc[-1]["Date"].timestamp()
    x_final = arr.iloc[-2]["Date"].timestamp()

    coleccion_x = []
    for i in range(1, 10):
        coleccion_x.append(arr.iloc[-i]["Date"].timestamp())
    coleccion_y_200 = []
    for i in range(1, 10):
        coleccion_y_200.append(arr.iloc[-i]["EMA200"])
    coleccion_y_50 = []
    for i in range(1, 10):
        coleccion_y_50.append(arr.iloc[-i]["EMA50"])


    x11, y11 = x_inicial, arr.iloc[-1]["EMA50"]  # Punto de inicio para la primera recta
    x12, y12 = x_final, arr.iloc[-2]["EMA50"]  # Punto de fin para la primera recta


    x21, y21 = x_inicial, arr.iloc[-1]["EMA200"]  # Punto de inicio para la segunda recta
    x22, y22 = x_final, arr.iloc[-2]["EMA200"]  # Punto de fin para la segunda recta

    # Pendientes
    m1 = (y12 - y11) /(x12 - x11)  # Pendiente de la primera recta
    print("m1: ", m1)
    m2 = (y22-y21)/(x22-x21)  # Pendiente de la segunda recta
    print("m2: ", m2)

    # Ecuaciones de las rectas
    # y = mx + b -> Despejamos b = y - mx
    b1 = y11 - m1 * x11  # Ordenada al origen de la primera recta
    print("b1: ", b1)
    b2 = y21 - m2 * x21  # Ordenada al origen de la segunda recta
    print("b2: ", b2)

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


    x_intersect = (b2 - b1) / (m1 - m2)
    y_intersect = m1 * x_intersect + b1

    x_intersect = pd.to_datetime(x_intersect, unit='s').floor('min')
    print("x_intersect: ", x_intersect)

    # Generar los valores de x para graficar
    x_values = np.linspace(x_inicial, x_inicial+7200, 120)

    # Ecuaciones de las rectas
    y_values1 = m1 * x_values + b1
    y_values200 = m2 * x_values + b2
    y_values50 = m50 * x_values + b50
    print("y_values2: ", y_values200)
    print("y_values50: ", y_values50)

    y_values_resultante = (y_values200 + y_values50) / 2


    x_values = pd.to_datetime(x_values, unit='s').floor('min')
    # Graficar las dos rectas
    # plt.figure(figsize=(8,6))
    # plt.plot(x_values, y_values1, label=f'Recta 1: Pendiente {m1}', color='blue')
    # plt.plot(x_values, y_values2, label=f'Recta 2: Pendiente {m2}', color='green')

    # # Graficar el punto de intersección
    # plt.plot(x_intersect, y_intersect, 'ro', label=f'Intersección ({x_intersect:.2f}, {y_intersect:.2f})')

    # # Añadir etiquetas y leyenda
    # plt.title('Gráfica de dos rectas con sus intersecciones')
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.legend()
    # plt.grid(True)

    # Mostrar la gráfica
    # plt.show()
    for i in range(0, muestraRan):
        # print("interacion: ", i)
        # print("probAlcista: ", probAlcista)
        # print("probBajista: ", probBajista)
        
        if(arr['Cruce Próximo'].iloc[-1]):
            aux = probAlcista
            probAlcista = probBajista
            probBajista = aux

        # probAlcista, probBajista = calculoPropAlc(arr, probAlcista, probBajista)

        z = randint(1, 100)
        ultima_fila = arr.iloc[-1]
        nueva_fecha = ultima_fila['Date'] + pd.Timedelta(minutes=1)
        rango200_lower = y_values200[i] - (y_values200[i] * 0.0009)
        # print("VALUE", y_values2[i])
        # print("rango200_lower: ", rango200_lower)
        rango200_upper = y_values200[i] + (y_values200[i] * 0.0009)

        # print("rango200_upper: ", rango200_upper)
        if z <= probAlcista*100:
            # Probabilidad Alcista
            nuevo_precio = y_values200[i] + ruleta(indicePrecio, intervaloPrecio)
            while nuevo_precio >= rango200_upper:
                # print("nuevo_precio: ", nuevo_precio)
                nuevo_precio = y_values200[i] + ruleta(indicePrecio, intervaloPrecio)


        else:
            # Probabilidad Bajista
            nuevo_precio = y_values200[i] - ruleta(indicePrecio, intervaloPrecio)
            while nuevo_precio <= rango200_lower :
                # print("nuevo_precio: ", nuevo_precio)
                nuevo_precio = y_values200[i] - ruleta(indicePrecio, intervaloPrecio)
        nueva_fila = pd.DataFrame({'Date': [nueva_fecha], 'Close': [nuevo_precio]})
        arr = pd.concat([arr, nueva_fila])
        arr = calculoEMA(arr, 50, 200)

    grafica200 = pd.DataFrame({'Date': x_values})
    grafica200['Value'] = y_values200
    grafica50 = pd.DataFrame({'Date': x_values})
    grafica50['Value'] = y_values50
    return arr, grafica200, grafica50


def calculoPuntoQuiebre(df):
    punto_quiebre = []
    quiebre = 0
    for d in range(len(df)):
        if 'EMA200' in df.columns and not pd.isna(df.iloc[d]["EMA200"]):
            if df.iloc[d]["EMA50"] - df.iloc[d]["EMA200"] > 0 and quiebre < 0:
                punto_quiebre.append(df.iloc[d])
            elif df.iloc[d]["EMA50"] - df.iloc[d]["EMA200"] < 0 and quiebre > 0:
                punto_quiebre.append(df.iloc[d])
            quiebre = df.iloc[d]["EMA50"] - df.iloc[d]["EMA200"]
    return punto_quiebre


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
