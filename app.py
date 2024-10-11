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
st.title("Stock Cluster Visualization")

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
    opacity=0.6  # Set lower opacity for all points
)

# If a stock is selected, add a separate trace to highlight the selected stock
if selected_stock and selected_stock != '':
    stock_data = cluster_df[cluster_df['Security'] == selected_stock]
    cluster_number = stock_data['Cluster'].iloc[0]
    hover_text = (
        f"<b>{selected_stock}</b><br><br>"
        f"Cumulative Return={stock_data['Cumulative Return'].iloc[0]:.2f}<br>"
        f"Annualized Volatility={stock_data['Annualized Volatility'].iloc[0]:.2f}<br>"
        f"Trend Indicator={stock_data['Trend Indicator'].iloc[0]:.2f}<br>"
        f"Cluster={cluster_number}"
    )
    
    fig.add_scatter3d(
        x=stock_data['Cumulative Return'],
        y=stock_data['Annualized Volatility'],
        z=stock_data['Trend Indicator'],
        mode='markers',
        marker=dict(size=8, color='red', symbol='circle'),  # Highlight the selected point with a distinct color
        name=f"Selected: {selected_stock} (Cluster {cluster_number})",
        text=hover_text,
        hoverinfo='text',
        opacity=1.0  # Full opacity for the selected point
    )

# Display the 3D plot
st.plotly_chart(fig, use_container_width=True)

# Time Series Plot for Adjusted Close
if selected_stock and selected_stock != '':
    stock_time_series = time_series_df[time_series_df['Security'] == selected_stock]
    time_fig = px.line(stock_time_series, x='Date', y='Adj Close', title=f'Time Series Data for {selected_stock}')
    st.plotly_chart(time_fig)

    # Show metrics side by side, including the cluster number
    selected_metrics = cluster_df[cluster_df['Security'] == selected_stock][['Cumulative Return', 'Annualized Volatility', 'Trend Indicator', 'Cluster']].iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Cumulative Return", value=f"{selected_metrics['Cumulative Return']:.2f}")
    col2.metric(label="Annualized Volatility", value=f"{selected_metrics['Annualized Volatility']:.2f}")
    col3.metric(label="Trend Indicator", value=f"{selected_metrics['Trend Indicator']:.2f}")
    col4.metric(label="Cluster", value=f"{selected_metrics['Cluster']}")
else:
    st.write("Select a stock to view its time series data.")
