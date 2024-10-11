import streamlit as st
import pandas as pd
import plotly.express as px

# Load datasets
@st.cache
def load_cluster_data():
    return pd.read_feather('stock_cluster_data.feather')  # Replace with your actual file path

@st.cache
def load_time_series_data():
    return pd.read_feather('stock_time_series_cluster_data.feather')  # Replace with your actual file path

# Load datasets using cached functions
cluster_df = load_cluster_data()
time_series_df = load_time_series_data()

# App Layout
st.title("Interactive Stock Cluster Visualization")

# Sector filter dropdown
sector_options = ['All'] + sorted(cluster_df['GICS Sector'].unique())
selected_sector = st.selectbox("Select Sector:", sector_options)

# Dynamic search bar
search_term = st.text_input("Search for a stock:")

# Filter stock suggestions based on search term and sector
filtered_stocks = cluster_df[
    (cluster_df['Security'].str.contains(search_term, case=False)) &
    ((cluster_df['GICS Sector'] == selected_sector) | (selected_sector == 'All'))
].sort_values(by='Avg Volume', ascending=False)  # Sort by average volume

# Show filtered results in dropdown
selected_stock = None
if not filtered_stocks.empty:
    selected_stock = st.selectbox("Select a stock from suggestions:", filtered_stocks['Security'])
else:
    st.write("No results found.")

# 3D Plot with cumulative return, annualized volatility, and trend indicator
fig = px.scatter_3d(
    cluster_df, 
    x='Cumulative Return', 
    y='Annualized Volatility', 
    z='Trend Indicator',
    color='Cluster', 
    hover_name='Security'
)

# Update plot if a stock is selected
if selected_stock:
    stock_data = cluster_df[cluster_df['Security'] == selected_stock]
    fig = px.scatter_3d(
        stock_data, 
        x='Cumulative Return', 
        y='Annualized Volatility', 
        z='Trend Indicator', 
        color='Cluster'
    )

# Display the 3D plot
st.plotly_chart(fig, use_container_width=True)

# Time Series Plot for Adjusted Close
if selected_stock:
    stock_time_series = time_series_df[time_series_df['Security'] == selected_stock]
    time_fig = px.line(stock_time_series, x='Date', y='Adj Close', title=f'Time Series Data for {selected_stock}')
    st.plotly_chart(time_fig)
else:
    st.write("Select a stock to view its time series data.")

# Reset button
if st.button('Reset'):
    st.experimental_rerun()  # Rerun the script to reset everything
