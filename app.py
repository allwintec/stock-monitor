import streamlit as st
import yfinance as yf
import pandas as pd

# 輸入股票代碼
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")

# 手動設定天數
days = st.sidebar.number_input("天數", min_value=1, max_value=365, value=5)

# 取得股票資料
ticker = yf.Ticker(stock_symbol)
df = ticker.history(period=f"{days}d", interval="1d")

# 取得股票名稱
stock_name = ticker.info['longName'] if 'longName' in ticker.info else stock_symbol

# 防呆檢查
if df is None or df.empty:
    st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    st.stop()

# 顯示股票名稱
st.subheader(f"{stock_name}（{stock_symbol}）")

# 確保數據列名存在
if 'Close' not in df.columns or 'Volume' not in df.columns:
    st.error("⚠️ 資料中缺少所需的 'Close' 或 'Volume' 列，無法顯示圖表")
    st.stop()

# 顯示最新股價
try:
    latest_price = float(df['Close'].iloc[-1])  # 取得最新的收盤價
    st.metric(label="最新股價", value=f"{latest_price:.2f} 元")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 顯示最新成交量
try:
    latest_volume = df['Volume'].iloc[-1]  # 取得最新的成交量
    st.metric(label="成交量", value=f"{latest_volume:.0f}")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 顯示股價和成交量折線圖
st.subheader("📊 股價與成交量變化")
try:
    st.line_chart(df[['Close', 'Volume']])
except Exception as e:
    st.error(f"⚠️ 顯示圖表時發生錯誤：{e}")

# 顯示支撐價和壓力價設定
st.sidebar.subheader("支撐/壓力價設定")
mode = st.sidebar.radio("模式", ["系統建議", "手動設定"])

if mode == "系統建議":
    # 使用 rolling() 並確保選取最後的數值，並強制轉為 float
    support = float(df['Low'].rolling(3).mean().iloc[-1])  # 取得最近的支撐價
    resistance = float(df['High'].rolling(3).mean().iloc[-1])  # 取得最近的壓力價
else:
    support = st.sidebar.number_input("支撐價", min_value=0.0, value=370.0)
    resistance = st.sidebar.number_input("壓力價", min_value=0.0, value=390.0)

# 顯示支撐價和壓力價
st.info(f"🔵 支撐價：{support:.2f} 元")
st.info(f"🔴 壓力價：{resistance:.2f} 元")

# 判斷是否突破或跌破
try:
    if pd.notna(latest_price):  # 確保 latest_price 有有效數值
        if latest_price < support:
            st.error("📉 股價跌破支撐價")
        elif latest_price > resistance:
            st.success("📈 股價突破壓力價")
        else:
            st.write("⚖️ 股價位於支撐與壓力之間")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")
