import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visor de Perforación", layout="wide")

st.title("🛠️ Visor de Datos de Perforación")

# --- CARGA DE EXCEL ---
archivo = st.sidebar.file_uploader("📁 Cargar archivo Excel", type=["xlsx"])

if archivo:
    excel_file = pd.ExcelFile(archivo)
    hojas_disponibles = excel_file.sheet_names

    st.sidebar.header("📄 Selección de Hoja")

    # Selector de hoja
    hoja_seleccionada = st.sidebar.selectbox("Selecciona una hoja", hojas_disponibles)

    # Campo opcional para escribir manualmente la hoja
    hoja_manual = st.sidebar.text_input("O escribe el nombre exacto de la hoja", value=hoja_seleccionada)

    hoja_final = hoja_manual if hoja_manual in hojas_disponibles else hoja_seleccionada

    @st.cache_data
    def cargar_datos(nombre_hoja):
        return pd.read_excel(
            archivo,
            sheet_name=nombre_hoja,
            engine="openpyxl",
            skiprows=12,
            usecols="B:BS"
        )

    try:
        df = cargar_datos(hoja_final)
        df.columns = df.columns.str.strip()
        st.sidebar.success(f"✅ Hoja '{hoja_final}' cargada")
    except:
        st.error(f"❌ No se pudo cargar la hoja '{hoja_final}'")
        st.stop()

    # --- FILTROS ---
    st.sidebar.header("🎛️ Filtros")
    if "Mes Logueo" in df:
        df["Mes Logueo"] = pd.to_datetime(df["Mes Logueo"], errors="coerce").dt.strftime("%B")

    def filtro_opcional(columna):
        opciones = df[columna].dropna().astype(str).unique().tolist()
        opciones.sort()
        opciones.insert(0, "⛔ Vacío")
        return st.sidebar.multiselect(f"{columna}", opciones, default=opciones)

    def filtro_multiple(columna):
        return st.sidebar.multiselect(columna, sorted(df[columna].dropna().unique()), default=None)

    # Filtros estándar
    año = filtro_multiple("AÑO") if "AÑO" in df else []
    ubicacion = filtro_multiple("UBICACIÓN") if "UBICACIÓN" in df else []
    categoria = filtro_multiple("CATEGORIA") if "CATEGORIA" in df else []
    logueado_por = filtro_multiple("LOGUEADO POR") if "LOGUEADO POR" in df else []
    mes_logueo = filtro_multiple("Mes Logueo") if "Mes Logueo" in df else []

    # Filtros opcionales
    logueo = filtro_opcional("LOGUEO") if "LOGUEO" in df else []
    imago = filtro_opcional("IMAGO") if "IMAGO" in df else []
    corte = filtro_opcional("Corte") if "Corte" in df else []
    muestreo = filtro_opcional("Muestreo") if "Muestreo" in df else []

    def aplicar_filtros(df):
        if año: df = df[df["AÑO"].isin(año)]
        if ubicacion: df = df[df["UBICACIÓN"].isin(ubicacion)]
        if categoria: df = df[df["CATEGORIA"].isin(categoria)]
        if logueado_por: df = df[df["LOGUEADO POR"].isin(logueado_por)]
        if mes_logueo: df = df[df["Mes Logueo"].isin(mes_logueo)]

        for col, val in zip(
            ["LOGUEO", "IMAGO", "Corte", "Muestreo"],
            [logueo, imago, corte, muestreo]
        ):
            if col in df.columns and val:
                incluye_vacio = "⛔ Vacío" in val
                valores = [v for v in val if v != "⛔ Vacío"]
                if incluye_vacio:
                    df = df[df[col].isna() | df[col].astype(str).isin(valores)]
                else:
                    df = df[df[col].astype(str).isin(valores)]
        return df

    df_filtrado = aplicar_filtros(df)

    # --- MINI DASHBOARD / RESUMEN GENERAL ---
    st.subheader("📊 Resumen General")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total registros", len(df_filtrado))
    col2.metric("Prom. recuperación (%)", round(df_filtrado["Recuperacion (%)"].mean(), 2) if "Recuperacion (%)" in df_filtrado else "N/A")
    if "Recuperacion (%)" in df_filtrado.columns:
        col3.metric("Con recuperación < 85%", df_filtrado[df_filtrado["Recuperacion (%)"] < 85].shape[0])
    else:
        col3.metric("Con recuperación < 85%", "Columna no encontrada")

    col4.metric("Ubicaciones únicas", df_filtrado["UBICACIÓN"].nunique() if "UBICACIÓN" in df_filtrado else "N/A")

    # --- SELECCIÓN DE COLUMNAS ---
    st.sidebar.header("📋 Columnas a mostrar")
    columnas_importantes = ["SONDAJE", "UBICACIÓN", "MAQUINA", "OBJETIVO", 
                            "Metros Perforados", "Recuperacion (%)", 
                            "Inicio Perforación", "Fin perforación", 
                            "FECHA ENVIO", "LABORATORIO"]

    columnas_opcionales = st.sidebar.multiselect(
        "Selecciona columnas adicionales", df.columns.tolist(), default=[]
    )
    modo = st.sidebar.radio("¿Cómo mostrar las columnas?", ["Agregar", "Reemplazar"])

    if modo == "Reemplazar":
        columnas_mostrar = columnas_opcionales or columnas_importantes
    else:
        columnas_mostrar = list(dict.fromkeys(columnas_importantes + columnas_opcionales))

    # --- ALERTA POR BAJA RECUPERACIÓN ---
    if "Recuperacion (%)" in df_filtrado.columns and (df_filtrado["Recuperacion (%)"] < 85).any():
        st.warning("⚠️ Hay registros con recuperación menor al 85%")

    # --- MOSTRAR TABLA ---
    st.subheader("📑 Datos Filtrados")
    st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True)

else:
    st.info("📤 Por favor, sube un archivo Excel para comenzar.")
