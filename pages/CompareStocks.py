import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Set page configuration for a better layout
st.set_page_config(page_title="Stock Price Movement Comparison", layout="wide")

# Custom CSS to improve UI appearance
st.markdown("""
    <style>
        body {
            background-color: #f4f4f9;
            font-family: 'Helvetica', sans-serif;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #4CAF50;
        }
        .stTextInput>div>div>input {
            background-color: #e0f7fa;
            color: #004d40;
            border-radius: 5px;
            font-size: 16px;
        }
        .stSelectbox>div>div>input {
            background-color: #e0f7fa;
            color: #004d40;
            border-radius: 5px;
            font-size: 16px;
        }
        .stSlider>div>div>div {
            background-color: #e0f7fa;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #388e3c;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("Stock Price Movement Comparison")
st.markdown("""
This app allows you to compare the price movements and cumulative returns of two stocks over a specified period.
Upload a CSV file containing stock data with the required columns (`date`, `symbol`, `open`, `close`) and use the controls below to analyze.
""")

# File uploader for the dataset
uploaded_file = st.file_uploader("Upload your dataset (CSV file):", type=["csv"])

if uploaded_file is not None:
    # Load the uploaded dataset
    try:
        df = pd.read_csv(uploaded_file)

        # Data preprocessing
        if not {'date', 'symbol', 'open', 'close'}.issubset(df.columns):
            st.error("The uploaded dataset must contain the columns: 'date', 'symbol', 'open', and 'close'.")
        else:
            df.dropna(subset=['date', 'symbol'], inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.sort_values(by=['symbol', 'date'], inplace=True)

            # Calculate price change and percentage change
            df['price_change'] = df['close'] - df['open']
            df['price_change_pct'] = ((df['close'] - df['open']) / df['open']) * 100

            # Interactive input widgets
            col1, col2 = st.columns(2)

            with col1:
                stock1 = st.text_input("Enter the first stock symbol (e.g., AAPL):").upper()

            with col2:
                stock2 = st.text_input("Enter the second stock symbol (e.g., MSFT):").upper()

            # Select date range with sliders
            start_date = st.date_input("Select the start date:", min_value=df['date'].min(), max_value=df['date'].max())
            end_date = st.date_input("Select the end date:", min_value=df['date'].min(), max_value=df['date'].max())

            # Ensure the date range is valid
            if start_date > end_date:
                st.error("Start date cannot be after the end date. Please select a valid range.")
            else:
                if stock1 and stock2 and start_date and end_date:
                    # Filter the data based on the date range and selected stocks
                    filtered_data = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]
                    stock1_data = filtered_data[filtered_data['symbol'] == stock1]
                    stock2_data = filtered_data[filtered_data['symbol'] == stock2]

                    # Ensure there is data for both stocks
                    if stock1_data.empty or stock2_data.empty:
                        st.error(f"No data found for the symbols '{stock1}' or '{stock2}' in the selected date range.")
                    else:
                        # Align the data for the two stocks by date
                        aligned_data = pd.merge(
                            stock1_data[['date', 'close']].rename(columns={'close': f'{stock1}_close'}),
                            stock2_data[['date', 'close']].rename(columns={'close': f'{stock2}_close'}),
                            on='date',
                            how='inner'
                        )

                        # Calculate percentage changes and cumulative returns
                        aligned_data[f'{stock1}_pct_change'] = aligned_data[f'{stock1}_close'].pct_change() * 100
                        aligned_data[f'{stock2}_pct_change'] = aligned_data[f'{stock2}_close'].pct_change() * 100
                        aligned_data[f'{stock1}_cumulative_return'] = (1 + aligned_data[f'{stock1}_pct_change'] / 100).cumprod() - 1
                        aligned_data[f'{stock2}_cumulative_return'] = (1 + aligned_data[f'{stock2}_pct_change'] / 100).cumprod() - 1

                        # Plot stock price movement
                        st.subheader("Stock Price Movement")
                        fig, ax = plt.subplots(figsize=(14, 7))
                        ax.plot(aligned_data['date'], aligned_data[f'{stock1}_close'], label=f'{stock1} Closing Price', color='tab:blue', linewidth=2)
                        ax.plot(aligned_data['date'], aligned_data[f'{stock2}_close'], label=f'{stock2} Closing Price', color='tab:orange', linewidth=2)
                        ax.set_title(f"Stock Price Movement: {stock1} vs {stock2}", fontsize=16)
                        ax.set_xlabel("Date", fontsize=12)
                        ax.set_ylabel("Price (USD)", fontsize=12)
                        ax.legend(loc="upper left")
                        ax.grid(True, linestyle="--", alpha=0.6)
                        st.pyplot(fig)

                        # Plot cumulative returns
                        st.subheader("Cumulative Returns")
                        fig, ax = plt.subplots(figsize=(14, 7))
                        ax.plot(aligned_data['date'], aligned_data[f'{stock1}_cumulative_return'], label=f'{stock1} Cumulative Return', color='tab:blue', linewidth=2)
                        ax.plot(aligned_data['date'], aligned_data[f'{stock2}_cumulative_return'], label=f'{stock2} Cumulative Return', color='tab:orange', linewidth=2)
                        ax.set_title(f"Cumulative Returns: {stock1} vs {stock2}", fontsize=16)
                        ax.set_xlabel("Date", fontsize=12)
                        ax.set_ylabel("Cumulative Return", fontsize=12)
                        ax.legend(loc="upper left")
                        ax.grid(True, linestyle="--", alpha=0.6)
                        st.pyplot(fig)
                else:
                    st.warning("Please enter both stock symbols and select a valid date range.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload a CSV file to begin.")
