import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

# 函數：取得股市資料
def get_stock_data(symbol, period="7d", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval)
        if df.empty:
            st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
            return None
        return df
    except Exception as e:
        st.error(f"⚠️ 發生錯誤：{e}")
        return None

# 側邊欄：股票代碼輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")

# 取得股市資料
df = get_stock_data(stock_symbol)

if df is None:
    st.stop()

# 顯示最新股價
def display_latest_price(df):
    try:
        latest_price = df['Close'].iloc[-1] if not df['Close'].empty else None
        if pd.notna(latest_price):
            st.metric(label="股價", value=f"{latest_price:.2f} 元")
        else:
            st.warning("⚠️ 無法顯示股價（資料為空）")
    except Exception as e:
        st.error(f"⚠️ 發生錯誤：{e}")

display_latest_price(df)

# 顯示成交量
def display_latest_volume(df):
    try:
        latest_volume = df['Volume'].iloc[-1] if not df['Volume'].empty else None
        if pd.notna(latest_volume):
            st.metric(label="成交量", value=f"{latest_volume:.0f}")
        else:
            st.warning("⚠️ 無法顯示成交量（資料尚未更新）")
    except Exception as e:
        st.error(f"⚠️ 發生錯誤：{e}")

display_latest_volume(df)

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

# 計算支撐和壓力價
def calculate_support_resistance(df, mode):
    if mode == "系統建議":
        # 使用 rolling() 並強制轉為 float
        support = float(df['Low'].rolling(3).mean().iloc[-1])
        resistance = float(df['High'].rolling(3).mean().iloc[-1])
    else:
        support = st.sidebar.number_input("支撐價", min_value=0.0, value=370.0)
        resistance = st.sidebar.number_input("壓力價", min_value=0.0, value=390.0)
    return support, resistance

support, resistance = calculate_support_resistance(df, mode)

# 顯示支撐價和壓力價
st.info(f"🔵 支撐價：{support:.2f} 元")
st.info(f"🔴 壓力價：{resistance:.2f} 元")

# 判斷是否突破或跌破
def check_price_status(latest_price, support, resistance):
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

check_price_status(df['Close'].iloc[-1], support, resistance)
