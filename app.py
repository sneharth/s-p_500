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

color_map = { "Stable Low Growth" : "#b5de2b",
           "Moderate Growth High Volatility" : "#482878",
           "Underperforming High Risk" : "#31688e",
           "Exceptional High Growth Outliers": "#1f9e89",
           "Consistent High Growth" : "#26828e",
           "High Growth Volatile" : '#fde725'}
fig = px.scatter_3d(
    cluster_df, 
    x='Cumulative Return', 
    y='Annualized Volatility', 
    z='Trend Indicator',
    color='Cluster_Type', 
    hover_name='Security',
    color_discrete_map=color_map,
    opacity=0.6  # Set lower opacity for all points
)

# If a stock is selected, add a separate trace to highlight the selected stock
if selected_stock and selected_stock != '':
    stock_data = cluster_df[cluster_df['Security'] == selected_stock]
    cluster_type = stock_data['Cluster_Type'].iloc[0]
    cluster_number = stock_data['Cluster'].iloc[0]
    sector = stock_data['GICS Sector'].iloc[0]
    hover_text = (
        f"<b>{selected_stock}</b><br><br>"
        f"Cluster_Type={cluster_type}<br>"
        f"Cumulative Return={stock_data['Cumulative Return'].iloc[0]:.2f}<br>"
        f"Annualized Volatility={stock_data['Annualized Volatility'].iloc[0]:.2f}<br>"
        f"Trend Indicator={stock_data['Trend Indicator'].iloc[0]:.2f}<br>"
    )
    
    fig.add_scatter3d(
        x=stock_data['Cumulative Return'],
        y=stock_data['Annualized Volatility'],
        z=stock_data['Trend Indicator'],
        mode='markers',
        marker=dict(size=8, color='red', symbol='circle'),  # Highlight the selected point with a distinct color
        name=f"Selected: {selected_stock}<br>Cluster: {cluster_type}<br>Sector: {sector}",
        text=hover_text,
        hoverinfo='text',
        opacity=1.0  # Full opacity for the selected point
    )

# Display the 3D plot
st.plotly_chart(fig, use_container_width=True)

# Time Series Plot for Adjusted Close
if selected_stock and selected_stock != '':
    stock_time_series = time_series_df[time_series_df['Security'] == selected_stock]
    stock_time_series.rename(columns={"Close": "Adj. Close"}, inplace=True)
    time_fig = px.line(stock_time_series, x='Date', y='Adj. Close', title=f'Time Series Data for {selected_stock}')
    st.plotly_chart(time_fig)

    # Show metrics side by side, including the cluster number
    selected_metrics = cluster_df[cluster_df['Security'] == selected_stock][['Cumulative Return', 'Annualized Volatility', 'Trend Indicator', 'Cluster_Type']].iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Cumulative Return", value=f"{selected_metrics['Cumulative Return']:.2f}%")
    col2.metric(label="Annualized Volatility", value=f"{selected_metrics['Annualized Volatility']:.2f}%")
    col3.metric(label="Trend Indicator", value=f"{selected_metrics['Trend Indicator']:.2f}%")
    col4, col5 = st.columns(2)
    col4.metric(label="Cluster", value=cluster_type)
    col5.metric(label="Sector", value=sector)
else:
    st.write("Select a stock to view its time series data.")
