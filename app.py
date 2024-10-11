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

# Define session state variables with defaults
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = ''
if 'selected_sector' not in st.session_state:
    st.session_state.selected_sector = 'All'

# App Layout
st.title("Interactive Stock Cluster Visualization")

# Sector filter dropdown
sector_options = ['All'] + sorted(cluster_df['GICS Sector'].unique())
selected_sector = st.selectbox("Select Sector:", sector_options, index=sector_options.index(st.session_state.selected_sector))

# Update session state
st.session_state.selected_sector = selected_sector

# Dynamic search bar and stock suggestions combined
if selected_sector == 'All':
    sector_filtered_stocks = cluster_df
else:
    sector_filtered_stocks = cluster_df[cluster_df['GICS Sector'] == selected_sector]

selected_stock = st.selectbox(
    "Search and select a stock:",
    options=[''] + list(sector_filtered_stocks['Security'].sort_values()),  # Include an empty option to clear selection
    format_func=lambda x: 'Select a stock' if x == '' else x,
)

# Update session state
st.session_state.selected_stock = selected_stock

# 3D Plot with cumulative return, annualized volatility, and trend indicator
fig = px.scatter_3d(
    cluster_df, 
    x='Cumulative Return', 
    y='Annualized Volatility', 
    z='Trend Indicator',
    color='Cluster', 
    hover_name='Security',
    category_orders={"Cluster": [0, 1, 2, 3, 4, 5]},  # Keep consistent cluster categories
    color_discrete_sequence=px.colors.qualitative.T10  # Use a distinct color palette
)

# Optionally remove the legend
fig.update_layout(showlegend=False)

# Update plot if a stock is selected to show only that stock
if selected_stock and selected_stock != '':
    stock_data = cluster_df[cluster_df['Security'] == selected_stock]
    fig = px.scatter_3d(
        stock_data, 
        x='Cumulative Return', 
        y='Annualized Volatility', 
        z='Trend Indicator', 
        color='Cluster',
        category_orders={"Cluster": [0, 1, 2, 3, 4, 5]},
        color_discrete_sequence=px.colors.qualitative.T10
    )
    fig.update_layout(showlegend=False)  # Ensure legend is hidden for the selected stock plot

# Display the 3D plot
st.plotly_chart(fig, use_container_width=True)

# Time Series Plot for Adjusted Close
if selected_stock and selected_stock != '':
    stock_time_series = time_series_df[time_series_df['Security'] == selected_stock]
    time_fig = px.line(stock_time_series, x='Date', y='Adj Close', title=f'Time Series Data for {selected_stock}')
    st.plotly_chart(time_fig)
else:
    st.write("Select a stock to view its time series data.")

# Reset button functionality to reliably reset session state variables
if st.button('Reset'):
    # Reset the session state variables to defaults without rerunning the entire app
    st.session_state.selected_stock = ''
    st.session_state.selected_sector = 'All'
    # Manually clear out the input fields for the current view
    selected_stock = ''
    selected_sector = 'All'
