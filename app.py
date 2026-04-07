import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv", thousands=',')

# -----------------------------
# CLEAN DATA
# -----------------------------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df = df.sort_values(by='Date')

# -----------------------------
# CREATE KPIs
# -----------------------------
df['Transfer_Efficiency'] = df.iloc[:, 3] / df.iloc[:, 2]
df['Discharge_Effectiveness'] = df.iloc[:, 5] / df.iloc[:, 4]
df['Pipeline_Throughput'] = df.iloc[:, 5] / (df.iloc[:, 1] + 1)
df['Backlog'] = df.iloc[:, 1] - df.iloc[:, 5]

# -----------------------------
# TITLE
# -----------------------------
st.title("Care Transition Efficiency Dashboard")

# -----------------------------
# DATE FILTER
# -----------------------------
start_date = st.date_input("Start Date", df['Date'].min())
end_date = st.date_input("End Date", df['Date'].max())

df = df[(df['Date'] >= pd.to_datetime(start_date)) &
        (df['Date'] <= pd.to_datetime(end_date))]

# -----------------------------
# KPI TOGGLE
# -----------------------------
st.subheader("Select KPIs to Display")

show_transfer = st.checkbox("Transfer Efficiency", True)
show_discharge = st.checkbox("Discharge Effectiveness", True)
show_throughput = st.checkbox("Pipeline Throughput", True)

# -----------------------------
# DATASET
# -----------------------------
st.subheader("Full Dataset")
st.dataframe(df, use_container_width=True)

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Avg Transfer Efficiency", round(df['Transfer_Efficiency'].mean(), 2))
col2.metric("Avg Discharge Effectiveness", round(df['Discharge_Effectiveness'].mean(), 2))
col3.metric("Avg Pipeline Throughput", round(df['Pipeline_Throughput'].mean(), 2))

# -----------------------------
# KPI TRENDS (FIXED)
# -----------------------------
st.subheader("KPI Trends Over Time")

fig, ax = plt.subplots()

if show_transfer:
    ax.plot(df['Date'], df['Transfer_Efficiency'], label='Transfer Efficiency', linewidth=2)

if show_discharge:
    ax.plot(df['Date'], df['Discharge_Effectiveness'], label='Discharge Effectiveness', linewidth=2)

if show_throughput:
    ax.plot(df['Date'], df['Pipeline_Throughput'], label='Pipeline Throughput', linewidth=2)

# FIX: reduce date clutter
dates = df['Date']
step = max(len(dates)//10, 1)

ax.set_xticks(dates[::step])
ax.set_xticklabels(dates.dt.strftime('%Y-%m-%d')[::step], rotation=45)

ax.set_xlabel("Date")
ax.set_ylabel("Values")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# -----------------------------
# BACKLOG TREND (FIXED)
# -----------------------------
st.subheader("Backlog Trend")

fig2, ax2 = plt.subplots()

ax2.plot(df['Date'], df['Backlog'], linewidth=2)
ax2.axhline(0)

# FIX: reduce date clutter
ax2.set_xticks(dates[::step])
ax2.set_xticklabels(dates.dt.strftime('%Y-%m-%d')[::step], rotation=45)

ax2.set_xlabel("Date")
ax2.set_ylabel("Backlog")
ax2.grid(True)

st.pyplot(fig2)

# -----------------------------
# MONTHLY ANALYSIS (CLEAN)
# -----------------------------
df['Month'] = df['Date'].dt.to_period('M')

st.subheader("Monthly Pipeline Throughput")

monthly = df.groupby('Month')['Pipeline_Throughput'].mean()

fig3, ax3 = plt.subplots()

ax3.plot(monthly.index.astype(str), monthly.values, linewidth=2)

# reduce labels
ax3.set_xticks(range(0, len(monthly.index), 2))
ax3.set_xticklabels(monthly.index.astype(str)[::2], rotation=45)

ax3.set_xlabel("Month")
ax3.set_ylabel("Avg Throughput")
ax3.grid(True)

st.pyplot(fig3)

# -----------------------------
# WEEKDAY VS WEEKEND
# -----------------------------
df['DayType'] = df['Date'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')

st.subheader("Weekday vs Weekend Discharge Effectiveness")

day_analysis = df.groupby('DayType')['Discharge_Effectiveness'].mean()
st.write(day_analysis)

# -----------------------------
# STABILITY
# -----------------------------
st.subheader("Outcome Stability")

st.write("Discharge Variability (Std Dev):", round(df['Discharge_Effectiveness'].std(), 2))

# -----------------------------
# STAGNATION
# -----------------------------
st.subheader("Stagnation Detection")

df['Throughput_Change'] = df['Pipeline_Throughput'].diff()
stagnation = df[df['Throughput_Change'].abs() < 0.01]

st.dataframe(stagnation[['Date', 'Pipeline_Throughput']].head(), use_container_width=True)

# -----------------------------
# ALERT SYSTEM
# -----------------------------
st.subheader("System Alerts")

if df['Backlog'].mean() > 0:
    st.error("⚠️ Backlog accumulating")
elif df['Discharge_Effectiveness'].mean() < 0.5:
    st.warning("⚠️ Low discharge effectiveness")
else:
    st.success("✅ System operating efficiently")

# -----------------------------
# PIPELINE FLOW
# -----------------------------
st.subheader("Care Pipeline Flow")

st.write("""
CBP Custody → HHS Care → Sponsor Placement

- Children are apprehended and placed in CBP custody
- Transferred to HHS care
- Discharged to sponsors
""")

# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("Key Insights")

st.write("""
- Transfer efficiency is stable → intake system is consistent
- Discharge effectiveness is very low → major delay in placement
- Backlog shows system pressure and recovery cycles
- Monthly and weekday trends indicate performance variation
- Stability analysis shows inconsistency in outcomes
""")