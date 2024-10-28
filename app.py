import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from functions import get_etf_data, get_multietf_data, get_stat_string

st.title("Info ETF")

# Lista de ETFs
etfs = [
    'FXI',      # AZ China
    'EWT',      # AZ MSCI TAIWAN INDEX FD
    'IWM',      # AZ RUSSELL 2000
    'EWZ',      # AZ Brasil
    'EWU',      # AZ MSCI UNITED KINGDOM
    'IYF',      # AZ DJ US FINANCIAL SECT
    'BKF',      # AZ BRIC
    'EWY',      # AZ MSCI SOUTH KOREA IND
    'AGG',      # AZ BARCLAYS AGGREGATE
    'EEM',      # AZ Mercados Emergentes
    'EZU',      # AZ MSCI EMU
    'FXI',      # AZ FTSE/XINHUA CHINA 25
    'GLD',      # AZ Oro
  #  'QQQ',      # AZ QQQ NASDAQ 100
    'AAXJ',     # AZ MSCI ASIA EX-JAPAN
    'SHY',      # AZ BARCLAYS 1-3 YEAR TR
    'ACWI',     # AZ MSCI ACWI INDEX FUND
    'SLV',      # AZ SILVER TRUST
    'EWH',      # AZ MSCI HONG KONG INDEX
    'SPY',      # AZ SPDR S&P 500 ETF TRUST
    'EWJ',      # AZ MSCI JAPAN INDEX FD
    'IEGL',     # AZ BG EUR GOVT BOND 1-3
    'DIA',      # AZ SPDR DJIA TRUST
    'EWQ',      # AZ MSCI FRANCE INDEX FD
    'XOP',      # AZ DJ US OIL & GAS EXPL
    'VWO',      # AZ VANGUARD EMERGING MARKET ETF
    'EWA',      # AZ MSCI AUSTRALIA INDEX
    'XLF',      # AZ FINANCIAL SELECT SECTOR SPDR
    'EWC',      # AZ MSCI CANADA
    'ILF',      # AZ S&P LATIN AMERICA 40
    'XLV',      # AZ HEALTH CARE SELECT SECTOR
    'EWG',      # AZ MSCI GERMANY INDEX
    'ITB'       # AZ DJ US HOME CONSTRUCT
]

# Barra de búsqueda para el Multiselect
selected_etf = st.selectbox('Selecciona un ETF:', etfs)
comparison_etfs = etfs.copy()
comparison_etfs.remove(selected_etf)
# Obtener datos del ETF seleccionado
info = get_etf_data(selected_etf)

# Mostrar información básica
st.subheader(f"{info['longName']} ({info['symbol']})")

st.write(f"Category: {info.get('category', 'NA')} / {info['quoteType']}")
st.write(f"Description: {info.get('longBusinessSummary', '*Not available.*')}")


# Mostrar datos financieros clave
st.subheader("Key Financial Data")
col1, col2, col3 = st.columns(3)
with col1:
    previousClose = get_stat_string('previousClose', '$', info)
    open = get_stat_string('open', '$', info)
    volume = get_stat_string('volume', 'M', info)
    averageVolume = get_stat_string('averageVolume', 'M', info)

    col1.metric('Previous close', value=previousClose)
    col1.metric('Open', value=open)
    col1.metric('Volume (M)', value=volume)
    col1.metric('Average Vol (M)', value=averageVolume)
with col2:
    open = info.get('open', False)
    volume = info.get('volume', False)
    if open and volume: 
        market_cap = open * volume / 1000000
        col2.metric('Market Cap (M)', value=f'${market_cap:,.0f}')
    else:
        col2.metric('Market Cap (M)', value='NA')

    beta3Year = get_stat_string('beta3Year', 'f', info)
    trailingPE = get_stat_string('trailingPE', 'f', info)
    trailingAnnualDividendYield = get_stat_string('trailingAnnualDividendYield', '%', info)
    
    col2.metric('Beta (3Y)', value=beta3Year)
    col2.metric('Trailing PE', value=trailingPE)
    col2.metric('Annual Dividend Yield', value=trailingAnnualDividendYield)

with col3:
    ytdReturn = get_stat_string('ytdReturn', '%', info)
    threeYearAverageReturn = get_stat_string('threeYearAverageReturn', '%', info)
    fiveYearAverageReturn = get_stat_string('fiveYearAverageReturn', '%', info)

    col3.metric('YTD Return', value=ytdReturn)
    col3.metric('3YR Avg. Return', value=threeYearAverageReturn)
    col3.metric('5YR Avg. Return', value=fiveYearAverageReturn)

# Gráfico de precios
st.subheader("Price chart (historical)")

#Multiselect para comparar con otros ETFs
selected_comparison_etfs = st.multiselect("Select comparison ticker", options=comparison_etfs)

#lista para representar los múltiples ETFs seleccionados
all_selected_etfs = [selected_etf] + selected_comparison_etfs

history = get_multietf_data(all_selected_etfs)['Adj Close']


#Filtro con periodos de tiempo
#Espacio para dos columnas, considerando espacio que toma cada columna

col1, col2 = st.columns([1, 7])
with col1:
    range_choice = st.radio( #Boton de rangos - revisar doc. streamlit
        "**Range**", #titulo
        ["All","5Y","2Y","1Y","6M","3M","5D",] #lista con valores posibles

    )

    #diccionario con los valores de cada opción del rango / usando pandas Date Offsets

t_offsets = {
    "All": False,  #no se puede years = 0 o days = 0, no se puede definir de 0 y falla al momento de restar el filtro
    "5Y": pd.DateOffset(years=5),
    "2Y": pd.DateOffset(years=2),
    "1Y": pd.DateOffset(years=1),
    "6M": pd.DateOffset(months=6),
    "3M": pd.DateOffset(months=3),
    "5D": pd.DateOffset(days=5),
}



#Marca error porque las zonas horarias son diferentes de aquí a NY
#Hacer que las zonas horarias sean ambas de NY

tz=history.index.tz
now = pd.Timestamp.now(tz=tz) #El tipo de valor individual de history.index[0] es Timestamp

offset = t_offsets[range_choice] #ligar los valores del rango que selecciono con el diccionario

#para que salga el "all" se dene usar un if 
if offset:
     filtered_data = history[history.index >= now - offset] #history.index es la fecha / filtrar rango seleccionado / filtrado condicional
else:
     filtered_data = history


#Para hacer todo base 100 si es que hay algo que comparar
if selected_comparison_etfs:
     filtered_data = filtered_data/filtered_data.iloc[1]*100

with col2:
    st.line_chart(filtered_data)



tickers = selected_etf

if offset:
     historicos_precios = history[history.index >= now - offset] #history.index es la fecha / filtrar rango seleccionado / filtrado condicional
else:
     historicos_precios = history

if not selected_comparison_etfs:

 ############

  # Calcular rendimientos logarítmicos
    rendimiento_select_etf = np.log(historicos_precios / historicos_precios.shift(1))
    rend_diario_ind = rendimiento_select_etf.mean()

    # Rendimiento Anual
    st.subheader("Annual Performance")
    rend_anual_ind = rend_diario_ind * 250 * 100
    st.markdown(f"<h4 style='color: #FF85A1;'>{rend_anual_ind:+.2f}%</h4>", unsafe_allow_html=True)

    # Desviación Estándar
    st.subheader("Standard Deviation")
    std_anual_ind = rendimiento_select_etf.std() * np.sqrt(250) * 100
    st.markdown(f"<h4 style='color: #FF85A1;'>{std_anual_ind:.2f}%</h4>", unsafe_allow_html=True)

    # Varianza
    st.subheader("Variance")
    var_anual_ind = rendimiento_select_etf.var() * 250 * 100
    st.markdown(f"<h4 style='color: #FF85A1;'>{var_anual_ind:.2f}</h4>", unsafe_allow_html=True)

############
else:

    # Calcular todas las métricas
    rendimientos_etfs = np.log(historicos_precios / historicos_precios.shift(1))
    rend_diario = rendimientos_etfs.mean()
    rend_anual = rend_diario * 250 * 100
    std_anual = rendimientos_etfs.std() * 250 ** 0.5
    var_anual = rendimientos_etfs.var() * 250 * 100

    # Crear un DataFrame con todas las métricas
    metricas_df = pd.DataFrame({
        'Annual Performance (%)': rend_anual,
        'Standard Deviation (%)': std_anual,
        'Variance (%)': var_anual
    })

    # Formatear los números para mejor visualización
    metricas_df = metricas_df.round(2)

    # Mostrar la tabla con formato en Streamlit
    st.subheader("Risk-Return Metrics")
    st.dataframe(
        metricas_df,
        column_config={
            "Annual Performance (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Standard Deviation (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Variance (%)": st.column_config.NumberColumn(
                format="%.2f%%"
            )
        }
    )

    # Si quieres agregar estadísticas descriptivas adicionales:
    with st.expander("Additional Descriptive Statistics"):
        st.write("Correlations between ETFs:")
        st.dataframe(rendimientos_etfs.corr().round(2))

    #correlación
    corr_matrix = rendimientos_etfs.corr() 

    # Crear el mapa de calor
    st.subheader("Heat Map - Correlation Matrix")

    # Crear la figura con un tamaño específico
    fig, ax = plt.subplots(figsize=(10, 8))

    # Crear el mapa de calor con seaborn
    sns.heatmap(
        corr_matrix,
        annot=True,  # Muestra los valores en cada celda
        cmap='coolwarm',  # Esquema de colores (rojo-azul)
        center=0,  # Centra el colormap en 0
        fmt='.2f',  # Formato de dos decimales
        square=True,  # Hace las celdas cuadradas
        cbar_kws={'label': 'Correlation'}  # Etiqueta de la barra de color
    )

    # Rotar las etiquetas del eje x para mejor legibilidad
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    # Ajustar el layout para que no se corten las etiquetas
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Opcional: Agregar una explicación
    with st.expander("📊 Heat Map Interpretation"):
        st.write("""
        - Redder colors indicate stronger positive correlations (closer to 1)
        - Bluer colors indicate stronger negative correlations (closer to -1)
        - Lighter colors indicate correlations closer to 0
        - The diagonal is always 1 because it represents the correlation of an ETF with itself
        """)


