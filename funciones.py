import streamlit as st 
import pandas as pd
import numpy as np
from io import BytesIO

#Convertir a excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

#Texto "24 ENE 2024" a dato de tipo tiempo 
def texto_a_fechas(text):
    try:
        pd.to_datetime(text)
        result=text
    except:
        text=list(text)
        text=list(filter(lambda x: x!=" ",text))
        d=text[0:2]
        d1=d[0]
        d2=d[1]
        y=text[5:]
        y1=y[0]
        y2=y[1]
        y3=y[2]
        y4=y[3]
        month_words=text[2:5]
        m1=month_words[0]
        m2=month_words[1]
        m3=month_words[2]
        month_words=str(f"{m1}{m2}{m3}")

        meses=["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
        for mes in meses:
            if month_words==mes:
                m=meses.index(mes)+1
        result=f"{d1}{d2}-{m}-{y1}{y2}{y3}{y4}"
        try:
            pd.to_datetime(result)
        except:
            result="Revisar fechas o Abreviaciones en Python"
    return result

#Eliminar lotes sin dueño identificado
def lotes_sin_nombre(texto):
    try:
        texto=float(texto)
    except:
        texto=float(0)
    return texto