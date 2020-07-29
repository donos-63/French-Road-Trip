import os, sys
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as colors
import numpy as np
from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as sql

MAP_FILE_PATH = os.path.dirname(sys.argv[0]) + os.sep + 'tmp' + os.sep +'travel_map.jpg'

plt.rcParams['figure.figsize'] = [20, 20]
np.set_printoptions(suppress=True)

db_connector = Connector()

results = db_connector.execute_query(sql.SQL_GET_FRENCH_TRIP)
waypoints = results.fetchall()


lat = []
long = []
for trip in waypoints:
        long.append(float(trip[0]))
        lat.append(float(trip[1]))        
        long.append(float(trip[2]))
        lat.append(float(trip[3]))        

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

cmap = plt.get_cmap('plasma')
new_cmap = truncate_colormap(cmap, 0.4, 0.9)

fig = plt.figure()

m = Basemap(projection='merc',
            llcrnrlat = 42,
            llcrnrlon = -5,
            urcrnrlat = 52,
            urcrnrlon = 9,
            resolution='l')

m.drawmapboundary(fill_color=[0.9,0.9,0.9])
m.fillcontinents(color='white',lake_color=[0.9,0.9,0.9],zorder=1)
m.drawcoastlines(linewidth=0.5,color=[0.15,0.15,0.15])
m.drawcountries(linewidth=1,color=[0.15,0.15,0.15])

x,y = m(lat,long)

for i in range(len(x)-1):
    col = new_cmap(i/len(x))
    x1 = [lat[i],lat[i+1]]
    y1 = [long[i],long[i+1]]
    m.drawgreatcircle(x1[0],y1[0],x1[1],y1[1],linewidth=1.5,color=col,alpha=0.8)
    
plt.scatter(x, y, c = range(len(x)), cmap=new_cmap,alpha=0.8,s=80,zorder=2)

fig.savefig(MAP_FILE_PATH)




