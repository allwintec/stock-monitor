import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

# 側邊欄：股票代碼輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")

# 改為日線資料以提高成功率
df = yf.download(stock_symbol, period="7d", interval="1d")

# 防呆檢查
if df is None or df.empty:
    st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    st.stop()

# 確保 latest_price 是數值
try:
    latest_price = df['Close'].iloc[-1] if not df['Close'].empty else None
    if pd.notna(latest_price):  # 如果最新價格有效
        st.metric(label="股價", value=f"{latest_price:.2f} 元")
    else:
        st.warning("⚠️ 無法顯示股價（資料為空）")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 確保 latest_volume 是數值
try:
    latest_volume = df['Volume'].iloc[-1] if not df['Volume'].empty else None
    if pd.notna(latest_volume):  # 如果最新成交量有效
        st.metric(label="成交量", value=f"{latest_volume:.0f}")
    else:
        st.warning("⚠️ 無法顯示成交量（資料尚未更新）")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 顯示 K 線圖
st.subheader("📊 K線圖")
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='K線'))
fig.update_layout(xaxis_rangeslider_visible=False)
st.plotly_chart(fig)

# 側邊欄：支撐/壓力價設定
st.sidebar.subheader("支撐/壓力價設定")
mode = st.sidebar.radio("模式", ["系統建議", "手動設定"])

if mode == "系統建議":
    # 使用 .iloc[-1] 提取最終單一數值，避免產生 Series
    support = df['Low'].rolling(3).mean().iloc[-1]  # 使用 .iloc[-1] 確保是單一數值
    resistance = df['High'].rolling(3).mean().iloc[-1]  # 同上
else:
    support = st.sidebar.number_input("支撐價", min_value=0.0, value=370.0)
    resistance = st.sidebar.number_input("壓力價", min_value=0.0, value=390.0)

# 檢查 support 和 resistance 是否為 Series，並確保它們是數值
if isinstance(support, pd.Series):
    support = support.item()  # 將 Series 轉換為單一數值

if isinstance(resistance, pd.Series):
    resistance = resistance.item()  # 將 Series 轉換為單一數值

# 顯示支撐價
