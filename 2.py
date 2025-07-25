import streamlit as st
import pandas as pd

st.set_page_config(page_title="App de Perforación", layout="wide")

st.title("⛏️ Análisis de Perforación por SONDAJE")

# Cargar archivo Excel
archivo = st.file_uploader("📤 Cargar archivo Excel", type=["xlsx"])

if archivo:
    def cargar_datos(nombre_hoja):
        return pd.read_excel(archivo, sheet_name=nombre_hoja, engine="openpyxl", skiprows=12)

    nombre_hoja = "2025 GNRL"
    df = cargar_datos(nombre_hoja)
    df.dropna(how="all", inplace=True)
    df.columns = df.columns.astype(str).str.strip()

    if "SONDAJE" not in df.columns:
        st.error("❌ La columna 'SONDAJE' no fue encontrada en el archivo.")
    else:
        st.markdown("### 🔍 Buscar Información por Número de Sondaje")
        sondaje_input = st.text_input("Ingresa el número de SONDAJE", placeholder="Ejemplo: SDJ-12345")

        if sondaje_input:
            df_filtrado = df[df["SONDAJE"].astype(str).str.strip() == sondaje_input.strip()]

            if df_filtrado.empty:
                st.warning("⚠️ No se encontró información para ese SONDAJE.")
            else:
                st.success(f"📌 Resultados para SONDAJE: `{sondaje_input}`")

                # Selección de columnas
                columnas_disponibles = list(df_filtrado.columns)
                columnas_seleccionadas = st.multiselect(
                    "🧩 Selecciona las columnas que deseas visualizar",
                    columnas_disponibles,
                    default=["SONDAJE", "FECHA", "UBICACION", "RECUPERACION"] if "RECUPERACION" in df.columns else columnas_disponibles[:5]
                )

                # Estilo de presentación
                st.markdown("### 📋 Datos del SONDAJE")
                st.dataframe(df_filtrado[columnas_seleccionadas], use_container_width=True, hide_index=True)

                # Resumen general (si hay datos numéricos)
                columnas_numericas = df_filtrado.select_dtypes(include="number").columns
                if not columnas_numericas.empty:
                    st.markdown("### 📊 Resumen Estadístico")
                    resumen = df_filtrado[columnas_numericas].describe().transpose()
                    resumen["mediana"] = df_filtrado[columnas_numericas].median()
                    st.dataframe(resumen, use_container_width=True)

