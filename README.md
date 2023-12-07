# GPS Data Visualization Script

This script reads GPS data from a JSON file generated by `gpsd` and `gpspipe`. It then generates a joint plot using Seaborn to visualize the latitude, longitude, and altitude changes. Additionally, it calculates and displays statistics on the plot.

![sample_plot](plot-lat-lon.png)

## Prerequisites

- Python 3.x
- Required Python packages: `json`, `matplotlib`, `numpy`, `seaborn`

## Usage

```bash
# get some samples from gpsd
gpspipe -v -w -n 10 > input.json
# make a plot using every 10th data point
python gpsjsonplot.py --json input.json --outfile output.png --every 10
```


-    `--json`: Path to the input JSON file containing GPS data.
-    `--outfile`: Path to the output image file where the plot will be saved.
-    `--every`: Optional parameter to select every n-th line from the input JSON file (default is 10).

## Script Overview

1.    Parses command line arguments using argparse.
1.    Reads every n-th line of JSON data from the specified file, filtering by "class":"TPV".
1.    Extracts relevant data (latitude, longitude, altitude).
1.    Calculates mean latitude and longitude.
1.    Converts latitude and longitude to meters from the mean.
1.    Calculates statistics like mean and standard deviation for altitude, latitude, and longitude.
1.    Generates a joint plot using Seaborn with a scatter plot and kernel density estimates.
1.    Displays mean location as a red cross and statistics
1.    Saves the plot as an image file.