from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as sql
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

pd.set_option("max.columns", 30)

print("Available Pandas Datasets", gpd.datasets.available)

db_connector = Connector()

results = db_connector.execute_query(sql.SQL_GET_FRENCH_TRIP)
waypoints = results.fetchall()
fig = go.Figure()

all_waypoints = pd.DataFrame(results.fetchall())

source_to_dest = zip(all_waypoints[0].values,all_waypoints[2].values,
                     all_waypoints[1].values, all_waypoints[3].values,
                     all_waypoints[4])


## Loop thorugh each flight entry to add line between source and destination
for slat,dlat, slon, dlon, description in source_to_dest:
    fig.add_trace(go.Scattergeo(
                        lat = [slat,dlat],
                        lon = [slon, dlon],
                        mode = 'lines',
                        line = description
                        ))

## Logic to create labels of source and destination cities of flights
cities = brazil_cnt_df["Cidade.Origem"].values.tolist()+brazil_cnt_df["Cidade.Destino"].values.tolist()
countries = brazil_cnt_df["Pais.Origem"].values.tolist()+brazil_cnt_df["Pais.Destino"].values.tolist()
scatter_hover_data = [country + " : "+ city for city, country in zip(cities, countries)]

## Loop thorugh each flight entry to plot source and destination as points.
fig.add_trace(
    go.Scattergeo(
                lon = brazil_cnt_df["LongOrig"].values.tolist()+brazil_cnt_df["LongDest"].values.tolist(),
                lat = brazil_cnt_df["LatOrig"].values.tolist()+brazil_cnt_df["LatDest"].values.tolist(),
                hoverinfo = 'text',
                text = scatter_hover_data,
                mode = 'markers',
                marker = dict(size = 10, color = 'orangered', opacity=0.1,))
    )

## Update graph layout to improve graph styling.
fig.update_layout(
                  height=500, width=800, margin={"t":0,"b":0,"l":0, "r":0, "pad":0},
                  showlegend=False,
                  title_text = 'Connection Map Depicting Flights between Cities of Brazil',
                  geo = dict(projection_type = 'natural earth',scope = 'south america'),
                )

fig.show()







print('toto')