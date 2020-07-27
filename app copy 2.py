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

all_waypoints = []
db_connector = Connector()

#API_KEY = '6cf28a3a-59c3-4c82-8cbf-8fa5e64b01da'
API_KEY = '3fd6041b-beda-4a79-9f1a-09bc263a1dfd'

API_NAVITIA = "https://api.sncf.com/v1/coverage/sncf/journeys?key={3}&from=admin:fr:{0}&to=admin:fr:{1}&datetime={2}&min_nb_journeys=10"
DURATION_SEARCH = "DURATION_SEARCH"
CO2_SEARCH = "CO2_SEARCH"
travel_results = []
start_date = "20200730T152506"

def datetime_str_to_datetime_str(datetime_str, fromFormat, toFormat):
    date_time = datetime.strptime(datetime_str, fromFormat)
    return date_time.strftime(toFormat)  

def compute_fitness(solution, search_type):
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
    
    new_random_agent = list(all_waypoints)
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

            population_fitness[agent_genome] = compute_fitness(agent_genome, DURATION_SEARCH)

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

saved_waypoints = db_connector.execute_query('SELECT count(*) FROM journey')

saved_waypoints.fetchall()
# if not len(saved_waypoints.fetchall()) == 0:
if True == False:
    print("le référentiel des voyage existe déjà")
else :
    results = db_connector.execute_query(sql.SQL_GET_ALL_PREFECTURE)
    all_waypoints = results.fetchall()

    for (waypoint1, waypoint2) in combinations(all_waypoints, 2):
        try:
            from_city = waypoint1[0]
            to_city = waypoint2[0]
            route = requests.get(API_NAVITIA.format(from_city, to_city, "20200730T152506", API_KEY))
            response = json.loads(route.text)

            mid_duration = 0
            mid_co2 = 0
            for journey in response["journeys"]:
                mid_duration += journey["duration"]
                mid_co2 += journey["co2_emission"]["value"]

            waypoint_co2[frozenset([from_city, to_city])] = mid_co2/len(response["journeys"])
            waypoint_durations[frozenset([from_city, to_city])] = mid_duration/len(response["journeys"])
        
        except Exception as e:
            print("Error with finding the route between %s and %s." % (from_city, to_city))
            db_connector.execute_query(sql.SQL_INSERT_CITY_WITHOUT_STATION, [from_city, to_city, 0 ])

    #Enregistrement des trajets point à point
    for (waypoint1, waypoint2) in waypoint_co2.keys():
        waypoint = [waypoint1,
                    waypoint2,
                    str(waypoint_co2[frozenset([waypoint1, waypoint2])]),
                    str(int(waypoint_durations[frozenset([waypoint1, waypoint2])]))]
        db_connector.execute_nonquery(sql.SQL_INSERT_WAYPOINT, waypoint)
    
    #commit voyage dans la bdd
    db_connector.commit()

waypoint_co2 = {}
waypoint_durations = {}
all_waypoints = set()

waypoints = db_connector.execute_query(sql.SQL_GET_WAYPOINTS)

for row in waypoints:
    waypoint_co2[frozenset([int(row[0]), int(row[1])])] = row[2]
    waypoint_durations[frozenset([int(row[0]), int(row[1])])] = row[3]
    all_waypoints.update([row[0], row[1]])

run_genetic_algorithm()

#take most represented travel
journey_groups = Counter(chain(*travel_results))
top_journeys = journey_groups.most_common(1)[0][0]

print(top_journeys)

#calcul des horaires de voyage réels pour le trajet le plus optimisé 
travels = []
trip_date = start_date
top_journeys = top_journeys
travel_date = datetime.now().strftime("%Y%m%dT%H%M%S")
print('Départ du calcul du voyage à %s' % (datetime_str_to_datetime_str(travel_date,"%Y%m%dT%H%M%S", "%H:%M:%S-%d/%Y/%m")))

for i in range(len(top_journeys)-1):
#for journey in top_journeys:
    from_city = top_journeys[i]
    to_city = top_journeys[i+1]
    route = requests.get(API_NAVITIA.format( from_city, to_city, travel_date, API_KEY))
    best_travel = json.loads(route.text)[0]

    print('Voyage de %s à %s. Départ à %s ' % ( from_city, to_city, datetime_str_to_datetime_str(best_travel['departure_date_time'], "%Y%m%dT%H%M%S", "%H:%M:%S-%d/%Y/%m")) )
    print('Arrivé à %s après %s transferts' % ( datetime_str_to_datetime_str(best_travel['arrival_date_time'], "%Y%m%dT%H%M%S", "%H:%M:%S-%d/%Y/%m"), best_travel['nb_transfers']))

    for section in best_travel['sections']:
        if 'from' in section:
            if not section['type'] == 'crow_fly':
                if not 'transfer_type' in section or not section['transfer_type'] == 'walking': #vilaine faute d'orthographe sur transfer_type
                    print('       -> %s - %s (%s)' % (section['from']['name'], section['to']['name'], section['display_informations']['physical_mode']))
            #else : initiale section, not used
        else:
            print('       -> Waiting %s minutes' % (section['duration']/60))

    travel_date = best_travel['arrival_date_time']
        
