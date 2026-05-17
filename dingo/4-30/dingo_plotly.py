from pathlib import Path
import argparse

import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


parser = argparse.ArgumentParser(description="Plot Dingo data with Plotly")
parser.add_argument("csv_path", nargs="?", default="data/data_18.csv", help="Path to CSV file")
args = parser.parse_args()
PATH = args.csv_path

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


time_col = get_col(["time_ms", "time", "timestamp", "t", "time_sec", "time_us"])
engine_col = get_col(["engine_rpm", "engine rpm", "engine"])
secondary_col = get_col(["secondary_rpm", "secondary rpm", "secondary"])
# speed_col = get_col(["speed_mph", "speed", "mph"])
speed_col = None
temp_col = get_col(["temperature_c", "temp_c", "temperature"])
brake_col = get_col(["brake_pot", "brake_position", "brake"])
setpoint_col = get_col(["motor_setpoint", "setpoint", "pwm", "throttle_pwm"])
position_col = get_col(["motor_position", "position"])
fuel_used_col = get_col(["fuel_consumed_l", "fuel_used_l", "fuel_consumed"])
fuel_remaining_col = get_col(["fuel_remaining_l", "fuel_remaining"])
rl_col = get_col(["rl_rpm", "rear_left_rpm", "rear_left"])
rr_col = get_col(["rr_rpm", "rear_right_rpm", "rear_right"])
fl_col = get_col(["fl_rpm", "front_left_rpm", "front_left"])
fr_col = get_col(["fr_rpm", "front_right_rpm", "front_right"])


if time_col is None:
    df = df.reset_index().rename(columns={"index": "sample_index"})
    time_col = "sample_index"
elif "ms" in time_col.lower():
    df[time_col] = df[time_col] / 1000.0
elif "us" in time_col.lower():
    df[time_col] = df[time_col] / 1_000_000.0


wheel_cols = [c for c in [rl_col, rr_col] if c]
if wheel_cols:
    df["wheel_rpm_avg"] = df[rl_col]
    # df["wheel_rpm_avg"] = df["wheel_rpm_avg"].rolling(window=3, center=True).mean()
# use wheel rpm avg to calculate speed if not explicitly present


if speed_col is None and "wheel_rpm_avg" in df.columns:
    wheel_radius_inch = 11  # approximate effective radius of the wheel+sheave in inches
    inch_per_mile = 63360
    minutes_per_hour = 60
    df["speed_mph"] = df["wheel_rpm_avg"] * (2 * 3.14159 * wheel_radius_inch) / inch_per_mile * minutes_per_hour
    speed_col = "speed_mph"


if engine_col and secondary_col:
    df["cvt_gear_ratio"] = df[engine_col] / df[secondary_col].replace(0, pd.NA)


rows = 5
subplot_titles = [
    "Engine RPM",
    "Wheel RPM + Speed",
    "Motor Setpoint vs Position",
    "Secondary RPM",
    "Engine RPM vs Speed",
]

fig = make_subplots(
    rows=rows,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.6] * rows,
    subplot_titles=subplot_titles,
)

if engine_col:
    fig.add_trace(
        go.Scatter(x=df[time_col], y=df[engine_col], mode="lines", name="engine_rpm", line=dict(color="blue")),
        row=1,
        col=1,
    )

# if "wheel_rpm_avg" in df.columns:
#     fig.add_trace(
#         go.Scatter(x=df[time_col], y=df["wheel_rpm_avg"], mode="lines", name="wheel_rpm_avg", line=dict(color="purple")),
#         row=2,
#         col=1,
#     )
#     fig.add_trace(
#         go.Scatter(x=df[time_col], y=df[rl_col], mode="lines", name="rl_col", line=dict(color="purple")),
#         row=2,
#         col=1,
#     )
#     fig.add_trace(
#         go.Scatter(x=df[time_col], y=df[rr_col], mode="lines", name="rr_col", line=dict(color="magenta")),
#         row=2,
#         col=1,
#     )
#     fig.add_trace(
#         go.Scatter(x=df[time_col], y=df[fl_col], mode="lines", name="fl_col", line=dict(color="cyan")),
#         row=2,
#         col=1,
#     )
#     fig.add_trace(  
#         go.Scatter(x=df[time_col], y=df[fr_col], mode="lines", name="fr_col", line=dict(color="orange")),
#         row=2,
#         col=1,
#     )

if speed_col:
    fig.add_trace(
        go.Scatter(x=df[time_col], y=df[speed_col], mode="lines", name="speed_mph", line=dict(color="orange")),
        row=2,
        col=1,
    )

if setpoint_col:
    fig.add_trace(
        go.Scatter(x=df[time_col], y=df[setpoint_col], mode="lines", name="motor_setpoint", line=dict(color="red")),
        row=3,
        col=1,
    )
if position_col:
    fig.add_trace(
        go.Scatter(x=df[time_col], y=df[position_col], mode="lines", name="motor_position", line=dict(color="blue", dash="dash")),
        row=3,
        col=1,
    )

if secondary_col:
    fig.add_trace(
        go.Scatter(x=df[time_col], y=df[secondary_col], mode="lines", name="secondary_rpm", line=dict(color="green")),
        row=4,
        col=1,
    )

if speed_col and engine_col:
    fig.add_trace(
        go.Scatter(
            x=df[speed_col],
            y=df[engine_col],
            mode="markers",
            name="engine_rpm_vs_speed",
            marker=dict(color="brown", size=5, opacity=0.6),
        ),
        row=5,
        col=1,
    )


fig.update_layout(
    height=1600,
    width=1200,
    title_text=f"Data visualization: {PATH}",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
)

fig.update_xaxes(title_text="Time (s)", row=rows, col=1)
fig.update_xaxes(showticklabels=True, nticks=20)

fig.update_yaxes(title_text="RPM", row=1, col=1)
fig.update_yaxes(title_text="RPM / MPH", row=2, col=1)
fig.update_yaxes(title_text="Setpoint / Position", row=3, col=1)
fig.update_yaxes(title_text="RPM", row=4, col=1)
fig.update_yaxes(title_text="Engine RPM", row=5, col=1)


out_html = Path(__file__).resolve().with_suffix(".plot.html")
fig.write_html(str(out_html), auto_open=False)
print(f"Wrote interactive plot to: {out_html}")
