import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 股票代碼輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")
days = st.sidebar.number_input("輸入要查詢的天數", min_value=1, max_value=60, value=10, step=1)

# 股票名稱對照表（可擴充）
stock_names = {
    "2317.TW": "鴻海",
    "2330.TW": "台積電",
    "3481.TW": "群創",
    "0050.TW": "元大台灣50"
}

# 抓取資料（1 天為單位）
df = yf.download(stock_symbol, period=f"{days}d", interval="1d")

# 檢查資料
if df.empty:
    st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    st.stop()

# 顯示中文股票名稱
stock_name = stock_names.get(stock_symbol, "未知股票")
st.subheader(f"{stock_name}（{stock_symbol}） 的 {days} 天股價與成交量")

# 最新股價與成交量
latest_price = df['Close'].iloc[-1]
latest_volume = df['Volume'].iloc[-1]
st.metric(label="最新股價", value=f"{latest_price:.2f} 元")
st.metric(label="最新成交量", value=f"{latest_volume:.0f}")

# 顯示折線圖 - 收盤價
fig_price = px.line(df, x=df.index, y="Close", title="收盤價走勢")
st.plotly_chart(fig_price)

# 顯示折線圖 - 成交量
fig_volume = px.line(df, x=df.index, y="Volume", title="成交量走勢")
st.plotly_chart(fig_volume)

# 顯示表格
st.subheader("詳細數據")
st.dataframe(df[['Open', 'High', 'Low', 'Close', 'Volume']].round(2))
