import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Top Companies Analysis", layout="wide")

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
        h1, h2, h3 {
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
st.title("Top Profit-Generating Companies Analysis")

# File upload section
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    # Load the dataset
    df = pd.read_csv(uploaded_file)


    # Step 2: Sorting by Profit
    if 'Profit' in df.columns:
        st.subheader("Top 10 Profit-Generating Companies")
        top_companies = df.sort_values(by='Profit', ascending=False).head(10)
        st.dataframe(top_companies[['Company', 'Profit']])

    # Step 3: Calculating Returns and Volatility
    if 'Net Income' in df.columns and 'Total Revenue' in df.columns:
        st.subheader("Top Companies with Returns and Volatility")

        # Sort by Net Income
        top_companies = df.sort_values(by='Net Income', ascending=False).head(10)

        # Calculate Returns
        top_companies['Returns (%)'] = (top_companies['Net Income'] / top_companies['Total Revenue']) * 100

        # Calculate Volatility
        volatility = []
        if 'Ticker Symbol' in df.columns:
            for ticker in top_companies['Ticker Symbol']:
                company_data = df[df['Ticker Symbol'] == ticker]
                returns = (company_data['Net Income'] / company_data['Total Revenue']) * 100
                volatility.append(returns.std())
            top_companies['Volatility'] = volatility

        st.dataframe(top_companies[['Ticker Symbol', 'Net Income', 'Returns (%)', 'Volatility']])
    else:
        st.warning("The dataset must include 'Net Income' and 'Total Revenue' columns.")

    # Step 4: Visualization of Volatility
    if 'Volatility' in top_companies.columns:
        st.subheader("Volatility of Top 10 Profit-Generating Companies")

        # Matplotlib Bar Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(top_companies['Ticker Symbol'], top_companies['Volatility'], color='skyblue')
        ax.set_title('Volatility of Top 10 Profit-Generating Companies', fontsize=14, color='#4CAF50')
        ax.set_xlabel('Company', fontsize=12)
        ax.set_ylabel('Volatility (%)', fontsize=12)
        ax.set_xticks(range(len(top_companies['Ticker Symbol'])))
        ax.set_xticklabels(top_companies['Ticker Symbol'], rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)

        # Seaborn Bar Plot
        st.subheader("Seaborn Plot of Volatility")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Ticker Symbol', y='Volatility', data=top_companies, palette='viridis', ax=ax)
        ax.set_title('Volatility of Top 10 Profit-Generating Companies', fontsize=14, color='#4CAF50')
        ax.set_xlabel('Company', fontsize=12)
        ax.set_ylabel('Volatility (%)', fontsize=12)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
else:
    st.info("Please upload a CSV file to proceed.")
