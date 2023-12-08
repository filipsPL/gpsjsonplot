#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import matplotlib.pyplot as plt
import numpy as np

# from datetime import datetime
import seaborn as sns
import argparse

# jsonfile = "/mnt/ramdisk/tmp/tpv.json"
# plotfile = "/mnt/ramdisk/tmp/tpv.json.png"
# n = 30  # Set the value of n (read every n-th line)

# -------------------------------------------------------- #

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("--json", dest="jsonfile", required=True, help="input json file")
parser.add_argument("--outfile", dest="outfile", required=True, help="output image file")
parser.add_argument("--every", dest="every", default=10, type=int, help="select every n-th line")
parser.add_argument("--contour", dest="contour", default=6, type=int, help="number of contour lines, 0-disables")

args = parser.parse_args()
jsonfile = args.jsonfile
outfile = args.outfile
every = args.every
contour = args.contour

# -------------------------------------------------------- #

# Read JSON data from the file
with open(jsonfile, "r") as file:
    # data = [json.loads(line) for line in file]
    data = [json.loads(line) for i, line in enumerate(file) if i % every == 0 and json.loads(line).get("class") == "TPV"]

# -------------------------------------------------------- #

# Extract relevant data
latitude = [entry["lat"] for entry in data]
longitude = [entry["lon"] for entry in data]
altitude = [entry["alt"] for entry in data]

points = len(latitude)

# Calculate mean latitude and longitude
mean_latitude = np.mean(latitude)
mean_longitude = np.mean(longitude)

# Convert latitude and longitude to meters
latitude_meters = (latitude - mean_latitude) * 111000  # Approximate 1 degree = 111000 meters
longitude_meters = (longitude - mean_longitude) * 111000 * np.cos(np.radians(mean_latitude))


# mean_altitude = np.mean(altitude)
std_altitude = np.std(altitude)

std_latitude = np.std(latitude_meters)
std_longitude = np.std(longitude_meters)



# Calculate maximum absolute values for latitude and longitude
max_abs_latitude = max(np.abs(latitude_meters))
max_abs_longitude = max(np.abs(longitude_meters))

# Set explicit limits for the axes based on maximum absolute values
lim = np.ceil(max(max_abs_longitude, max_abs_latitude))


# Convert mean latitude and longitude to meters
mean_latitude_meters = 0
mean_longitude_meters = 0

# ------------------------------------------------------------------ #

# Create a joint plot with Seaborn
# sns.set(style="white", color_codes=True)
g = sns.jointplot(
    x=longitude_meters,
    y=latitude_meters,
    kind="scatter",
    color="silver",
    edgecolor="black",  # for edge color
    linewidth=0.3,
    s=10,
    xlim=(-lim, lim),
    ylim=(-lim, lim),
    height=4.6,
    ratio=4,
    marginal_kws=dict(fill=True, log_scale=False, color="silver", stat="density"),
)

g.plot_joint(sns.kdeplot, color="r", zorder=5, levels=contour)
# g.plot_marginals(sns.rugplot, color="r", height=-.15, clip_on=False)
g.plot_marginals(sns.kdeplot, color="silver", fill=True)

g.set_axis_labels("Longitude (meters from mean)", "Latitude (meters from mean)")

# Plotting mean location as a red dot
plt.scatter(0, 0, color="red", marker="x", s=100, label="Mean Location")

# Display mean and std in the top right corner
text_str = f"{points:} points. STD: alt: {std_altitude:.2f}m lat: {std_latitude:.2f}m, lon: {std_longitude:.2f}m"

plt.text(
    0.5,
    -0.18,
    text_str,
    transform=g.ax_joint.transAxes,
    verticalalignment="top",
    horizontalalignment="center",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
)

# -------------------------------------------------------- #
# Save the plot to a file
plt.savefig(outfile, bbox_inches="tight")
