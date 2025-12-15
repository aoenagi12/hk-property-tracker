import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.info("📊 This dashboard uses a sample dataset of ~300 transactions from 2023. Full version would include multi-year data and more districts.")
st.title("🏠 Hong Kong Property Price Tracker (2023 Snapshot)")
st.markdown("Interactive dashboard of 2023 residential property transactions in Hong Kong (Centaline data via Kaggle)")

conn = sqlite3.connect('hk_property.db')
df = pd.read_sql_query("SELECT * FROM transactions", conn)
conn.close()

# Sidebar filters
st.sidebar.header("Filters")
districts = sorted(df['district'].dropna().unique())
selected_district = st.sidebar.multiselect("District", options=districts, default=districts[:3] if len(districts) >= 3 else districts)

# Year filter — smart handling for limited years
years = pd.to_datetime(df['date']).dt.year.unique()
years_sorted = sorted(years)

if len(years_sorted) > 1:
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=int(years_sorted[0]),
        max_value=int(years_sorted[-1]),
        value=(int(years_sorted[0]), int(years_sorted[-1]))
    )
else:
    st.sidebar.write(f"Data available only for year: **{years_sorted[0]}**")
    year_range = (years_sorted[0], years_sorted[0])

# Filter data
filtered_df = df.copy()
if selected_district:
    filtered_df = filtered_df[filtered_df['district'].isin(selected_district)]
filtered_df = filtered_df[pd.to_datetime(filtered_df['date']).dt.year.between(year_range[0], year_range[1])]

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Average Price (HKD)", f"{filtered_df['price'].mean():,.0f}")
col2.metric("Avg Price per Sqft (HKD)", f"{filtered_df['price_per_sqft'].mean():,.0f}")
col3.metric("Transactions Shown", len(filtered_df))

# Trend chart (monthly)
st.subheader("Price per Sqft Trend Over Time")
monthly = filtered_df.copy()
monthly['month'] = pd.to_datetime(monthly['date']).dt.to_period('M').astype(str)
trend_df = monthly.groupby('month')['price_per_sqft'].mean().reset_index()
fig1 = px.line(trend_df, x='month', y='price_per_sqft', title="Monthly Average Price per Sqft")
st.plotly_chart(fig1, use_container_width=True)

# District comparison
st.subheader("Average Price per Sqft by District")
district_avg = filtered_df.groupby('district')['price_per_sqft'].mean().reset_index()
fig2 = px.bar(district_avg.sort_values('price_per_sqft', ascending=False), x='district', y='price_per_sqft', title="Avg Price per Sqft by District")
st.plotly_chart(fig2, use_container_width=True)

# Price distribution
st.subheader("Transaction Price Distribution")
fig3 = px.histogram(filtered_df, x='price', nbins=50, title="Prices (HKD)")
st.plotly_chart(fig3, use_container_width=True)

# Sample data
st.subheader("Sample Transactions")
st.dataframe(filtered_df[['date', 'address', 'district', 'price', 'saleable_area', 'price_per_sqft']].head(200))

st.caption("Data source: Hong Kong Housing Prices sample – 299 transactions in 2023 (Kaggle / Centaline scrape). Built as portfolio demo project.")