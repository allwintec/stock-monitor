import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib import rcParams

# 設定中文字體避免亂碼
rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
rcParams['axes.unicode_minus'] = False

# 側邊欄輸入
st.sidebar.header("股票設定")
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")
days = st.sidebar.number_input("顯示最近幾天的資料", min_value=3, max_value=60, value=10)

# 下載資料
try:
    df = yf.download(stock_symbol, period=f"{days}d", interval="1d")
    if df.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確。")
        st.stop()
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")
    st.stop()

# 股票中文名稱（簡單處理）
stock_name_map = {
    "2317.TW": "鴻海",
    "2330.TW": "台積電",
    "2303.TW": "聯電",
    "3008.TW": "大立光",
    "2412.TW": "中華電",
    "1301.TW": "台塑",
    # 可擴充更多代碼與名稱
}
stock_name = stock_name_map.get(stock_symbol, stock_symbol)

st.title(f"📈 {stock_name}（{stock_symbol}） 股票資訊")

# 最新股價與成交量
latest_price = df['Close'].iloc[-1]
latest_volume = df['Volume'].iloc[-1]

st.metric(label="最新股價", value=f"{latest_price:.2f} 元")
st.metric(label="成交量", value=f"{latest_volume:,}")

# 顯示折線圖（收盤價）
st.subheader("📉 收盤價與成交量圖")
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.set_title("收盤價與成交量")
ax1.plot(df.index, df['Close'], color='blue', label='收盤價')
ax1.set_ylabel('收盤價', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

ax2 = ax1.twinx()
ax2.bar(df.index, df['Volume'], alpha=0.3, label='成交量', color='gray')
ax2.set_ylabel('成交量', color='gray')
ax2.tick_params(axis='y', labelcolor='gray')

fig.autofmt_xdate()
fig.tight_layout()
st.pyplot(fig)

# 支撐/壓力價設定
st.sidebar.subheader("支撐/壓力價設定")
mode = st.sidebar.radio("選擇模式", ["系統建議", "手動設定"])

if mode == "系統建議":
    support = round(df['Low'].rolling(3).mean().iloc[-1], 2)
    resistance = round(df['High'].rolling(3).mean().iloc[-1], 2)
else:
    support = st.sidebar.number_input("輸入支撐價", min_value=0.0, value=latest_price * 0.9)
    resistance = st.sidebar.number_input("輸入壓力價", min_value=0.0, value=latest_price * 1.1)

try:
    st.info(f"🔵 支撐價：{support:.2f} 元")
    st.info(f"🔴 壓力價：{resistance:.2f} 元")

    if latest_price < support:
        st.error("📉 股價跌破支撐價")
    elif latest_price > resistance:
        st.success("📈 股價突破壓力價")
    else:
        st.write("⚖️ 股價位於支撐與壓力之間")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")

# 漲跌幅計算
try:
    prev_close = df['Close'].iloc[-2] if len(df) >= 2 else None
    if prev_close:
        change = latest_price - prev_close
        pct_change = (change / prev_close) * 100
        st.write(f"💹 漲跌幅：{change:.2f} 元（{pct_change:.2f}%）")
except:
    pass

# 顯示表格
st.subheader("📋 歷史資料表格")
st.dataframe(df[['Open', 'High', 'Low', 'Close', 'Volume']].style.format("{:.2f}"))
