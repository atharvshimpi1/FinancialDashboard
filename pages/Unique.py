import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    fundamentals = pd.read_csv("/Users/atharvshimpi/Downloads/BNP_Dashboard /fundamentals.csv")
    prices_split_adjusted = pd.read_csv("/Users/atharvshimpi/Downloads/BNP_Dashboard /prices-split-adjusted.csv")
    prices = pd.read_csv("/Users/atharvshimpi/Downloads/BNP_Dashboard /prices.csv")
    securities = pd.read_csv("/Users/atharvshimpi/Downloads/BNP_Dashboard /securities.csv")
    return fundamentals, prices_split_adjusted, prices, securities

fundamentals, prices_split_adjusted, prices, securities = load_data()

# Streamlit App
st.title("Stock Market Data Visualizations")
st.sidebar.title("Options")

# Unique Visualization: Seasonality of Prices
st.header("1. Seasonality in Stock Prices")
st.subheader("Monthly Stock Price Patterns")
selected_stock = st.selectbox("Choose a stock to analyze:", prices_split_adjusted["symbol"].unique())

if selected_stock:
    stock_data = prices_split_adjusted[prices_split_adjusted["symbol"] == selected_stock]
    stock_data["month"] = pd.to_datetime(stock_data["date"]).dt.month_name()
    monthly_avg = stock_data.groupby("month")["close"].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    monthly_avg.reindex(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]).plot(kind="line", marker="o", ax=ax)
    ax.set_title(f"Monthly Average Prices for {selected_stock}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Closing Price")
    st.pyplot(fig)

# Unique Visualization: Moving Average Convergence/Divergence (MACD)
st.header("2. Technical Indicator: MACD")
st.subheader("Analyze MACD for a Stock")
macd_stock = st.selectbox("Select a stock for MACD analysis:", prices_split_adjusted["symbol"].unique())

if macd_stock:
    stock_data = prices_split_adjusted[prices_split_adjusted["symbol"] == macd_stock]
    stock_data["12_EMA"] = stock_data["close"].ewm(span=12, adjust=False).mean()
    stock_data["26_EMA"] = stock_data["close"].ewm(span=26, adjust=False).mean()
    stock_data["MACD"] = stock_data["12_EMA"] - stock_data["26_EMA"]
    stock_data["Signal"] = stock_data["MACD"].ewm(span=9, adjust=False).mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stock_data["date"], stock_data["MACD"], label="MACD", color="blue")
    ax.plot(stock_data["date"], stock_data["Signal"], label="Signal Line", color="red")
    ax.set_title(f"MACD Analysis for {macd_stock}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    st.pyplot(fig)

st.write("Use the sidebar to explore unique insights and analyses.")
