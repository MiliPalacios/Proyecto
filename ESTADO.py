import streamlit as st 
import numpy as np
import pandas as pd
from io import BytesIO
import funciones as f
from pages import pag1,pag2
from openpyxl import Workbook
from openpyxl.styles import Font,Color, Alignment,PatternFill,Border
from openpyxl.drawing import image

st.sidebar.header("Paginas")
pages={
    "PDF": pag1,
    "EXCEL":pag2
}
selection=st.sidebar.radio("Ir a",list(pages.keys()))
page=pages[selection]
st.title("RESUMEN ESTADO DE CUENTA")
st.write("Aquí podrá encontrar varias herramientas para dar un vistazo más detallado a la información dada")

# Subir base desde el computador
try:
    archivo_base = st.file_uploader('Subir base de datos',type=['xlsx'])
except:
    st.warning("Se debe subir un archivo de EXCEL",icon="🔴")
    
if archivo_base is not None:
    st.success("Archivo subido correctamente",icon="✅")
    # Lectura de la base
    datos = pd.read_excel(archivo_base)    
    #Transformar datos de fecha a datos de tiempo
    for i in range (len(list(datos.index))) :
        datos["Fecha"][i]=pd.to_datetime(f.texto_a_fechas(datos["Fecha"][i])) 

    st.subheader("La base de datos es:")
    st.write(datos)
    #AGREGAR UN MENU DE OPCIONES
    opciones=['Filtrar información','Solo créditos','Ingresos y egresos tototales','Ingresos y egresos por dia',"Reportes en EXCEL","Reportes en PDF"]
    opcion = st.selectbox('¿Qué deseas hacer?',opciones)
    if opcion=='Filtrar información':
        #FILTRAR INFORMACION POR CLASES EN COLUMNAS
        st.subheader('Filtrar información')
        columnas=list(datos.columns)
        columna = st.selectbox('Selecciona una opción',columnas)
        valores=datos[columna].unique()
        valor = st.selectbox('Selecciona una opción',valores)
        datos_f=datos[datos[columna]==valor]
        st.write(datos_f)
    if opcion=='Solo créditos':
        #Data frame depurado
        st.subheader('Solo créditos')
        st.write('Esta sección permite observar los ingresos facturados y no facturados')
        st.info("Seccion en CORRECCION")
        #Eliminar columnas
        datos_importantes=datos.drop(columns=["Tipo de transacción","Oficina","Concepto","Documento","Saldo","Hora","ORDENANTE","CUENTA ORIGEN","DESCRIPCION BANCO","DETALLE PAGO","BANCO","OBSERVACION","OBSERVACIONES","ESTADO CONTABILIDAD","N. de comprobante","Unnamed: 9"])

        #Eliminar valores negativos
        v_negativos=[]
        for monto in datos_importantes["Monto"]:
            if monto<0:
                indice=list(datos_importantes["Monto"]).index(monto)
                v_negativos.append(indice)
        datos_importantes=datos_importantes.drop(index=v_negativos)
        st.write(datos_importantes)
    if opcion=='Ingresos y egresos tototales':
        #Ingresos y egresos totales
        st.subheader('Ingresos y egresos tototales')
        st.write("Referente a TODA la data del archivo")
        datos_i_e=datos.loc[:,["Fecha","Tipo de transacción","Monto"]]
        tabla_i_e=datos_i_e.pivot_table(index="Tipo de transacción", values="Monto", aggfunc= lambda x:sum(x))
        st.write(tabla_i_e)

    if opcion=='Ingresos y egresos por dia':
        #Ingresos y egresos por día     
        fechas=datos["Fecha"].unique()
        datos_i_e=datos.loc[:,["Fecha","Tipo de transacción","Monto"]]
       #Ingresos y egresos por día     
        st.subheader('Ingresos y egresos por dia')
        st.info("Seccion en CORRECCION")
        fecha=st.selectbox('Selecciona: ', fechas)
        datos_d=datos_i_e[datos_i_e["Fecha"].isin([fecha])]
        tabla_d=datos_d.pivot_table(index="Tipo de transacción",columns="Fecha", values="Monto", aggfunc= lambda x:sum(x))
        st.write(tabla_d)
        st.write("Aquí se presenta el valor de los montos depositados por cada transacción")
        st.line_chart(datos_d["Monto"])
    if opcion=="Reportes en EXCEL":
        st.title("Reportes en EXCEL")
        st.write("Aquí usted podrá descargar los reportes generados en base a los pagos de cada lote")
        datos["LOTE"]=datos["LOTE"].apply(f.lotes_sin_nombre)
        datos=datos.sort_values(by=["LOTE"])
        lotes=datos["LOTE"].unique()
        lote=st.selectbox("Escoja el lote:", lotes)
       
    #poner graficos en excel
     #fig=px.histogram(datos,x=pregunta)

    #DESCARGAR EL EXCEL
        #excel_file=f.to_excel(df)
        #st.download_button(
        #label="Descargar Excel",
        #data=excel_file,
        #file_name=f"respuestas_por_genero_{preguntap}_{pregunta}.xlsx",icon="⬇️")
