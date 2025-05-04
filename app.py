import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

# 側邊欄：股票代碼輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="3491.TW")

# 下載資料
df = yf.download(stock_symbol, period="5d", interval="1m")

# ✅ 正確的防呆檢查（變數名稱 df）
if df is None or df.empty:
    st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    st.stop()

# 顯示標題與即時資訊
st.title(f"{stock_symbol} 即時股價監控")
latest_price = df['Close'].iloc[-1]
latest_volume = df['Volume'].iloc[-1]

st.subheader("📈 最新價格資訊")
st.metric(label="股價", value=f"{latest_price:.2f} 元")
st.metric(label="成交量", value=f"{latest_volume:.0f}")

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

# 側邊欄：支撐/壓力設定
st.sidebar.subheader("支撐/壓力價設定")
mode = st.sidebar.radio("模式", ["系統建議", "手動設定"])

if mode == "系統建議":
    support = round(df['Low'].rolling(5).mean().iloc[-1], 2)
    resistance = round(df['High'].rolling(5).mean().iloc[-1], 2)
else:
    support = st.sidebar.number_input("支撐價", min_value=0.0, value=370.0)
    resistance = st.sidebar.number_input("壓力價", min_value=0.0, value=390.0)

st.info(f"支撐價：{support} 元")
st.info(f"壓力價：{resistance} 元")

# 判斷是否突破或跌破
if latest_price < support:
    st.error("⚠️ 股價跌破支撐價")
elif latest_price > resistance:
    st.success("🚀 股價突破壓力價")
else:
    st.write("價格尚在支撐／壓力區間內")
