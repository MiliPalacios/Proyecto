import streamlit as st 
import numpy as np
import pandas as pd
from io import BytesIO
import funciones as f
from pages import pag1,pag2
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font,Color, Alignment,PatternFill,Border
from openpyxl.drawing import image
from PIL import Image

st.sidebar.header("Paginas")
pages={
    "Extra1": pag1,
    "Extra2":pag2
}
selection=st.sidebar.radio("Ir a",list(pages.keys()))
page=pages[selection]
st.title("RESUMEN ESTADO DE CUENTA")
st.write("Esta app fue hecha con el fin de facilitar los procedimientos internos en la tesoreria de un conjunto de residencias")
st.warning("APP AUN DESARROLLANDOSE: no exite contenido en las paginas anexas")
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
    for i in range (len(datos.index)) :
        datos["Fecha"][i]=pd.to_datetime(f.texto_a_fechas(datos["Fecha"][i])) 
    datos=datos.fillna(int("0"))
    st.subheader("La base de datos es:")
    st.write(datos)
    #AGREGAR UN MENU DE OPCIONES
    opciones=['Analisis general',"Analisis por lote",'Analisis por dia',"Reportes en EXCEL","Reportes en PDF",'Filtrar información']
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
    if opcion=='Analisis general':
        #Data frame depurado
        st.subheader('INGRESOS VS FACTURAS')
        st.write('A continuación se presenta una gráfica de los montos facturados y no facturados. Objetivo: dar un vistazo general al movimiento de ADMINISTRACIÓN.')
        #Eliminar valores negativos
        datos_importantes=datos[datos["Tipo de transacción"].isin(["Crédito"])]

        #Eliminar columnas
        datos_importantes=datos_importantes.drop(columns=["Tipo de transacción","Oficina","Concepto","Documento","Saldo","Hora","ORDENANTE","CUENTA ORIGEN","DESCRIPCION BANCO","DETALLE PAGO","BANCO","OBSERVACION","OBSERVACIONES","ESTADO CONTABILIDAD","N. de comprobante"])
       
        #GRAFICO FACTURAS VS INGRESOS
        dias=datos_importantes["Fecha"].unique()
        x = np.arange(len(dias))
        ancho=0.25
        datos_importantes=datos[datos["Tipo de transacción"].isin(["Crédito"])]
        dias=datos_importantes["Fecha"].unique()
        ingresos=[]
        facturado=[]
        for i in range(len(dias)):
            dia=dias[i]
            datos_i=datos_importantes[datos_importantes["Fecha"].isin([dia])].drop(columns=["LOTE","MES","ESTADO CONTABILIDAD","CUENTA ORIGEN","DESCRIPCION BANCO","OBSERVACIONES","OBSERVACION","Tipo de transacción","Oficina","Concepto","Documento","Saldo","DETALLE PAGO","BANCO","N. de comprobante"])
            valores_ingresos_i=datos_i["Monto"].sum()
            valores_facturados_i=datos_i[datos_i["FACTURA"]!=0]["Monto"].sum()
            ingresos.append(valores_ingresos_i)
            facturado.append(valores_facturados_i)

        df=pd.DataFrame({
            "Ingresos" : ingresos,
            "Facturado": facturado,
            })
        st.line_chart(df,color=["#F50404","#002EB1"])
        st.write("En caso de existir inconsistencias, revisar el dataframe a continuación:")
        st.write(datos_importantes)

        st.subheader('INGRESOS VS EGRESOS')
        datos_i_e=datos.loc[:,["Fecha","Tipo de transacción","Monto"]]
        tabla_i_e=datos_i_e.pivot_table(index="Tipo de transacción", values="Monto", aggfunc= lambda x:sum(x))
        st.write(tabla_i_e)
  
    if opcion=='Analisis por dia':
        #Ingresos y egresos por día     
        fechas=datos["Fecha"].unique()
        datos_i_e=datos.loc[:,["Fecha","Tipo de transacción","Monto"]]
       #Ingresos y egresos por día     
        st.subheader('TRANSACCIONES')
        st.info("Seccion en CORRECCION: dias 0")
        st.info("Para ejemplo rápido seleccionar: 2024-01-03")
        fecha=st.selectbox('Seleccione una opción: ', fechas)
        datos_d=datos_i_e[datos_i_e["Fecha"].isin([fecha])]
        tabla_d=datos_d.pivot_table(index="Tipo de transacción",columns="Fecha", values="Monto", aggfunc= lambda x:sum(x))
        st.write("Totales repecto al tipo de transacción")
        st.write(tabla_d)
        st.write("Aquí se presenta el valor de los montos depositados. Objetivo: identificar valores no usuales en las transacciones")
        st.line_chart(datos_d["Monto"],color="#08FF01")    
        
        st.subheader('INGRESOS VS FACTURAS')
        st.write("Aqui usted puede verificar los ingresos que aun no han sido facturados")
        datos_dia=datos[datos["Fecha"].isin([fecha])].drop(columns=["LOTE","MES","ESTADO CONTABILIDAD","CUENTA ORIGEN","DESCRIPCION BANCO","OBSERVACIONES","OBSERVACION","Oficina","Concepto","Documento","Saldo","DETALLE PAGO","BANCO","N. de comprobante"])
        datos_dia=datos_dia[datos_dia["Tipo de transacción"].isin(["Crédito"])]
        st.write(datos_dia)
        valores_ingresos_d=datos_dia["Monto"].sum()
        valores_facturados_d=datos_dia[datos_dia["FACTURA"]!=0]["Monto"].sum()
        y2=[valores_ingresos_d,valores_facturados_d]
        x2=[1,2]
        plt.figure(figsize=(10, 6))
        plt.title(f"CONTROL DEL REGISTRO DE INGRESOS DIA {fecha}")
        barras2=plt.bar(x2,y2,width=0.8,edgecolor="k",color=["g","b"])
        plt.ylabel('USD')
        plt.xticks([1,2],["INGRESO","MONTO FACTURADO"])
        for barra in barras2:
            altura = barra.get_height()
            plt.text(barra.get_x()+barra.get_width()/2, altura/2, altura, ha = 'center',va="bottom")
        plt.savefig('images/i_vs_f_dia.png')
        image=Image.open('./images/i_vs_f_dia.png')
        st.image(image,caption="Objetivo: dar un vistazo más cercano a las actualizaciones de ADMINISTRACIÓN.")
    if opcion=="Analisis por lote":
        datos["LOTE"]=datos["LOTE"].apply(f.lotes_sin_nombre)
        datos=datos.sort_values(by=["LOTE"])
        lotes=datos["LOTE"].unique()
        lote=st.selectbox("Escoja el lote:", lotes)
        #REPORTE POR LOTE
    if opcion=="Reportes en EXCEL":
        st.title("Reportes en EXCEL")
        st.write("Aquí usted podrá descargar los reportes generados en base a los pagos de cada lote")
        st.info("ERROR: datos de tipo tiempo no se pueden convertir a Excel :/ Se descargan las fechas sin el formato #/#/#")

        datos["LOTE"]=datos["LOTE"].apply(f.lotes_sin_nombre)
        datos=datos.sort_values(by=["LOTE"])
        lotes=list(datos["LOTE"].unique())
        lote=st.selectbox("Escoja el lote:", lotes)

        wb=Workbook()
        ws=wb.active
        ws["E1"]=f"REPORTE DEL LOTE {lote}"
        ws['E1'].font = Font(name='Amercian Typewriter',size=20,bold=True,italic=True,color='139911')
        ws.row_dimensions[1].height = 30
        ws['E1'].alignment = Alignment(horizontal='center',vertical='center')

        datos_lote=datos[datos["LOTE"].isin([lote])].drop(columns=["LOTE","MES","ESTADO CONTABILIDAD","CUENTA ORIGEN","DESCRIPCION BANCO","OBSERVACIONES","OBSERVACION","Tipo de transacción","Oficina","Concepto","Documento","Saldo","DETALLE PAGO","BANCO","N. de comprobante"])

        list=["B","C","D","E","F","G","H"]
        for j in range (len(list)):
            ws.column_dimensions[f'{list[j]}'].width=20
            ws[f"{list[j]}4"]=datos_lote.columns[j]
            ws[f"{list[j]}4"].font = Font(name='Times',size=12,bold=True,italic=False,color='243783')
            ws[f"{list[j]}4"].alignment = Alignment(horizontal='center',vertical='center')

        aux=0
        for i in range (5,5+len(datos_lote.index)):
            ws[f"B{i}"]=datos_lote["Fecha"].values[aux]
            ws[f"B{i}"].alignment = Alignment(horizontal='center',vertical='center')
            ws[f"C{i}"]=datos_lote["Hora"].values[aux]
            ws[f"C{i}"].alignment = Alignment(horizontal='center',vertical='center')
            ws[f"D{i}"]=datos_lote["Monto"].values[aux]
            ws[f"D{i}"].alignment = Alignment(horizontal='center',vertical='center')
            ws[f"E{i}"]=datos_lote["ORDENANTE"].values[aux]
            ws[f"E{i}"].alignment = Alignment(horizontal='center',vertical='center')
            ws[f"F{i}"]=datos_lote["FACTURA"].values[aux]
            ws[f"F{i}"].alignment = Alignment(horizontal='center',vertical='center')
            ws[f"G{i}"]=datos_lote["FECHA FACTURA"].values[aux]
            ws[f"G{i}"].alignment = Alignment(horizontal='center',vertical='center')
            ws[f"H{i}"]=datos_lote["MOTIVO"].values[aux]
            ws[f"H{i}"].alignment = Alignment(horizontal='center',vertical='center')
            aux+=1
        #DESCARGAR EL EXCEL
        excel_file=f.descargar_excel(wb)
        st.download_button(label="Descargar Excel",data=excel_file,file_name=f"Reporte_lote_{lote}.xlsx")

       


    #Agregar imagenes
    #img = Image("images/donut_chart_platform.png")
    #ws.add_image(img,"A4")
    #Guardar
    #poner graficos en excel
    #fig=px.histogram(datos,x=pregunta)

    if opcion=="Reportes en PDF":
        print ("En desarrollo")