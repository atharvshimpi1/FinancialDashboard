import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration for a better layout
st.set_page_config(page_title="Portfolio Visualization", layout="wide")

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
        h1 {
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

# App title
st.title("Portfolio Visualization with Profit and Loss")

# Sidebar for uploading CSV file
st.sidebar.header("Upload a CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Display a preview of the data
    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    # Check for required columns
    required_columns = ['symbol', 'date', 'close']
    if all(col in df.columns for col in required_columns):

        # Convert 'date' column to datetime, handling inconsistent formats and ignoring invalid dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Drop rows with invalid or missing dates
        df = df.dropna(subset=['date'])

        # Sidebar to select stocks
        unique_stocks = df['symbol'].unique()
        selected_stocks = st.sidebar.multiselect(
            "Select Stocks for Portfolio",
            options=unique_stocks,
            default=unique_stocks[:10]
        )

        if selected_stocks:
            # Filter data for selected stocks
            df_selected = df[df['symbol'].isin(selected_stocks)]

            # Assign 100 units for each stock
            quantities = {stock: 100 for stock in selected_stocks}

            # Calculate portfolio value over time
            df_selected['value'] = df_selected['symbol'].map(quantities) * df_selected['close']
            portfolio_value = df_selected.groupby('date')['value'].sum()

            # Profit/Loss calculation
            profit_loss_data = []
            for stock in selected_stocks:
                stock_data = df_selected[df_selected['symbol'] == stock].sort_values(by='date')

                # Calculate profit/loss
                initial_price = stock_data['close'].iloc[0]
                latest_price = stock_data['close'].iloc[-1]
                quantity = quantities[stock]
                profit_loss = (latest_price - initial_price) * quantity

                profit_loss_data.append({
                    'Stock': stock,
                    'Initial Price': initial_price,
                    'Latest Price': latest_price,
                    'Profit/Loss': profit_loss
                })

            # Create a DataFrame for profit/loss
            profit_loss_df = pd.DataFrame(profit_loss_data)

            # Display profit/loss table
            st.subheader("Profit and Loss for Selected Stocks")
            st.dataframe(profit_loss_df)

            # Plot portfolio performance
            st.subheader("Portfolio Performance Over Time")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(portfolio_value.index, portfolio_value.values, label='Portfolio Value', color='blue')
            ax.set_title("Portfolio Performance")
            ax.set_xlabel("Date")
            ax.set_ylabel("Portfolio Value")
            ax.legend()
            st.pyplot(fig)

            # Plot profit/loss as a bar chart
            st.subheader("Profit/Loss Representation")
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['green' if pl >= 0 else 'red' for pl in profit_loss_df['Profit/Loss']]
            ax.bar(profit_loss_df['Stock'], profit_loss_df['Profit/Loss'], color=colors)
            ax.set_title("Profit/Loss by Stock")
            ax.set_xlabel("Stock")
            ax.set_ylabel("Profit/Loss")
            st.pyplot(fig)

        else:
            st.error("Please select at least one stock for the portfolio.")

    else:
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")

else:
    st.info("Please upload a CSV file to proceed.")
