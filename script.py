from binance import Client
import datetime as dt
import config as cfg
import numpy as np
from random import *
import ta
import pandas as pd

import funciones as f
import api as a
import graficas as g


##### LLAMADA API BINANCE #####

#Config API
api_key = cfg.api_key
api_secret = cfg.api_secret
client = Client(api_key, api_secret)
price = client.get_symbol_ticker(symbol="BTCUSDT")

#Parametros para las salidas
tiempo_referencia = 1   # Tamaño de la vela
añopredict = 2024               
horaInicioprincipal = 8  # Hora en la que se inicia la grafica principal a predecir
horaIniciopredict = 20 
horasDePredict = 2  # Tiempo de prediccion
horaFinpredict = horaIniciopredict + horasDePredict # Horario fin de la prediccion

tiempo_init = dt.time(horaInicioprincipal,0,0) #Formato HIPP:00:00
tiempo_current = dt.time(horaIniciopredict,0,0) #Formato HIP:00:00
tiempo_fin_predict = dt.time(horaFinpredict,0,0) #Formato HFP:00:00

#Configuracion de la llamada a la API
asset="BTCUSDT"
start= str(añopredict) + ".07.04" + " " + str(tiempo_init)
end= str(añopredict) + ".07.04" + " " + str(tiempo_current)
startPredict= str(añopredict) + ".07.04"+ " " + str(tiempo_current)
endPredict= str(añopredict) + ".07.04" + " " + str(tiempo_fin_predict)
timeframe= str(tiempo_referencia) + "m"

#Llamada a la API
df, df2 = a.llamada_api(start, end, startPredict, endPredict, timeframe, asset, client)
print(df)
print("--------")
# df_mensual = a.llamada_mensual(client, asset, timeframe)
# print(df_mensual)
# print("--------")

df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
df['EMA100'] = ta.trend.ema_indicator(df['Close'], window=100)
df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200)

# df_mensual['EMA50'] = ta.trend.ema_indicator(df_mensual['Close'], window=50)
# df_mensual['EMA200'] = ta.trend.ema_indicator(df_mensual['Close'], window=200)

#Seteo de los datos de cada intervalo
# data_1m = f.getHistoricalData(asset, Client.KLINE_INTERVAL_1MINUTE, start, end, client)
# data_5m = f.getHistoricalData(asset, Client.KLINE_INTERVAL_5MINUTE, start, end, client)
# data_15m = f.getHistoricalData(asset, Client.KLINE_INTERVAL_15MINUTE, start, end, client)

#GRAFICAS COMPARATIVAS PARA VER COMPOSICION FRACTAL
# g.comparativaFractal(data_1m, data_5m, data_15m)

ultimo_valor = df.iloc[-1]

## DIFERENCIA ENTRE EMMA50 Y EMMA200 ##
u_50 = ultimo_valor['EMA50']
u_200 = ultimo_valor['EMA200']
diff_emma = (u_50 - u_200)/ultimo_valor['Close'] * 100 
print("EMMA50: ", u_50)
print("EMMA200: ", u_200)
print("Diferencia entre EMMA50 y EMMA200: ", diff_emma)
if diff_emma > 1:
    print("Tendencia alcista")
else:
    print("Tendencia bajista")


## CALCULO DE PUNTO DE QUIEBRE ##
punto_quiebre = f.calculoPuntoQuiebre(df)
        
print("Punto de quiebre: ", punto_quiebre)
ultimo_quiebre = punto_quiebre[-1]
diff_tiempo = ultimo_valor.name - ultimo_quiebre.name
print("Diferencia de tiempo: ")
print("--------------------------------")

# Calcular la mitad del tiempo de diff_tiempo
mitad_diff_tiempo = diff_tiempo / 2
# Sumar la mitad del tiempo al último punto de quiebre
nuevo_tiempo = ultimo_quiebre.name + mitad_diff_tiempo

# Obtener el valor de "Close" en el nuevo tiempo
emma_50 = df.loc[nuevo_tiempo]['EMA50']
punto_medio = df.loc[nuevo_tiempo]
diff_emma2 = (punto_medio['EMA50'] - punto_medio['EMA200'])/punto_medio['Close'] * 100
print("Nuevo emma: ", diff_emma2 )

if(diff_emma2 < diff_emma):
    print("Tendencia bajista")
else:
    print("Tendencia alcista")


## CALCULO DE PUNTO DE QUIEBRE GRAL##
# punto_quiebre_gral = f.calculoPuntoQuiebre(df_mensual)
        
# print("Punto de quiebre_gral: ", punto_quiebre_gral)
# diferencias_tiempo = []
# for i in range(1, len(punto_quiebre)):
#     tiempo_anterior = punto_quiebre[i-1].name
#     tiempo_actual = punto_quiebre[i].name
#     diferencia = tiempo_actual - tiempo_anterior
#     diferencias_tiempo.append(diferencia)

# tiempo_promedio_quiebres = sum(diferencias_tiempo, pd.Timedelta(0)) / len(diferencias_tiempo)
# print(f"Tiempo promedio entre quiebres: {tiempo_promedio_quiebres}")



### CALCULO PROBABILIDADES ALC y BAJ ###
probAlcista, probBajista = f.probAlcBaj(df)
### CALCULO DE INTERVALOS DE PRECIO (ruleta)###
intervaloPrecio, indicePrecio = f.probPrecio(df)
    
xtotal = probAlcista + probBajista

probAlcista = probAlcista/xtotal
probBajista = probBajista/xtotal

print("Probabilidad Alcista: ", probAlcista)
print("Probabilidad Bajista: ", probBajista)


# Ajuste de salida para cualquier tiempo de referencia y hora (Sirve para un mismo dia, ajustar para todos los dias parametrizando los mismos) 
muestraRan = 0
horaspredict = horaFinpredict - horaIniciopredict
if horaspredict <= 0:
    horaspredict += 24
muestraRan = 60 * horaspredict // tiempo_referencia


    ### Corridas prediccion ###

# CORRIDA 1
arr_reset = df.reset_index()
arr_reset2 = df2.reset_index()

arr = arr_reset
arr = f.prediccionCorrida(arr, muestraRan, probAlcista, indicePrecio, intervaloPrecio)


# CORRIDA 2
arr3 = arr_reset
arr3 = f.prediccionCorrida(arr3, muestraRan, probAlcista, indicePrecio, intervaloPrecio)
  
# CORRIDA 3
arr4 = arr_reset
arr4 = f.prediccionCorrida(arr4, muestraRan, probAlcista, indicePrecio, intervaloPrecio)

# CORRIDA 4
arr5 = arr_reset
arr5 = f.prediccionCorrida(arr5, muestraRan, probAlcista, indicePrecio, intervaloPrecio)

# CORRIDA 5
arr6 = arr_reset
arr6 = f.prediccionCorrida(arr6, muestraRan, probAlcista, indicePrecio, intervaloPrecio)

# CORRIDA 6
arr7 = arr_reset
arr7 = f.prediccionCorrida(arr7, muestraRan, probAlcista, indicePrecio, intervaloPrecio)


#Tramo real de la moneda que queremos predecir (Para comparar resultados)
arr2 = arr_reset2
long = len(df["Close"].values)-1

## RESULTANTE
# arr_resultante = [(a + b + c + d + e + f)/6 for a, b, c, d, e, f in zip(arr[long:], arr3[long:], arr4[long:], arr5[long:], arr6[long:], arr7[long:])]

coleccion_arrays = [arr, arr3, arr4, arr5, arr6, arr7]

g.comparativaCorridas(arr_reset , coleccion_arrays, arr2, asset, horaInicioprincipal, horaIniciopredict, horaspredict, tiempo_referencia)

#Analisis posterior. 
f.analisisPosterior(df, df2, arr, arr2, arr3, arr4)

## CALCULO DE ERROR RELATIVO EN LAS PREDICCIONES GRAFICADAS    
print("------------------CALCULO DE ERROR RELATIVO------------------")
print("Error relativo (Original): ", f.calcu_error_rela(arr2, arr2), " %")
print("Error relativo (Corrida 1): ", f.calcu_error_rela(arr[long:], arr2), " %")
print("Error relativo (Corrida 2): ", f.calcu_error_rela(arr3[long:], arr2), " %")
print("Error relativo (Corrida 3): ", f.calcu_error_rela(arr4[long:], arr2), " %")
