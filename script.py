from binance import Client
import datetime as dt
import config as cfg
import numpy as np
from random import *

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
start= str(añopredict) + ".08.10" + " " + str(tiempo_init)
end= str(añopredict) + ".08.10" + " " + str(tiempo_current)
startPredict= str(añopredict) + ".08.10"+ " " + str(tiempo_current)
endPredict= str(añopredict) + ".08.10" + " " + str(tiempo_fin_predict)
timeframe= str(tiempo_referencia) + "m"

#Llamada a la API
df, df2 = a.llamada_api(start, end, startPredict, endPredict, timeframe, asset, client)
print(df)
print("--------")


#Seteo de los datos de cada intervalo
data_1m = f.getHistoricalData(asset, Client.KLINE_INTERVAL_1MINUTE, start, end, client)
data_5m = f.getHistoricalData(asset, Client.KLINE_INTERVAL_5MINUTE, start, end, client)
data_15m = f.getHistoricalData(asset, Client.KLINE_INTERVAL_15MINUTE, start, end, client)

#GRAFICAS COMPARATIVAS PARA VER COMPOSICION FRACTAL
g.comparativaFractal(data_1m, data_5m, data_15m)


# #Podemos hacer este calculo de dimension fractal para ver como difieren en el valor final segun el intervalo. Serviria para la parte teorica un poco
# dim_5m = fractal_dimension(data_5m["Close"].values, 10)
# dim_1h = fractal_dimension(data_1h["Close"].values, 10)

# print(f"Dimension fractal (5 minutos): {dim_5m}")
# print(f"Dimension fractal (1 hora): {dim_1h}")

# #Comparar las dimensiones fractales
# diff = dim_5m - dim_1h

# print(f"Diferencia de dimensiones fractales: {diff}")


### CALCULO PROBABILIDADES ALC y BAJ ###
probAlcista, probBajista = f.probAlcBaj(df)
### CALCULO DE INTERVALOS DE VOLUMEN (ruleta) ###
intervaloVolumen, indiceVolumen = f.probVolumen(df)
### CALCULO DE INTERVALOS DE PRECIO (ruleta)###
intervaloPrecio, indicePrecio = f.probPrecio(df)
    
xtotal = probAlcista + probBajista

probAlcista = probAlcista/xtotal
probBajista = probBajista/xtotal

print("Probabilidad Alcista: ", probAlcista)
print("Probabilidad Bajista: ", probBajista)
# print(f"Diferencia de dimensiones fractales: {diff}")


# Ajuste de salida para cualquier tiempo de referencia y hora (Sirve para un mismo dia, ajustar para todos los dias parametrizando los mismos) 
muestraRan = 0
horaspredict = horaFinpredict - horaIniciopredict
if horaspredict <= 0:
    horaspredict += 24
muestraRan = 60 * horaspredict // tiempo_referencia

    ### Corridas prediccion ###

# CORRIDA 1
arr = df["Close"].values.tolist()
# Calcular el exponente de Hurst para la serie de precios
H = f.hurst_exponent(np.array(arr))
print(f"El exponente de Hurst es: {H}")
arr = f.prediccionCorrida(arr, muestraRan, probAlcista, indicePrecio, intervaloPrecio)

# CORRIDA 2
arr3 = df["Close"].values.tolist()
arr3 = f.prediccionCorrida(arr3, muestraRan, probAlcista, indicePrecio, intervaloPrecio)
  
# CORRIDA 3
arr4 = df["Close"].values.tolist()
arr4 = f.prediccionCorrida(arr4, muestraRan, probAlcista, indicePrecio, intervaloPrecio)


#Tramo real de la moneda que queremos predecir (Para comparar resultados)
arr2 = df2["Close"].values.tolist()
long = len(df["Close"].values)-1

g.comparativaCorridas(arr, arr2, arr3, arr4, asset, horaInicioprincipal, horaIniciopredict, horaspredict, tiempo_referencia, long)

#Analisis posterior. 
f.analisisPosterior(df, df2, arr, arr2, arr3, arr4)

## CALCULO DE ERROR RELATIVO EN LAS PREDICCIONES GRAFICADAS    
print("------------------CALCULO DE ERROR RELATIVO------------------")
print("Error relativo (Original): ", f.calcu_error_rela(arr2, arr2), " %")
print("Error relativo (Corrida 1): ", f.calcu_error_rela(arr[long:], arr2), " %")
print("Error relativo (Corrida 2): ", f.calcu_error_rela(arr3[long:], arr2), " %")
print("Error relativo (Corrida 3): ", f.calcu_error_rela(arr4[long:], arr2), " %")
