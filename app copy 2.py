import pandas as pd
import googlemaps
from itertools import combinations
import numpy as np
import random
import requests
import json
from collections import Counter 
from itertools import chain 
from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as sql
from datetime import datetime
import re

all_waypoints = None
db_connector = Connector()

#API_KEY = '6cf28a3a-59c3-4c82-8cbf-8fa5e64b01da'
#API_KEY = '3fd6041b-beda-4a79-9f1a-09bc263a1dfd'
#API_KEY = 'd3f69ecb-68f5-477e-b1bb-d58208f936c5'
#API_KEY = '78cc6f8e-68d6-450d-89d0-8a085b6c5af5'
##API_KEY = 'b84ebebd-476c-4204-b195-7ffeb67043e7'
#API_KEY = 'cc3bc7b1-4c27-4176-aefd-15017c363178'
API_KEY = '57f195e9-78a9-4fd7-a10c-312f0502d659'

API_NAVITIA = "https://api.sncf.com/v1/coverage/sncf/journeys?key={3}&from=admin:fr:{0}&to=admin:fr:{1}&datetime={2}&min_nb_journeys=10"
DURATION_SEARCH = "DURATION_SEARCH"
CO2_SEARCH = "CO2_SEARCH"
travel_results = []
start_date = "20200730T152506"

def datetime_str_to_datetime_str(datetime_str, fromFormat, toFormat):
    date_time = datetime.strptime(datetime_str, fromFormat)
    return date_time.strftime(toFormat)  

def compute_fitness(solution):
    """
        This function returns the total distance traveled on the current road trip.
        
        The genetic algorithm will favor road trips that have shorter
        total distances traveled.
    """
    
    solution_fitness = 0.0
    
    for index in range(len(solution)):
        waypoint1 = int(solution[index - 1])
        waypoint2 = int(solution[index])
        
        try:
            if search_type == CO2_SEARCH:
                waypoints = waypoint_co2[frozenset([waypoint1, waypoint2])]
                solution_fitness += waypoint_co2[waypoints]
            else:
                waypoints = waypoint_durations[frozenset([waypoint1, waypoint2])]
                solution_fitness += waypoint_durations[waypoints]
        except:
            print("tuple not found '{0}' & '{1}'".format(waypoint1, waypoint2))
       
    return solution_fitness

def generate_random_agent():
    """
        Creates a random road trip from the waypoints.
    """
    
    new_random_agent = list(processed_waypoints)
    random.shuffle(new_random_agent)
    return tuple(new_random_agent)

def mutate_agent(agent_genome, max_mutations=3):
    """
        Applies 1 - `max_mutations` point mutations to the given road trip.
        
        A point mutation swaps the order of two waypoints in the road trip.
    """
    
    agent_genome = list(agent_genome)
    num_mutations = random.randint(1, max_mutations)
    
    for mutation in range(num_mutations):
        swap_index1 = random.randint(0, len(agent_genome) - 1)
        swap_index2 = swap_index1

        while swap_index1 == swap_index2:
            swap_index2 = random.randint(0, len(agent_genome) - 1)

        agent_genome[swap_index1], agent_genome[swap_index2] = agent_genome[swap_index2], agent_genome[swap_index1]
            
    return tuple(agent_genome)

def shuffle_mutation(agent_genome):
    """
        Applies a single shuffle mutation to the given road trip.
        
        A shuffle mutation takes a random sub-section of the road trip
        and moves it to another location in the road trip.
    """
    
    agent_genome = list(agent_genome)
    
    start_index = random.randint(0, len(agent_genome) - 1)
    length = random.randint(2, 20)
    
    genome_subset = agent_genome[start_index:start_index + length]
    agent_genome = agent_genome[:start_index] + agent_genome[start_index + length:]
 
    insert_index = random.randint(0, len(agent_genome) + len(genome_subset) - 1)
    agent_genome = agent_genome[:insert_index] + genome_subset + agent_genome[insert_index:]
    
    return tuple(agent_genome)

def generate_random_population(pop_size):
    """
        Generates a list with `pop_size` number of random road trips.
    """
    
    random_population = []
    for agent in range(pop_size):
        random_population.append(generate_random_agent())
    return random_population
    
def run_genetic_algorithm(generations=50, population_size=10):
    """
        The core of the Genetic Algorithm.
        
        `generations` and `population_size` must be a multiple of 10.
    """
    
    population_subset_size = int(population_size / 10.)
    generations_10pct = int(generations / 10.)
    
    # Create a random population of `population_size` number of solutions.
    population = generate_random_population(population_size)

    # For `generations` number of repetitions...
    for generation in range(generations):
        
        # Compute the fitness of the entire current population
        population_fitness = {}

        for agent_genome in population:
            if agent_genome in population_fitness:
                continue

            population_fitness[agent_genome] = compute_fitness(agent_genome)

        # Take the top 10% shortest road trips and produce offspring each from them
        new_population = []
        for rank, agent_genome in enumerate(sorted(population_fitness,
                                                   key=population_fitness.get)[:population_subset_size]):
            
            if (generation % generations_10pct == 0 or generation == generations - 1) and rank == 0:
                print("Generation %d best: %d | Unique genomes: %d" % (generation,
                                                                       population_fitness[agent_genome],
                                                                       len(population_fitness)))
                print(agent_genome)
                u = []
                u.append(agent_genome)
                travel_results.append(u)
                print("")

            # Create 1 exact copy of each of the top road trips
            new_population.append(agent_genome)

            # Create 2 offspring with 1-3 point mutations
            for offspring in range(2):
                new_population.append(mutate_agent(agent_genome, 3))
                
            # Create 7 offspring with a single shuffle mutation
            for offspring in range(7):
                new_population.append(shuffle_mutation(agent_genome))

        # Replace the old population with the new population of offspring 
        for i in range(len(population))[::-1]:
            del population[i]

        population = new_population

waypoint_co2 = {}
waypoint_durations = {}
search_type = DURATION_SEARCH

#get all prefectures referential
results = db_connector.execute_query(sql.SQL_GET_ALL_PREFECTURE)
all_waypoints = pd.DataFrame(results.fetchall())

#check if journeys are already computed
saved_waypoints = db_connector.execute_query('SELECT count(*) FROM journey')

travel_date = datetime.now().strftime("%Y%m%dT%H%M%S")

bad_waypoints = []
saved_waypoints.fetchall()
# if not len(saved_waypoints.fetchall()) == 0:
if True == False:
    print("le référentiel des voyage existe déjà")
else :
    k = 0 #todo : à supprimer
    for (from_city, to_city) in combinations(all_waypoints[0].values, 2):
        try:
            k = k + 1
            print(k)

            if int(from_city) in bad_waypoints or int(to_city) in bad_waypoints:
                continue

            route = requests.get(API_NAVITIA.format(int(from_city), int(to_city), travel_date, API_KEY))
            response = json.loads(route.text)

            mid_duration = 0
            mid_co2 = 0
            for journey in response["journeys"]:
                mid_duration += journey["duration"]
                mid_co2 += journey["co2_emission"]["value"]

            waypoint_co2[frozenset([from_city, to_city])] = mid_co2/len(response["journeys"])
            waypoint_durations[frozenset([from_city, to_city])] = mid_duration/len(response["journeys"])
        
        except Exception as e:
            print("Error with finding the route between %s and %s : %s" % (from_city, to_city, response["error"]["message"]))
            if 'no destination point' == response["error"]["message"]:
         #       db_connector.execute_nonquery(sql.SQL_INSERT_CITY_WITHOUT_STATION, [to_city])
                bad_waypoints.append(int(to_city))
            
            if 'no origin point' == response["error"]["message"]:
         #       db_connector.execute_nonquery(sql.SQL_INSERT_CITY_WITHOUT_STATION, [from_city])
                bad_waypoints.append(int(from_city))
            
            for bad_insee_code in re.findall('The entry point: admin:fr:([0-9]+) is not valid', response["error"]["message"]):
                if not int(bad_insee_code) in bad_waypoints:
         #           db_connector.execute_nonquery(sql.SQL_INSERT_CITY_WITHOUT_STATION, [bad_insee_code])
                    bad_waypoints.append(int(bad_insee_code))

    #Enregistrement des trajets point à point
    for (waypoint1, waypoint2) in waypoint_co2.keys():
        waypoint = [waypoint1,
                    waypoint2,
                    str(waypoint_co2[frozenset([waypoint1, waypoint2])]),
                    str(int(waypoint_durations[frozenset([waypoint1, waypoint2])]))]
        db_connector.execute_nonquery(sql.SQL_INSERT_WAYPOINT, waypoint)
    
    #commit voyage dans la bdd
    db_connector.commit()

    #enregistrement des préfectures non référencées (pas de gare)
    print(bad_waypoints)
    for bad_city in bad_waypoints:
        db_connector.execute_nonquery(sql.SQL_INSERT_CITY_WITHOUT_STATION, bad_city)
    db_connector.commit()

def store_section(description, geo_point_from, geo_point_to, section_type, duration = None, co2 = None):
    indentation = ''
    if section_type == 'DELAY' or section_type == 'SUB_SECTION':
        indentation = '     -> '

    print(indentation + description)
    db_connector.execute_nonquery(sql.SQL_INSERT_FRENCH_TRIP_SECTION, [geo_point_from, geo_point_to, description, section_type, duration, co2  ] )

def save_trip_section(from_city_insee, to_city_insee, best_travel):
    
    from_city_name =  all_waypoints.loc[all_waypoints[0] == from_city_insee].values[0][2]
    to_city_name =  all_waypoints.loc[all_waypoints[0] == to_city_insee].values[0][2]
    from_city_gps =  all_waypoints.loc[all_waypoints[0] == to_city_insee].values[0][3]
    to_city_gps =  all_waypoints.loc[all_waypoints[0] == to_city_insee].values[0][3]

    store_section('Voyage de {} à {}. Départ à {} - Arrivée à {} après {} transferts '.format( from_city_name, to_city_name, datetime_str_to_datetime_str(best_travel['departure_date_time'], "%Y%m%dT%H%M%S", "%H:%M:%S-%d/%Y/%m"), datetime_str_to_datetime_str(best_travel['arrival_date_time'], "%Y%m%dT%H%M%S", "%H:%M:%S-%d/%Y/%m"), best_travel['nb_transfers']),
                    None,
                    None, 
                    'SECTION', 
                    best_travel['duration'],
                    best_travel['co2_emission']["value"]
                    )

    for section in best_travel['sections']:
        if 'from' in section:
            if not section['type'] == 'crow_fly':
                if not 'transfer_type' in section or not section['transfer_type'] == 'walking': #vilaine faute d'orthographe sur transfer_type
                    store_section('{} - {} ({})'.format(section['from']['name'], section['to']['name'], section['display_informations']['physical_mode']),
                                    from_city_gps,
                                    to_city_gps, 
                                    'SUB_SECTION')
            #else : initiale section, not used
        else:
            store_section('Waiting {} minutes'.format(section['duration']/60),
                            None,
                            None, 
                            'DELAY')

waypoint_co2 = {}
waypoint_durations = {}
processed_waypoints = set()

waypoints = db_connector.execute_query(sql.SQL_GET_WAYPOINTS)

for row in waypoints:
    waypoint_co2[frozenset([int(row[0]), int(row[1])])] = row[2]
    waypoint_durations[frozenset([int(row[0]), int(row[1])])] = row[3]
    processed_waypoints.update([row[0], row[1]])

run_genetic_algorithm()

#take most represented travel
journey_groups = Counter(chain(*travel_results))
top_journeys = journey_groups.most_common(1)[0][0]

print(top_journeys)
travel_date = datetime.now().strftime("%Y%m%dT%H%M%S")
#calcul des horaires de voyage réels pour le trajet le plus optimisé 
trip_date = start_date
top_journeys = top_journeys
print('Départ du calcul du voyage à %s' % (datetime_str_to_datetime_str(travel_date,"%Y%m%dT%H%M%S", "%H:%M:%S-%d/%m/%Y")))

db_connector.execute_nonquery(sql.SQL_REINIT_FRENCH_TRIP)
for i in range(len(top_journeys)-1):
#for journey in top_journeys:
    from_city_insee = top_journeys[i]
    to_city_insee = top_journeys[i+1]
    route = requests.get(API_NAVITIA.format( from_city_insee, to_city_insee, travel_date, API_KEY))
    travels = json.loads(route.text)

    best_travel = travels["journeys"][0] 
    for travel in travels["journeys"]:
        if search_type == CO2_SEARCH and float(best_travel['co2_emission']['value']) > float(travel['co2_emission']['value']):
            best_travel = travel
        elif  best_travel['arrival_date_time'] > travel['arrival_date_time']:
                best_travel = travel

    save_trip_section(from_city_insee, to_city_insee, best_travel)

    travel_date = best_travel['arrival_date_time']

db_connector.commit()

resume = db_connector.execute_query(sql.SQL_GET_C02_CONSUMPTION_RESUME)
resume = resume.fetchone()
db_connector.execute_nonquery(sql.SQL_INSERT_FRENCH_TRIP_SECTION, [None, None, 'Trip completed', 'INFO', resume[0], resume[1]  ] )

print('Travel complete. Have  nive trip!!!')

        
