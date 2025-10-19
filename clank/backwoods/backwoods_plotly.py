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

# locate the CSV: try a few reasonable relative locations
def find_csv(name="data_3.csv"):
    here = Path(__file__).resolve().parent
    candidates = [
        here / "data" / name,
        here.parent / "data" / name,
        here.parent.parent / "data" / name,
        Path.cwd() / "data" / name,
        Path.cwd() / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"Could not find {name}; checked: {candidates}")

DATA_CSV = find_csv("data_3.csv")

# load CSV
df = pd.read_csv(DATA_CSV)

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
# remove outliers where engine_rpm > 8000
df = df[df[engine_col] <= 8000] if engine_col else df



# create subplots: 3 rows sharing x-axis
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.5, 0.25, 0.25],
    subplot_titles=[
        "Engine RPM",
        "Wheel RPM",
        "Sheave Position",
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



fig.update_layout(
    height=900,
    width=1200,
    title_text=f"Data visualization: {DATA_CSV.name}",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
)

fig.update_xaxes(title_text=time_col, row=3, col=1)
fig.update_yaxes(title_text="Engine RPM", row=1, col=1)
fig.update_yaxes(title_text="Wheel RPM", row=2, col=1)
fig.update_yaxes(title_text="Sheave position", row=3, col=1)

# save and show
out_html = Path(__file__).resolve().with_suffix(".plot.html")
fig.write_html(str(out_html), auto_open=True)
print(f"Wrote interactive plot to: {out_html}")