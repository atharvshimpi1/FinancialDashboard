import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration for a better layout
st.set_page_config(page_title="Financial Analysis", layout="wide")

# Custom CSS for consistent styling
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
        h1, h2 {
            color: #4CAF50;
        }
        .stTextInput>div>div>input, .stFileUploader>div>div>input {
            background-color: #e0f7fa;
            color: #004d40;
            border-radius: 5px;
            font-size: 16px;
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

# Title for the app
st.title("Financial Analysis: P/E and P/B Ratios")

# Sidebar for file uploads
st.sidebar.header("Upload Your CSV Files")
fundamentals_file = st.sidebar.file_uploader("Upload fundamentals.csv", type="csv")
prices_split_adjusted_file = st.sidebar.file_uploader("Upload prices-split-adjusted.csv", type="csv")
prices_file = st.sidebar.file_uploader("Upload prices.csv", type="csv")
securities_file = st.sidebar.file_uploader("Upload securities.csv", type="csv")

if fundamentals_file and prices_split_adjusted_file and prices_file and securities_file:
    # Load data
    fundamentals = pd.read_csv(fundamentals_file)
    prices_split_adjusted = pd.read_csv(prices_split_adjusted_file)
    prices = pd.read_csv(prices_file)
    securities = pd.read_csv(securities_file)

    # Display previews of uploaded files
    st.header("Preview of Uploaded Data")
    st.subheader("Fundamentals")
    st.write(fundamentals.head())

    st.subheader("Prices Split Adjusted")
    st.write(prices_split_adjusted.head())

    st.subheader("Prices")
    st.write(prices.head())

    st.subheader("Securities")
    st.write(securities.head())

    # Data processing and merging
    fundamentals_filtered = fundamentals[['Ticker Symbol', 'Period Ending', 'Earnings Per Share', 'Total Equity', 'Estimated Shares Outstanding']]
    prices_filtered = prices_split_adjusted[['date', 'symbol', 'close']]
    securities_filtered = securities[['Ticker symbol', 'Security', 'GICS Sector']]

    # Rename columns for consistency
    fundamentals_filtered.rename(columns={'Ticker Symbol': 'symbol'}, inplace=True)
    securities_filtered.rename(columns={'Ticker symbol': 'symbol'}, inplace=True)

    # Calculate Book Value Per Share
    fundamentals_filtered['Book Value Per Share'] = fundamentals_filtered['Total Equity'] / fundamentals_filtered['Estimated Shares Outstanding']

    # Merge dataframes
    merged_data = pd.merge(fundamentals_filtered, securities_filtered, on='symbol', how='inner')
    merged_prices = pd.merge(prices_filtered, merged_data, on='symbol', how='inner')

    # Date conversion and filtering
    merged_prices['date'] = pd.to_datetime(merged_prices['date'])
    merged_prices['Period Ending'] = pd.to_datetime(merged_prices['Period Ending'])
    merged_prices = merged_prices[merged_prices['date'].dt.year == merged_prices['Period Ending'].dt.year]

    # Calculate P/E and P/B ratios
    merged_prices['P/E Ratio'] = merged_prices['close'] / merged_prices['Earnings Per Share']
    merged_prices['P/B Ratio'] = merged_prices['close'] / merged_prices['Book Value Per Share']

    # Extract relevant columns and sort
    time_series_data = merged_prices[['date', 'symbol', 'Security', 'close', 'P/E Ratio', 'P/B Ratio']]
    time_series_data.sort_values(by=['symbol', 'date'], inplace=True)

    # Add sector data
    time_series_data_with_sector = pd.merge(time_series_data, securities_filtered[['symbol', 'GICS Sector']], on='symbol', how='inner')

    # Descriptive statistics
    st.header("Descriptive Statistics")
    descriptive_stats = time_series_data[['P/E Ratio', 'P/B Ratio']].describe()
    st.write(descriptive_stats)

    # Correlation analysis
    st.header("Correlation Between P/E and P/B Ratios")
    correlation = time_series_data[['P/E Ratio', 'P/B Ratio']].corr()
    st.write(correlation)

    # Visualization for a specific stock
    st.header("P/E and P/B Ratios Over Time for a Specific Stock")
    selected_stock = st.selectbox("Select a Stock", time_series_data['symbol'].unique())
    stock_data = time_series_data[time_series_data['symbol'] == selected_stock]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stock_data['date'], stock_data['P/E Ratio'], label='P/E Ratio', color='blue')
    ax.plot(stock_data['date'], stock_data['P/B Ratio'], label='P/B Ratio', linestyle='--', color='orange')
    ax.set_title(f'P/E and P/B Ratios Over Time for {selected_stock}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Ratio Value')
    ax.legend()
    ax.grid()
    st.pyplot(fig)

    # Sector-wise comparison
    st.header("Sector-Wise Comparison of P/E and P/B Ratios")
    sector_ratios = time_series_data_with_sector.groupby('GICS Sector')[['P/E Ratio', 'P/B Ratio']].mean()

    st.bar_chart(sector_ratios)

else:
    st.warning("Please upload all four required CSV files to proceed.")
