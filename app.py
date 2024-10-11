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
    color_continuous_scale='Viridis',  # Use the Viridis color scale for continuous color mapping
)

# Display the interactive 3D plot
selected_point = st.plotly_chart(fig, use_container_width=True)

# Capture the Plotly click event to select a stock
if selected_point:
    selected_data = st.session_state.get('plotly_click')
    if selected_data:
        # Get the index of the selected point
        selected_index = selected_data['points'][0]['pointIndex']
        # Get the selected stock's name and sector
        selected_stock_name = cluster_df.iloc[selected_index]['Security']
        selected_sector_name = cluster_df.iloc[selected_index]['GICS Sector']
        # Update session state variables for selected stock and sector
        st.session_state.selected_stock = selected_stock_name
        st.session_state.selected_sector = selected_sector_name

# Time Series Plot for Adjusted Close
if st.session_state.selected_stock:
    stock_time_series = time_series_df[time_series_df['Security'] == st.session_state.selected_stock]
    time_fig = px.line(stock_time_series, x='Date', y='Adj Close', title=f'Time Series Data for {st.session_state.selected_stock}')
    st.plotly_chart(time_fig)

    # Show metrics side by side
    selected_metrics = cluster_df[cluster_df['Security'] == st.session_state.selected_stock][['Cumulative Return', 'Annualized Volatility', 'Trend Indicator']].iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Cumulative Return", value=f"{selected_metrics['Cumulative Return']:.2f}")
    col2.metric(label="Annualized Volatility", value=f"{selected_metrics['Annualized Volatility']:.2f}")
    col3.metric(label="Trend Indicator", value=f"{selected_metrics['Trend Indicator']:.2f}")
else:
    st.write("Select a stock to view its time series data.")
