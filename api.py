import pandas as pd
import graficas as g

def llamada_api(start, end, startPredict, endPredict, timeframe, asset, client):

    # data = client.get_historical_klines(asset, timeframe, start, end)
    df= pd.DataFrame(client.get_historical_klines(asset, timeframe, start, end))
    df=df.iloc[:,:6]
    df.columns=["Date","Open","High","Low","Close","Volume"]
    df=df.set_index("Date")
    df.index=pd.to_datetime(df.index,unit="ms")
    df=df.astype("float")

    # data = client.get_historical_klines(asset, timeframe, startPredict, endPredict)
    df2= pd.DataFrame(client.get_historical_klines(asset, timeframe, startPredict, endPredict))
    df2=df2.iloc[:,:6]
    df2.columns=["Date","Open","High","Low","Close","Volume"]
    df2=df2.set_index("Date")
    df2.index=pd.to_datetime(df2.index,unit="ms")
    df2=df2.astype("float")

    #GRAFICO DE VELAS INICIO
    g.velas(df, asset)

    return df, df2

def llamada_mensual(client, asset, timeframe ): # 60 dias
    df= pd.DataFrame(client.get_historical_klines(asset, timeframe, "2024.06.20", "2024.08.20"))
    df=df.iloc[:,:6]
    df.columns=["Date","Open","High","Low","Close","Volume"]
    df=df.set_index("Date")
    df.index=pd.to_datetime(df.index,unit="ms")
    df=df.astype("float")

    return df
