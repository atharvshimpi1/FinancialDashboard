import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px
from auth_check import check_authentication

# Check authentication at the start
user = check_authentication()

# Read csv file
try:
    df = pd.read_csv("prices.csv")
except Exception as e:
    st.error("Error loading data: Please ensure 'prices.csv' is in the correct location")
    df = pd.DataFrame()

# Set up Streamlit page configuration
st.set_page_config(
    page_title='Financial Dashboard',
    page_icon='📊',
    layout='wide'
)

# Add logout button in sidebar
with st.sidebar:
    st.write(f"👤 Logged in as: {user['email']}")
    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['user'] = None
        st.switch_page("Account.py")

# Dashboard title and user welcome
st.title("Financial Dashboard")
st.markdown(f"Welcome back! View real-time market data and analysis.")

# Only proceed if we have data
if not df.empty:
    # Top-level filters
    col1, col2 = st.columns([2, 1])
    with col1:
        symbol_filter = st.selectbox("Select Symbol", pd.unique(df['symbol']))
    with col2:
        update_speed = st.slider("Update Speed (seconds)", 1, 10, 1)

    # Creating a single-element container
    placeholder = st.empty()

    # Filter dataframe
    df_filtered = df[df['symbol'] == symbol_filter].copy()

    # Near real-time simulation
    for seconds in range(200):
        # Simulate data updates
        df_filtered['open_new'] = df_filtered['open'] * (1 + np.random.normal(0, 0.02, len(df_filtered)))
        df_filtered['close_new'] = df_filtered['close'] * (1 + np.random.normal(0, 0.02, len(df_filtered)))
        df_filtered['high_new'] = df_filtered['high'] * (1 + np.random.normal(0, 0.02, len(df_filtered)))
        df_filtered['low_new'] = df_filtered['low'] * (1 + np.random.normal(0, 0.02, len(df_filtered)))
        df_filtered['volume_new'] = df_filtered['volume'] * (1 + np.random.normal(0, 0.1, len(df_filtered)))

        # Calculate KPIs
        avg_close = np.mean(df_filtered['close_new'])
        avg_volume = np.mean(df_filtered['volume_new'])
        avg_high = np.mean(df_filtered['high_new'])

        # Previous values for delta calculations
        prev_close = np.mean(df_filtered['close'])
        prev_volume = np.mean(df_filtered['volume'])
        prev_high = np.mean(df_filtered['high'])

        with placeholder.container():
            # KPI Metrics
            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                label="Average Close Price 📈",
                value=f"${round(avg_close, 2):,.2f}",
                delta=f"{round((avg_close - prev_close) / prev_close * 100, 2)}%"
            )

            kpi2.metric(
                label="Average Volume 📊",
                value=f"{int(avg_volume):,}",
                delta=f"{round((avg_volume - prev_volume) / prev_volume * 100, 2)}%"
            )

            kpi3.metric(
                label="Average High Price 💹",
                value=f"${round(avg_high, 2):,.2f}",
                delta=f"{round((avg_high - prev_high) / prev_high * 100, 2)}%"
            )

            # Charts
            fig_col1, fig_col2 = st.columns(2)

            with fig_col1:
                st.markdown("### Price Trends")
                fig = px.line(
                    df_filtered,
                    x='date',
                    y='close_new',
                    title=f"{symbol_filter} Close Price",
                    template="plotly_dark"
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True, key=f"price_{seconds}")

            with fig_col2:
                st.markdown("### Volume Analysis")
                fig2 = px.bar(
                    df_filtered,
                    x='date',
                    y='volume_new',
                    title=f"{symbol_filter} Trading Volume",
                    template="plotly_dark"
                )
                fig2.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    hovermode='x unified'
                )
                st.plotly_chart(fig2, use_container_width=True, key=f"volume_{seconds}")

            # Data Table
            with st.expander("View Detailed Data"):
                st.dataframe(
                    df_filtered[['date', 'open_new', 'high_new', 'low_new', 'close_new', 'volume_new']]
                    .round(2)
                    .style.background_gradient(cmap='Blues')
                )

            # Add dynamic update speed
            time.sleep(update_speed)

else:
    st.error("No data available. Please check your data source.")