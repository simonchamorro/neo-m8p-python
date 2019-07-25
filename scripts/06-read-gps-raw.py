import re
import calendar
import matplotlib.pyplot as plt
import numpy as np
from geopy import distance
import tilemapbase

def read_gps(path):
    regex = r"\$GNRMC,([0-9\.]+)?,([VA]),(([0-9.]+)([0-9]{2}\.[0-9]+))?,([NS])?,(([0-9.]+)([0-9]{2}\.[0-9]+))?,([EW])?,([0-9.]+)?,([0-9.]+)?,([0-9.]+)?,([0-9.]+)?,([0-9.]+)?,(.*)?"
    time_regex = r"([0-9]+)?:([0-9]+)?:([0-9\.]+)?"
    coords = []
    with open(path, "r") as fid:
        while True:
            line = fid.readline()
            if not line:
                break
            match = re.match(regex, line.split()[-1])
            if match:
                mode = match.group(2)
                if mode == "A":
                    if match.group(6) == 'N':
                        latitude = round(float(match.group(4)) + float(match.group(5)) / 60, 8)
                    else:
                        latitude = -round(float(match.group(4)) + float(match.group(5)) / 60, 8)
                    if match.group(10) == 'E':
                        longitude = round(float(match.group(8)) + float(match.group(9)) / 60, 8)
                    else:
                        longitude = -round(float(match.group(8)) + float(match.group(9)) / 60, 8)
                    speedkm = round(float(match.group(11)), 2)
                    time = re.match(time_regex, line.split()[0])
                    timestamp = calendar.timegm((1970, 1, 1, int(time.group(1)), int(time.group(2)), float(time.group(3))))
                    print(f'gps: {latitude}, {longitude} timestamp: {timestamp}')
                    coords.append((timestamp, latitude, longitude))
                else:
                    pass
    return coords

def plot_coords(ground_truth, coords, degree_range=0.0001):
    tilemapbase.start_logging()
    tilemapbase.init(create=True)
    t = tilemapbase.tiles.build_OSM()

    degree_range = degree_range
    extent = tilemapbase.Extent.from_lonlat(ground_truth[1] - degree_range, ground_truth[1] + degree_range,
             ground_truth[0] - degree_range, ground_truth[0] + degree_range)
    extent = extent.to_aspect(1.0)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plotter = tilemapbase.Plotter(extent, t, width=600)
    plotter.plot(ax, t)
    x, y = tilemapbase.project(ground_truth[1], ground_truth[0])
    ax.scatter(x,y, marker="*", color="red", linewidth=5)
    for idx, coord in enumerate(coords):
        x, y = tilemapbase.project(coord[2], coord[1])
        ax.scatter(x,y, marker=".", c=(0, 1 - (1/len(coords))*idx, (1/len(coords))*idx), linewidth=1)
    plt.show()

def plot_error(ground_truth, coords, degree_range=0.0001):
    t = [coord[0] - coords[0][0] for coord in coords]
    lat = np.array([coord[1] for coord in coords])
    lon = np.array([coord[2] for coord in coords])
    avg_coords = [(coords[idx][0], np.mean(lat[0:idx + 1]), np.mean(lon[0:idx + 1])) for idx in range(len(coords))]
    plot_coords(ground_truth, avg_coords, degree_range)
    err = [distance.distance(ground_truth, coord[1:3]).km * 1000 for coord in avg_coords]
    plt.plot(t, err)
    plt.xlabel('time (s)')
    plt.ylabel('error of avg coords (m)')
    plt.show()


# coords = read_gps('gps_test1.txt')
# plot_coords((45.530505, -73.614722), coords)
# plot_error((45.530505, -73.614722), coords)

# coords = read_gps('gps_test2.txt')
# plot_coords((45.530693, -73.614824), coords)
# plot_error((45.530693, -73.614824), coords)

coords = read_gps('gps_test3.txt')
plot_coords((45.531104, -73.613218), coords)
plot_error((45.531104, -73.613218), coords)

coords = read_gps('gps_test4.txt')
plot_coords((45.530997, -73.613050), coords)
plot_error((45.530997, -73.613050), coords)

# coords = read_gps('block.txt')
# plot_coords((45.531308, -73.614679), coords, degree_range=0.002)

