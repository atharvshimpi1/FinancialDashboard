import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

# Set page configuration for a better layout
st.set_page_config(page_title="Company Profit Projection", layout="wide")

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

# Function to process the data
def process_data(file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Drop irrelevant columns
        df = df.drop(columns=['Unnamed: 0'], errors='ignore')

        # Convert 'Period Ending' to datetime
        df['Period Ending'] = pd.to_datetime(df['Period Ending'], errors='coerce')

        # Fill missing values for numerical columns with mean
        df['Net Income'] = df['Net Income'].fillna(df['Net Income'].mean())
        df['Total Revenue'] = df['Total Revenue'].fillna(df['Total Revenue'].mean())

        # Drop rows with critical missing values
        df = df.dropna(subset=['Ticker Symbol', 'Period Ending'])

        # Remove duplicates
        df = df.drop_duplicates()

        # Remove outliers based on Z-score
        df = df[(np.abs(stats.zscore(df['Net Income'])) < 3)]

        # Normalize 'Net Income' and 'Total Revenue'
        scaler = MinMaxScaler()
        df[['Net Income', 'Total Revenue']] = scaler.fit_transform(df[['Net Income', 'Total Revenue']])

        # Extract useful date-based features
        df['Year'] = df['Period Ending'].dt.year

        # Group by 'Ticker Symbol' and get the most recent data for each company
        latest_data = df.sort_values(by='Period Ending', ascending=False).drop_duplicates(subset='Ticker Symbol')

        # Sort by 'Net Income' or 'Total Revenue' to get the top 10 companies
        top_10_companies = latest_data.sort_values(by='Net Income', ascending=False).head(10)

        # Display the top 10 companies
        st.subheader("Top 10 Companies by Net Income")
        st.dataframe(top_10_companies[['Ticker Symbol', 'Net Income']])

        # Prepare data for linear regression
        top_10_data = df[df['Ticker Symbol'].isin(top_10_companies['Ticker Symbol'])]

        # Initialize the model
        model = LinearRegression()

        # Projection for each company
        projections = []
        for company in top_10_companies['Ticker Symbol']:
            company_data = top_10_data[top_10_data['Ticker Symbol'] == company]
            X = company_data[['Year', 'Total Revenue']]
            y = company_data['Net Income']
            model.fit(X, y)

            # Make a projection for the next year
            next_year = max(company_data['Year']) + 1
            next_year_data = np.array([[next_year, company_data['Total Revenue'].iloc[-1]]])
            projected_profit = model.predict(next_year_data)

            projections.append({
                'Ticker Symbol': company,
                'Projected Profit for Next Year': projected_profit[0]
            })

        # Convert projections into a DataFrame
        projection_df = pd.DataFrame(projections)

        # Display the profit projections
        st.subheader("Profit Projections for the Next Year")
        st.dataframe(projection_df)

        # Plot the projections
        st.subheader("Projected Profit for Top 10 Companies")
        plt.figure(figsize=(10, 6))
        plt.bar(projection_df['Ticker Symbol'], projection_df['Projected Profit for Next Year'], color='skyblue')
        plt.title('Projected Profit for Next Year for Top 10 Companies')
        plt.xlabel('Company')
        plt.ylabel('Projected Net Income')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot()

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Streamlit UI
st.title("Company Profit Projection")

# File uploader for CSV input
uploaded_file = st.file_uploader("Upload your dataset (CSV file):", type=["csv"])

if uploaded_file:
    # Save and process the uploaded file
    process_data(uploaded_file)
else:
    st.info("Please upload a CSV file to proceed.")
