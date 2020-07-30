import os
import sys
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as colors
import numpy as np
from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as sql

MAP_FILE_PATH = os.path.dirname(
    sys.argv[0]) + os.sep + 'tmp' + os.sep + 'travel_map.jpg'


def generate_visualization():
    """generate map from road trips data

    Returns:
        generate map in ./tmp/travel_map.jpg
    """

    plt.rcParams['figure.figsize'] = [20, 20]
    np.set_printoptions(suppress=True)

    # récupération des données du voyage
    db_connector = Connector()
    with db_connector:
        results = db_connector.execute_query(sql.SQL_GET_FRENCH_TRIP)
        waypoints = results.fetchall()

    lat = []
    long = []
    for trip in waypoints:
        long.append(float(trip[0]))
        lat.append(float(trip[1]))
        long.append(float(trip[2]))
        lat.append(float(trip[3]))

    # defini le layer couleur de la map
    cmap = plt.get_cmap('plasma')
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=0.4, b=0.9),
        cmap(np.linspace(0.4, 0.9, 100)))

    fig = plt.figure()

    # instanciation du générateur de carte, centré sur la france
    m = Basemap(projection='merc',
                llcrnrlat=42,
                llcrnrlon=-5,
                urcrnrlat=52,
                urcrnrlon=9,
                resolution='l')

    # définition des couleurs de la carte (mer, terre, bordure)
    m.drawmapboundary(fill_color=[0.9, 0.9, 0.9])
    m.fillcontinents(color='white', lake_color=[0.9, 0.9, 0.9], zorder=1)
    m.drawcoastlines(linewidth=0.5, color=[0.15, 0.15, 0.15])
    m.drawcountries(linewidth=1, color=[0.15, 0.15, 0.15])

    x, y = m(lat, long)

    for i in range(len(x)-1):
        col = new_cmap(i/len(x))
        x1 = [lat[i], lat[i+1]]
        y1 = [long[i], long[i+1]]
        m.drawgreatcircle(x1[0], y1[0], x1[1], y1[1],
                          linewidth=1.5, color=col, alpha=0.8)

    plt.scatter(x, y, c=range(len(x)), cmap=new_cmap,
                alpha=0.8, s=80, zorder=2)

    fig.savefig(MAP_FILE_PATH)

