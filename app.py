import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

# 側邊欄：股票代碼與天數輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")
days = st.sidebar.number_input("輸入資料天數", min_value=1, value=3, step=1)

# 根據輸入的天數下載資料
df = yf.download(stock_symbol, period=f"{days}d", interval="1d")

# 防呆檢查
if df is None or df.empty:
    st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    st.stop()

# 確保資料是正確的
st.write("資料內容：", df.tail())

# 檢查資料行數
if len(df) < 2:
    st.warning("⚠️ 資料過少，無法顯示 K 線圖，請增加資料天數。")
else:
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

# 確保 latest_price 是數值
try:
    latest_price = df['Close'].values[-1] if not df['Close'].empty else None
    st.write("latest_price 的值：", latest_price)  # 打印出 latest_price
    if latest_price is not None:  # 如果最新價格有效
        st.metric(label="股價", value=f"{latest_price:.2f} 元")
    else:
        st.warning("⚠️ 無法顯示股價（資料為空）")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 顯示成交量
try:
    latest_volume = df['Volume'].values[-1] if not df['Volume'].empty else None
    if latest_volume is not None:  # 如果最新成交量有效
        st.metric(label="成交量", value=f"{latest_volume:.0f}")
    else:
        st.warning("⚠️ 無法顯示成交量（資料尚未更新）")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 側邊欄：支撐/壓力價設定
st.sidebar.subheader("支撐/壓力價設定")
mode = st.sidebar.radio("模式", ["系統建議", "手動設定"])

if mode == "系統建議":
    # 使用 rolling() 並強制選取最後的有效數值
    support = df['Low'].rolling(3).mean().iloc[-1]  # 取得最近的支撐價
    resistance = df['High'].rolling(3).mean().iloc[-1]  # 取得最近的壓力價
    st.write("支撐價計算過程：", df['Low'].rolling(3).mean())  # 打印出 rolling 計算結果
else:
    support = st.sidebar.number_input("支撐價", min_value=0.0, value=370.0)
    resistance = st.sidebar.number_input("壓力價", min_value=0.0, value=390.0)

# 顯示支撐價和壓力價
st.info(f"🔵 支撐價：{support:.2f} 元")
st.info(f"🔴 壓力價：{resistance:.2f} 元")

# 判斷是否突破或跌破
try:
    if latest_price is not None:  # 確保 latest_price 有有效數值
        if latest_price < support:
            st.error("📉 股價跌破支撐價")
        elif latest_price > resistance:
            st.success("📈 股價突破壓力價")
        else:
            st.write("⚖️ 股價位於支撐與壓力之間")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")
