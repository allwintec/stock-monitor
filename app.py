import streamlit as st
import yfinance as yf

# 側邊欄：股票代碼輸入
stock_symbol = st.sidebar.text_input("輸入股票代碼（加 .TW）", value="2317.TW")

# 取得股市資料
try:
    df = yf.download(stock_symbol, period="7d", interval="1d")
    if df.empty:
        st.error("⚠️ 無法取得資料，請確認股票代碼是否正確，或稍後再試。")
    else:
        st.write(f"成功載入 {stock_symbol} 的資料")  # 顯示成功訊息
        # 顯示股價
        latest_price = df['Close'].iloc[-1]
        st.metric(label="股價", value=f"{latest_price:.2f} 元")
except Exception as e:
    st.error(f"⚠️ 發生錯誤：{e}")
