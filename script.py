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
 

##### LLAMADA API BINANCE  #####

#Config API
api_key = cfg.api_key
api_secret = cfg.api_secret
client = Client(api_key, api_secret)
price = client.get_symbol_ticker(symbol="BTCUSDT")

#Parametros para las salidas
tiempo_referencia = 1   # Tamaño de la vela
añopredict = 2024               
horaInicioprincipal = 4  # Hora en la que se inicia la grafica principal a predecir
horaIniciopredict = 20 
horasDePredict = 1  # Tiempo de prediccion
horaFinpredict = horaIniciopredict + horasDePredict # Horario fin de la prediccion
diaPredict = "02"
mesPredict = "07"

tiempo_init = dt.time(horaInicioprincipal,0,0) #Formato HIPP:00:00
tiempo_current = dt.time(horaIniciopredict,0,0) #Formato HIP:00:00
tiempo_fin_predict = dt.time(horaFinpredict,0,0) #Formato HFP:00:00

#Configuracion de la llamada a la API
asset="BTCUSDT"
<<<<<<< HEAD
start= str(añopredict) + ".04.10" + " " + str(tiempo_init)
end= str(añopredict) + ".04.10" + " " + str(tiempo_current)
startPredict= str(añopredict) + ".04.10"+ " " + str(tiempo_current)
endPredict= str(añopredict) + ".04.10" + " " + str(tiempo_fin_predict)
=======
start= str(añopredict) + "." + mesPredict + "." + diaPredict + " " + str(tiempo_init)
end= str(añopredict) + "." + mesPredict + "." + diaPredict + " " + str(tiempo_current)
startPredict= str(añopredict) + "." + mesPredict + "." + diaPredict + " " + str(tiempo_current)
endPredict= str(añopredict) + "." + mesPredict + "." + diaPredict + " " + str(tiempo_fin_predict)
>>>>>>> 7c9d772d5f931cf5d52126423f0df5787cd08b1f
timeframe= str(tiempo_referencia) + "m"

#Llamada a la API
df, df2 = a.llamada_api(start, end, startPredict, endPredict, timeframe, asset, client)
print(df)
print("--------")

df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200)


#GRAFICAS COMPARATIVAS PARA VER COMPOSICION FRACTAL

ultimo_valor = df.iloc[-1]

tiempo_estimado_quiebre = dt.time(1,52,0)
tiempo_estimado_quiebre = pd.Timedelta(hours=tiempo_estimado_quiebre.hour, minutes=tiempo_estimado_quiebre.minute)

## DIFERENCIA ENTRE EMMA50 Y EMMA200 ##
u_50 = ultimo_valor['EMA50']
u_200 = ultimo_valor['EMA200']
diff_emma = (u_50 - u_200)/ultimo_valor['Close'] * 100 



# Calcula las pendientes
df['Pendiente_EMA50'] = df['EMA50'].diff()
df['Pendiente_EMA200'] = df['EMA200'].diff()



# Señal de cruce próximo si ambas pendientes convergen hacia el mismo punto
df['Cruce Próximo'] = ((df['Pendiente_EMA50'] > 0) & (df['Pendiente_EMA200'] < 0)) | ((df['Pendiente_EMA50'] < 0) & (df['Pendiente_EMA200'] > 0))


tendencia_alcista = False
if diff_emma >= 0:
    print("Tendencia alcista")
    tendencia_alcista = True
else:
    print("Tendencia bajista")
    tendencia_alcista = False


intervaloPrecio, indicePrecio = f.probPrecio(df)


if(df['Cruce Próximo'].iloc[-1]):
    print("Cruce próximo")
    tendencia_alcista = not tendencia_alcista

if(tendencia_alcista):
    probAlcista = 55
    probBajista = 45
else:
    probAlcista = 45
    probBajista = 55

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
arr, grafica200, grafica50 = f.prediccionCorrida(arr, muestraRan, probAlcista, probBajista,indicePrecio, intervaloPrecio)


# CORRIDA 2
arr3 = arr_reset
arr3, grafica200, grafica50  = f.prediccionCorrida(arr3, muestraRan, probAlcista,probBajista, indicePrecio, intervaloPrecio)
  
# CORRIDA 3
arr4 = arr_reset
arr4, grafica200, grafica50 = f.prediccionCorrida(arr4, muestraRan, probAlcista,probBajista, indicePrecio, intervaloPrecio)

# CORRIDA 4
arr5 = arr_reset
arr5, grafica200, grafica50 = f.prediccionCorrida(arr5, muestraRan, probAlcista,probBajista, indicePrecio, intervaloPrecio)

# CORRIDA 5
arr6 = arr_reset
arr6, grafica200, grafica50 = f.prediccionCorrida(arr6, muestraRan, probAlcista,probBajista, indicePrecio, intervaloPrecio)

# CORRIDA 6
arr7 = arr_reset
arr7, grafica200, grafica50 = f.prediccionCorrida(arr7, muestraRan, probAlcista,probBajista, indicePrecio, intervaloPrecio)


#Coleccion de corridas
Corridas = [arr,arr3, arr4, arr5, arr6, arr7]

#Tramo real de la moneda que queremos predecir (Para comparar resultados)
arr2 = arr_reset2
long = len(df["Close"].values)-1


#Busqueda de mejor y peor
# mejorCorrida = f.mejorResultado(Corridas, arr2)
# peorCorrida = f.peorResultado(Corridas, arr2)

# coleccion_arrays = [mejorCorrida, peorCorrida]

print("arr recortado", arr[long:])

## RESULTANTE
arr_resultante = pd.DataFrame({'Date': arr[long:]['Date']})
arr_resultante['Close'] = [(a + b + c + d + e + f)/6 for a, b, c, d, e, f in zip(arr[long:]['Close'], arr3[long:]['Close'], arr4[long:]['Close'], arr5[long:]['Close'], arr6[long:]['Close'], arr7[long:]['Close'])]


g.comparativaCorridas(arr_reset , Corridas, arr2, asset, horaInicioprincipal, horaIniciopredict, horaspredict, tiempo_referencia, grafica200, grafica50, arr_resultante)


## CALCULO DE ERROR RELATIVO EN LAS PREDICCIONES GRAFICADAS    
print("------------------CALCULO DE ERROR RELATIVO------------------")
print("Error relativo (Original): ", f.calcu_error_rela(arr2, arr2), " %")
print("Error relativo (Corrida 1): ", f.calcu_error_rela(arr[long:], arr2), " %")
print("Error relativo (Corrida 2): ", f.calcu_error_rela(arr3[long:], arr2), " %")
print("Error relativo (Corrida 3): ", f.calcu_error_rela(arr4[long:], arr2), " %")
