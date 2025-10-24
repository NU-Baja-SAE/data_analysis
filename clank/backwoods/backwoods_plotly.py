from pathlib import Path
import sys
import pandas as pd
from plotly.subplots import make_subplots

#!/usr/bin/env python3
"""
backwoods_data.py

Read data/data_3.csv and create interactive plots with plotly.
Plots:
 - Row 1: engine_rpm, wheel_rpm, secondary_rpm (if present)
 - Row 2: sheave_position
 - Row 3: brake_position (accepts typo 'brake_postion')

Saves an HTML file next to this script and opens an interactive view.
"""

import plotly.graph_objects as go


PATH = "data_2/data_3.csv"

# load CSV
df = pd.read_csv(PATH)

# normalize column names to lowercase stripped names for robust matching
cols_map = {c.lower().strip(): c for c in df.columns}

def get_col(preferred_names):
    for name in preferred_names:
        key = name.lower()
        if key in cols_map:
            return cols_map[key]
    return None

# expected fields (accept common variants and typos)
engine_col = get_col(["engine_rpm", "engine rpm", "engine"])
wheel_col = get_col(["wheel_rpm", "wheel rpm", "wheel"])
secondary_col = get_col(["secondary_rpm", "secondary rpm", "secondary"])
sheave_col = get_col(["sheave_position", "sheave position", "sheave"])
brake_col = get_col(["brake_position", "brake position", "brake_postion", "brake"])

# use an index as x if no explicit time column present
time_col = get_col(["time", "timestamp", "t", "time_s"])
if time_col is None:
    df = df.reset_index().rename(columns={"index": "sample_index"})
    time_col = "sample_index"

#filter data
# remove outliers where engine_rpm > 8000 and filter with moving average
if engine_col:
    df = df[df[engine_col] <= 8000] if engine_col else df
    # correct for wrong magent count
    # df[engine_col] = df[engine_col] * 0.667
    df[engine_col] = df[engine_col].rolling(window=3, center=True).mean()



# filter wheel rpm with a moving average to reduce noise
if wheel_col:
    df[wheel_col] = df[wheel_col].rolling(window=7, center=True).mean()

# make a col for secondary rpm from wheel rpm 
if secondary_col is None and wheel_col:
    gear_ratio = 6.667  # fixed gear ratio
    df["secondary_rpm"] = df[wheel_col] * gear_ratio
    secondary_col = "secondary_rpm"


# make a new column for the cvt gear ratio if both engine and wheel rpm are present
geeb_reduction = 6.67
if engine_col and wheel_col:
    df["cvt_gear_ratio"] = df[engine_col] / (df[wheel_col] * geeb_reduction)
    


# convert wheel rpm to mph, assuming 22 inch diameter wheels
if wheel_col:
    wheel_radius_inch = 11  # 22 inch diameter
    inch_per_mile = 63360
    minutes_per_hour = 60
    df[wheel_col] = df[wheel_col] * (2 * 3.14159 * wheel_radius_inch) / inch_per_mile * minutes_per_hour

if sheave_col:
    df[sheave_col] = df[sheave_col].rolling(window=5, center=True).mean()



# create subplots: 3 rows sharing x-axis
fig = make_subplots(
    rows=6, cols=1, shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    subplot_titles=[
        "Engine RPM",
        "Car Speed (MPH from Wheel RPM)",
        "Sheave Position",
        "Gear Ratio (Engine RPM / (Wheel RPM * 6.67))" if "cvt_gear_ratio" in df.columns else "",
        "Gear Ratio vs Sheave Position",
        "Shift Plot"
    ],
)

# Row 1: RPM traces
fig.add_trace(
    go.Scatter(x=df[time_col], y=df[engine_col], mode="lines", name="engine_rpm", line=dict(color="blue")),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(x=df[time_col], y=df[wheel_col], mode="lines", name="wheel_rpm", line=dict(color="red")),
    row=2, col=1
)

# Row 3: sheave position
fig.add_trace(
    go.Scatter(x=df[time_col], y=df[sheave_col], mode="lines", name="sheave_position", line=dict(color="green")),
    row=3, col=1
)

# Row 4: gear ratio if available
fig.add_trace(
    go.Scatter(x=df[time_col], y=df["cvt_gear_ratio"], mode="lines", name="cvt_gear_ratio", line=dict(color="purple")),
    row=4, col=1)



# Row 5: gear ratio vs sheave position scatter
fig.add_trace(
    go.Scatter(x=df[sheave_col], y=df["cvt_gear_ratio"], mode="markers", name="gear_ratio_vs_sheave", marker=dict(color="orange", size=5, opacity=0.6)),
    row=5, col=1
)

# Row 6: shift plot (engine rpm vs secondary rpm)
fig.add_trace(
    go.Scatter(x=df[wheel_col], y=df[engine_col], mode="markers", name="shift_plot", marker=dict(color="brown", size=5, opacity=0.6)),
    row=6, col=1
)

sheave_setpoints = [
    {"pos": -90, "name": "sheave_idle", "color" : "black"}, 
    {"pos": -65, "name": "sheave_low", "color" : "orange"}, 
    {"pos": 50, "name": "sheave_low_max", "color" : "blue"}, 
    {"pos": 220, "name": "sheave_high", "color" : "red"}]

engine_rpm_setpoints = [
    {"rpm": 1900, "name": "engine_idle", "color" : "orange"}, 
    {"rpm": 3000, "name": "engine_max_torque", "color" : "red"},
    {"rpm": 3800, "name": "engine_redline", "color" : "black"}]

for sp in sheave_setpoints:
    fig.add_trace(
        go.Scatter(
            x=df[time_col],
            y=[sp["pos"]] * len(df),
            mode="lines",
            name=sp["name"],
            line=dict(color=sp["color"], dash="dash"),
        ),
        row=3,
        col=1,
    )
for sp in engine_rpm_setpoints:
    fig.add_trace(
        go.Scatter(
            x=df[time_col],
            y=[sp["rpm"]] * len(df),
            mode="lines",
            name=sp["name"],
            line=dict(color=sp["color"], dash="dash"),
        ),
        row=1,
        col=1,
    )


fig.update_layout(
    height=2200,
    width=1200,
    title_text=f"Data visualization: {PATH}",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
)

fig.update_xaxes(title_text=time_col, row=4, col=1)
fig.update_yaxes(title_text="Engine RPM", row=1, col=1)
fig.update_yaxes(title_text="MPH", row=2, col=1)
fig.update_yaxes(title_text="Sheave position", row=3, col=1)

# save and show
out_html = Path(__file__).resolve().with_suffix(".plot.html")
fig.write_html(str(out_html), auto_open=True)
print(f"Wrote interactive plot to: {out_html}")