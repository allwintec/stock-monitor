import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np

# 設定股市代碼（如昇達科）
stock_symbol = "3491.TW"

# 查詢資料
df = yf.download(stock_symbol, period="5d", interval="1m")

# 顯示股價
st.title(f"{stock_symbol} 即時股價監控")

# 顯示最近價格與成交量
latest_price = df['Close'].iloc[-1]
latest_volume = df['Volume'].iloc[-1]

st.subheader("即時股價與成交量")
st.write(f"最新股價: {latest_price:.2f} 元")
st.write(f"最新成交量: {latest_volume}")

# 顯示K線圖與成交量圖
fig = go.Figure()

fig.add_trace(go.Candlestick(x=df.index,
                             open=df['Open'],
                             high=df['High'],
                             low=df['Low'],
                             close=df['Close'],
                             name="K線"))

fig.update_layout(title=f"{stock_symbol} K線圖",
                  xaxis_title="日期",
                  yaxis_title="股價")
st.plotly_chart(fig)

# 手動或系統設定支撐/壓力價
st.sidebar.title("支撐/壓力價設置")
support = st.sidebar.number_input("支撐價（元）", min_value=0, value=370)
resistance = st.sidebar.number_input("壓力價（元）", min_value=0, value=390)

st.write(f"設定支撐價: {support} 元")
st.write(f"設定壓力價: {resistance} 元")

# 比較是否突破支撐或壓力
if latest_price < support:
    st.warning(f"股價突破支撐: {support} 元！")
if latest_price > resistance:
    st.success(f"股價突破壓力: {resistance} 元！")

# 模擬發送LINE通知
if latest_price < support or latest_price > resistance:
    st.write("發送 LINE 通知...")
