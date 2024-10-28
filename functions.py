import yfinance as yf
import streamlit as st

# Función para obtener datos del ETF
@st.cache_data
def get_etf_data(ticker):
    etf = yf.Ticker(ticker)
    info = etf.info
    #history = etf.history(period="max")
    return info #, history

# Función para el Multiselect
@st.cache_data
def get_multietf_data(tickers):
    history = yf.download(tickers)
    return history


def get_stat_string(name, type, data):
    if name in data:
        if type == "$":
            return f'${data[name]:,.2f}'
        elif type == "%":
            val = data[name] * 100
            return f'{val:.2f}%'
        elif type == "f":
            return f'{data[name]:,.2f}'
        elif type == "M":
            val = data[name] / 1000000
            return f'{val:,.2f}'
        else:
            return f'{data[name]:,}'
    
    return 'NA'



