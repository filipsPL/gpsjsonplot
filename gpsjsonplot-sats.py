#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import json
import argparse
from datetime import datetime


# Function to plot satellites on a polar plot with colored points
def plot_satellites(data, last=False):
    if "satellites" not in data:
        return  # Skip data without satellite information

    angles = np.array([satellite.get("az", np.nan) for satellite in data["satellites"]])
    elevations = np.array([90 - satellite.get("el", np.nan) for satellite in data["satellites"]])
    snr_values = np.array([satellite.get("ss", np.nan) for satellite in data["satellites"]])
    used_flags = np.array([satellite.get("used", False) for satellite in data["satellites"]])

    valid_data_mask = np.isfinite(angles) & np.isfinite(elevations) & np.isfinite(snr_values) & np.isfinite(used_flags)
    angles, elevations, snr_values, used_flags = (
        angles[valid_data_mask],
        elevations[valid_data_mask],
        snr_values[valid_data_mask],
        used_flags[valid_data_mask],
    )

    if not angles.size or not elevations.size or not snr_values.size or not used_flags.size:
        return  # Skip data without valid satellite information

    # Normalize SNR values for colormap
    norm = plt.Normalize(np.min(snr_values), np.max(snr_values))
    colors = plt.cm.viridis(norm(snr_values))

    # Plot satellites with colored points and different shapes
    marker = "o" if not last else "H"
    color = "orange" if last else colors
    size = 50 if last else 10

    plt.scatter(np.radians(angles), elevations, color=color, marker=marker, alpha=0.85, edgecolor="black", linewidth=0.1, s=size)

def read_uniform_sample(jsonfile, n):
    data = []
    with open(jsonfile, "r") as file:
        # Read all lines from the file
        all_lines = file.readlines()

        if n == 0:
            # If n is 0, read all lines
            n = len(all_lines)

        step_size = max(len(all_lines) // n, 1)

        for i in range(0, len(all_lines), step_size):
            line = all_lines[i]
            try:
                json_data = json.loads(line)
                # Check if the "class" is "SKY"
                if json_data.get("class") == "SKY":
                    data.append(json_data)
            except json.decoder.JSONDecodeError as e:
                print(f"Error decoding JSON at line {i + 1}: {e}")
                # print("Problematic JSON:", line.strip())

    return data

# Use argparse to get file names and other parameters
parser = argparse.ArgumentParser(description="Plot satellite positions from JSON data.")
parser.add_argument("--json", dest="jsonfile", required=True, help="input json file")
parser.add_argument("--outfile", dest="outfile", required=True, help="output image file")
parser.add_argument("--n", dest="n", default=50, type=int, help="sample n points; n=0 - get all points")

args = parser.parse_args()
jsonfile = args.jsonfile
outfile = args.outfile
n = args.n



data = read_uniform_sample(jsonfile, n)


points = len(data)

# Create a polar plot
plt.figure(figsize=(4.6, 3.9))  # x - y
ax = plt.axes(projection="polar")

# Rotate the plot so that 0 degrees is on the north
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)

# Plot satellites for each selected JSON object
for satellite_data in data:
    plot_satellites(satellite_data)


last_data = data[-1] if data else None
if last_data:
    plot_satellites(last_data, last=True)


# Customize the plot
plt.title("Satellite Positions with SNR")

# Add color bar for SNR values
snr_values = [satellite["ss"] for satellite_data in data for satellite in satellite_data.get("satellites", []) if "ss" in satellite]
sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(min(snr_values), max(snr_values)))
sm.set_array([])  # An empty array to associate with the color map
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.1)
cbar.set_label("SNR")

point1 = Line2D(
    [0],
    [0],
    label="current sat position",
    marker="H",
    markersize=4,
    markerfacecolor="orange",
    markeredgecolor="black",
    linestyle="",
    markeredgewidth=0.3,
)
point2 = Line2D([0], [0], label="not used", marker="^", markersize=4, markerfacecolor="blue", linestyle="", markeredgewidth=0.3)
point3 = Line2D([0], [0], label="used", marker="o", markersize=4, markerfacecolor="blue", linestyle="", markeredgewidth=0.3)


# access legend objects automatically created from data
handles, labels = plt.gca().get_legend_handles_labels()

# add manual symbols to auto legend
handles.extend([point1, point2, point3])
plt.legend(handles=handles, bbox_to_anchor=(0.2, 0.01), prop={"size": 6}, frameon=False)


# Add current date and time outside the plotting area (bottom-left)
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
text_str = f"{points:} data samples"

footnote = f"{current_datetime:} | {text_str:}"

plt.text(0.9, 0.02, footnote, fontsize=6, family='monospace', horizontalalignment='right', transform=plt.gcf().transFigure)


# Save the plot to the specified output image file
plt.savefig(outfile, bbox_inches="tight")
