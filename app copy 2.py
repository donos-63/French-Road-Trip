import pandas as pd
from itertools import combinations
import requests
import json
from math import trunc
from datetime import datetime, timedelta 
import re
from collections import Counter
from itertools import chain
from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as sql
import bdd_management
import algorithms


all_waypoints = None
db_connector = Connector()

#API_KEY = '6cf28a3a-59c3-4c82-8cbf-8fa5e64b01da'
API_KEY = '3fd6041b-beda-4a79-9f1a-09bc263a1dfd'
#API_KEY = 'd3f69ecb-68f5-477e-b1bb-d58208f936c5'
#API_KEY = '78cc6f8e-68d6-450d-89d0-8a085b6c5af5'
##API_KEY = 'b84ebebd-476c-4204-b195-7ffeb67043e7'
#API_KEY = 'cc3bc7b1-4c27-4176-aefd-15017c363178'
#API_KEY = '57f195e9-78a9-4fd7-a10c-312f0502d659'

API_NAVITIA = "https://api.sncf.com/v1/coverage/sncf/journeys?key={3}&from=admin:fr:{0}&to=admin:fr:{1}&datetime={2}&min_nb_journeys=10"
IS_MIN_CO2_SEARCH = True
IS_FORCE_COMPUTE = False

def datetime_str_to_datetime_str(datetime_str, fromFormat="%Y%m%dT%H%M%S", toFormat="%d/%m/%Y à %H:%M"):
    date_time = datetime.strptime(datetime_str, fromFormat)
    return date_time.strftime(toFormat)

def store_section(description, geo_point_from, geo_point_to, section_type, duration=None, co2=None):
    indentation = ''
    if section_type == 'DELAY' or section_type == 'SUB_SECTION':
        indentation = '     -> '

    print(indentation + description)
    db_connector.execute_nonquery(sql.SQL_INSERT_FRENCH_TRIP_SECTION, [
                                  geo_point_from, geo_point_to, description, section_type, duration, co2])

def save_trip_section(from_city_insee, to_city_insee, best_travel):

    from_city_name = all_waypoints.loc[all_waypoints[0]
                                       == from_city_insee].values[0][2]
    to_city_name = all_waypoints.loc[all_waypoints[0]
                                     == to_city_insee].values[0][2]
    from_city_gps = all_waypoints.loc[all_waypoints[0]
                                      == to_city_insee].values[0][3]
    to_city_gps = all_waypoints.loc[all_waypoints[0]
                                    == to_city_insee].values[0][3]

    store_section('Voyage de {} à {}. Départ le {} - Arrivée le {} après {} transferts '.format(from_city_name, to_city_name, datetime_str_to_datetime_str(best_travel['departure_date_time']), datetime_str_to_datetime_str(best_travel['arrival_date_time']), best_travel['nb_transfers']),
                  None,
                  None,
                  'SECTION',
                  best_travel['duration'],
                  best_travel['co2_emission']["value"]
                  )

    for section in best_travel['sections']:
        if 'from' in section:
            if not section['type'] == 'crow_fly':
                # vilaine faute d'orthographe sur transfer_type
                if not 'transfer_type' in section or not section['transfer_type'] == 'walking':
                    store_section('{} - {} ({})'.format(section['from']['name'], section['to']['name'], section['display_informations']['physical_mode']),
                                  from_city_gps,
                                  to_city_gps,
                                  'SUB_SECTION')
            # else : initiale section, not used
        else:
            store_section('Waiting {} minutes'.format(section['duration']/60),
                          None,
                          None,
                          'DELAY')

waypoint_co2 = {}
waypoint_durations = {}

# get all prefectures referential
results = db_connector.execute_query(sql.SQL_GET_ALL_PREFECTURE)
all_waypoints = pd.DataFrame(results.fetchall())

# Vérification si les trajets péfecture à préfecture ont été déjà calculés
saved_waypoints = db_connector.execute_query(sql.SQL_GET_WAYPOINTS)

# Dans le précalcul du trajet optimal, utilisation de la date courante
travel_date = datetime.now().strftime("%Y%m%dT%H%M%S")
bad_waypoints = []

if saved_waypoints.rowcount > 0 and not IS_FORCE_COMPUTE:
    print("le référentiel des voyage existe déjà")
else:
    bdd_management.truncate_journey()

    for (from_city, to_city) in combinations(all_waypoints[0].values, 2):
        try:
            if int(from_city) in bad_waypoints or int(to_city) in bad_waypoints:
                continue

            route = requests.get(API_NAVITIA.format(
                int(from_city), int(to_city), travel_date, API_KEY))
            response = json.loads(route.text)

            mid_duration = 0
            mid_co2 = 0
            for journey in response["journeys"]:
                mid_duration += journey["duration"]
                mid_co2 += journey["co2_emission"]["value"]

            waypoint_co2[frozenset([from_city, to_city])
                         ] = mid_co2/len(response["journeys"])
            waypoint_durations[frozenset(
                [from_city, to_city])] = mid_duration/len(response["journeys"])

        except Exception as e:
            print("Error with finding the route between %s and %s : %s" %
                  (from_city, to_city, response["error"]["message"]))
            if 'no destination point' == response["error"]["message"]:
                bad_waypoints.append(int(to_city))

            if 'no origin point' == response["error"]["message"]:
                bad_waypoints.append(int(from_city))

            for bad_insee_code in re.findall('The entry point: admin:fr:([0-9]+) is not valid', response["error"]["message"]):
                if not int(bad_insee_code) in bad_waypoints:
                    bad_waypoints.append(int(bad_insee_code))

    # Enregistrement des trajets point à point (préfecture à préfecture)
    for (waypoint1, waypoint2) in waypoint_co2.keys():
        waypoint = [waypoint1,
                    waypoint2,
                    str(waypoint_co2[frozenset([waypoint1, waypoint2])]),
                    str(int(waypoint_durations[frozenset([waypoint1, waypoint2])]))]
        db_connector.execute_nonquery(sql.SQL_INSERT_WAYPOINT, waypoint)

    # commit trajets unitaires dans la bdd
    db_connector.commit()

    # enregistrement des préfectures non trouvée (pas de gare)
    print(bad_waypoints)
    for bad_city in bad_waypoints:
        db_connector.execute_nonquery(
            sql.SQL_INSERT_CITY_WITHOUT_STATION, str(bad_city))
    db_connector.commit()

waypoint_co2 = {}
waypoint_durations = {}
processed_waypoints = set()

waypoints = db_connector.execute_query(sql.SQL_GET_WAYPOINTS)

for row in waypoints:
    waypoint_co2[frozenset([int(row[0]), int(row[1])])] = row[2]
    waypoint_durations[frozenset([int(row[0]), int(row[1])])] = row[3]
    processed_waypoints.update([row[0], row[1]])

travel_results = algorithms.run_genetic_algorithm(waypoints = list(processed_waypoints))

# take most represented trip order
journey_groups = Counter(chain(*travel_results))
top_journeys = journey_groups.most_common(1)[0][0]

print('Le voyage le plus représentatif est :')
print(top_journeys)
travel_date = datetime.now().strftime("%Y%m%dT%H%M%S")
# calcul des horaires de voyage réels pour le trajet le plus optimisé
#date de début du voyage
trip_date = "20200730T152506"

print('Départ du calcul du voyage le %s' %
      (datetime_str_to_datetime_str(travel_date)))

#vidage de la table contenant les informations du voyage
bdd_management.truncate_roadtrip()

for i in range(len(top_journeys)-1):
    try:
        from_city_insee = top_journeys[i]
        to_city_insee = top_journeys[i+1]
        route = requests.get(API_NAVITIA.format(
            int(from_city_insee), int(to_city_insee), travel_date, API_KEY))
        travels = json.loads(route.text)

        # Contrôle des voyage reçus pour identifier le plus adapté à recherche
        best_travel = travels["journeys"][0]
        for travel in travels["journeys"]:
            if IS_MIN_CO2_SEARCH and float(best_travel['co2_emission']['value']) > float(travel['co2_emission']['value']):
                best_travel = travel
            elif best_travel['arrival_date_time'] > travel['arrival_date_time']:
                best_travel = travel

        # sauvegarde du trajet 'i' en base
        save_trip_section(from_city_insee, to_city_insee, best_travel)

        # le prochain trajet devra avoir une date de départ > à la date de ce trajet
        travel_date = best_travel['arrival_date_time']

    except Exception as e:
        print("!!  Fail to compute travel between '%s' and '%s'" %
              (from_city_insee, to_city_insee))

db_connector.commit()

resume = db_connector.execute_query(sql.SQL_GET_C02_CONSUMPTION_RESUME)
resume = resume.fetchone()

resume_description = """Début du voyage le {} . Arrivée le {}. 
                    Le voyage à durée {} pour un total de {:d} kgeC""".format(
                                                            datetime_str_to_datetime_str(start_date),
                                                            datetime_str_to_datetime_str(travel_date),
                                                            str(timedelta(seconds=resume[0])) ,
                                                            trunc( resume[1]/1000))

store_section(resume_description, None, None, 'INFO', resume[0], resume[1])

db_connector.commit()

print('Travel complete. Have  nive trip!!!')
