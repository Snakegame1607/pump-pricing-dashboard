import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------

# PAGE CONFIG

# --------------------------------------------------

st.set_page_config(layout="wide")

# --------------------------------------------------

# TITLE

# --------------------------------------------------

st.markdown("<h1 style='text-align: center;'>Pump Pricing Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("### Strategic Pricing Analysis Tool")

# --------------------------------------------------

# FILE INPUT

# --------------------------------------------------

uploaded_file = st.file_uploader("Upload a new rate card (optional)", type=["xlsx"])

default_file = "Comprehensive Rate card component B.xlsx"

if uploaded_file is not None:
df = pd.read_excel(uploaded_file)
else:
df = pd.read_excel(default_file)

# --------------------------------------------------

# DATA CLEANING

# --------------------------------------------------

df.columns = df.columns.str.strip()

df = df.rename(columns={
df.columns[0]: "State",
df.columns[1]: "HP",
df.columns[2]: "Pump_Type",
df.columns[3]: "Pump_Sub_Type",
df.columns[4]: "Pump_Category",
df.columns[5]: "Controller_Type",
df.columns[6]: "Total_Cost_INR"
})

df["HP"] = df["HP"].astype(str).str.replace("HP", "")
df["HP"] = pd.to_numeric(df["HP"], errors="coerce")

df["Total_Cost_INR"] = df["Total_Cost_INR"].astype(str).str.replace(",", "")
df["Total_Cost_INR"] = pd.to_numeric(df["Total_Cost_INR"], errors="coerce")

df = df.dropna(subset=["State", "HP", "Total_Cost_INR"])

# --------------------------------------------------

# SIDEBAR FILTERS

# --------------------------------------------------

st.sidebar.header("Strategic Filters")

selected_hp = st.sidebar.multiselect(
"Select HP",
sorted(df["HP"].unique()),
default=sorted(df["HP"].unique())
)

selected_states = st.sidebar.multiselect(
"Select States",
sorted(df["State"].unique()),
default=sorted(df["State"].unique())
)

selected_type = st.sidebar.multiselect(
"Pump Type",
df["Pump_Type"].unique(),
default=df["Pump_Type"].unique()
)

selected_controller = st.sidebar.multiselect(
"Controller Type",
df["Controller_Type"].dropna().unique(),
default=df["Controller_Type"].dropna().unique()
)

filtered_df = df[
(df["HP"].isin(selected_hp)) &
(df["State"].isin(selected_states)) &
(df["Pump_Type"].isin(selected_type)) &
(df["Controller_Type"].isin(selected_controller))
]

# --------------------------------------------------

# KPI SECTION

# --------------------------------------------------

national_avg = filtered_df["Total_Cost_INR"].mean()

state_avg = filtered_df.groupby("State")["Total_Cost_INR"].mean()

lowest_state = state_avg.idxmin()
highest_state = state_avg.idxmax()

price_spread = ((state_avg.max() - state_avg.min()) / state_avg.min()) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("National Avg Price", f"₹{national_avg:,.0f}")
col2.metric("Lowest State", lowest_state)
col3.metric("Highest State", highest_state)
col4.metric("Price Spread %", f"{price_spread:.1f}%")

st.markdown("---")

# --------------------------------------------------

# RANKING TABLE

# --------------------------------------------------

ranking = state_avg.reset_index()
ranking.columns = ["State", "Avg Price"]
ranking["Rank"] = ranking["Avg Price"].rank(method="dense").astype(int)
ranking["Deviation vs Avg"] = ranking["Avg Price"] - national_avg
ranking["% Premium"] = (ranking["Deviation vs Avg"] / national_avg) * 100

ranking = ranking.sort_values("Avg Price")

st.subheader("State Price Benchmarking")

st.dataframe(ranking, use_container_width=True)

st.markdown("---")

# --------------------------------------------------

# HP PRICE SENSITIVITY CURVE

# --------------------------------------------------

st.subheader("HP Price Sensitivity Curve")

hp_curve = filtered_df.groupby(["HP", "State"])["Total_Cost_INR"].mean().reset_index()

fig_line = px.line(
hp_curve,
x="HP",
y="Total_Cost_INR",
color="State",
markers=True
)

st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# --------------------------------------------------

# HEATMAP

# --------------------------------------------------

st.subheader("State vs HP Heatmap")

pivot_table = filtered_df.pivot_table(
values="Total_Cost_INR",
index="State",
columns="HP",
aggfunc="mean"
)

fig_heatmap = px.imshow(
pivot_table,
aspect="auto",
color_continuous_scale="Blues"
)

st.plotly_chart(fig_heatmap, use_container_width=True)
