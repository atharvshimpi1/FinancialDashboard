import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Page Configuration
st.set_page_config(page_title="Price Performance Heatmap", layout="wide")

# Custom CSS for consistent UI
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
        h1, h2, h3, h4 {
            color: #4CAF50;
        }
        .stTextInput>div>div>input,
        .stFileUploader>div>div>input {
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

# Title and Description
st.title("Price Performance Heatmap")
st.markdown("""
This heatmap visualizes the normalized price performance of the **top 50 most traded stocks** for a selected year. 
Upload a CSV file containing stock data with the following columns: `date`, `symbol`, `close`, and `volume`.
""")

# File Uploader
uploaded_file = st.file_uploader("Upload your dataset (CSV file):", type=["csv"])

if uploaded_file:
    # Load Data
    try:
        prices_data = pd.read_csv(uploaded_file)

        # Ensure 'date' column exists and process it
        if 'date' in prices_data.columns:
            prices_data['date'] = pd.to_datetime(prices_data['date'], format='%Y-%m-%d', errors='coerce')
            prices_data['year'] = prices_data['date'].dt.year
        else:
            st.error("The dataset must contain a 'date' column.")
            st.stop()

        # Sidebar Year Selector
        available_years = sorted(prices_data['year'].dropna().unique())
        selected_year = st.sidebar.selectbox("Select a Year:", available_years)

        # Filter data for the selected year
        year_data = prices_data[prices_data['year'] == selected_year]

        # Calculate total traded volume for each stock and find the top 50
        top_traded_stocks = year_data.groupby('symbol')['volume'].sum().nlargest(50).index

        # Filter for these top 50 stocks
        top_traded_data = year_data[year_data['symbol'].isin(top_traded_stocks)]

        # Create a pivot table for price performance
        pivot_data = top_traded_data.pivot_table(
            index='date', columns='symbol', values='close', aggfunc='mean'
        )

        # Normalize the data to show relative performance
        normalized_data = pivot_data.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=0)

        # Plot the Heatmap
        st.subheader(f"Heatmap for {selected_year}")
        fig, ax = plt.subplots(figsize=(16, 10))
        im = ax.imshow(normalized_data.T, aspect='auto', cmap='coolwarm', interpolation='nearest')

        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Normalized Price Performance', fontsize=12)

        # Set title and labels
        ax.set_title(f"Price Performance Heatmap for Top 50 Most Traded Stocks ({selected_year})", fontsize=14)
        ax.set_xlabel("Date Index", fontsize=12)
        ax.set_ylabel("Stocks", fontsize=12)
        ax.set_yticks(np.arange(len(normalized_data.columns)))
        ax.set_yticklabels(normalized_data.columns, fontsize=8)
        ax.set_xticks(np.arange(len(normalized_data.index))[::30])  # Show fewer date ticks for readability
        ax.set_xticklabels(normalized_data.index.strftime('%Y-%m-%d')[::30], rotation=45, fontsize=8)

        # Display the plot in Streamlit
        st.pyplot(fig)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload a CSV file to proceed.")
