import streamlit as st
import yfinance as yf
import pandas as pd

# 側邊欄：股票代碼輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")

# 側邊欄：輸入天數
days = st.sidebar.number_input("輸入查詢天數", min_value=1, value=30)

# 獲取股票資料
df = yf.download(stock_symbol, period=f"{days}d", interval="1d")

# 防呆檢查
if df is None or df.empty:
    st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    st.stop()

# 顯示股價與成交量的表格
st.subheader(f"📊 {stock_symbol} 最近 {days} 天股價與成交量")
st.dataframe(df[['Close', 'Volume']])

# 顯示最新股價
latest_price = df['Close'].iloc[-1] if not df['Close'].empty else None

# 確保最新股價是數字類型
if latest_price is not None and isinstance(latest_price, (int, float)):
    st.metric(label="最新股價", value=f"{latest_price:.2f} 元")
else:
    st.error("⚠️ 無法顯示最新股價")

# 顯示最新成交量
latest_volume = df['Volume'].iloc[-1] if not df['Volume'].empty else None
if latest_volume is not None:
    st.metric(label="最新成交量", value=f"{latest_volume:.0f}")
else:
    st.error("⚠️ 無法顯示最新成交量")

# 支撐/壓力價設定
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
if latest_price < support:
    st.error("📉 股價跌破支撐價")
elif latest_price > resistance:
    st.success("📈 股價突破壓力價")
else:
    st.write("⚖️ 股價位於支撐與壓力之間")
