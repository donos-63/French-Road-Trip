import pandas as pd
import googlemaps
from itertools import combinations
import numpy as np
import random
import requests
import json
from collections import Counter 
from itertools import chain 


# [
# "3.61132640921;45.9381159052",
# "5.30407617795;44.7264116116",
# "3.9261116009;45.655161946",
# "4.8419319446;45.8220411914",
# "0.376581458211;48.4602912292",
# "6.98580589371;47.7919119213",
# "1.40684415026;49.3574004646",
# "6.78443520767;48.6300704003",
# "0.88757317848;47.7861085409",
# "2.94370342447;47.4543629223",
# "1.51011696561;48.5606379303",
# "3.93440126624;48.9038402772",
# "0.201372876533;43.281097408"
# ]

all_waypoints = ["16015",
"15014",
"24322",
"93008",
"38185",
"26362",
"95500",
"37261",
"01053",
"32013",
"12202",
"22278",
"40192",
"53130",
"72181",
"19272",
"05061",
"82121",
"28085",
"60057"
# "85191",
# "84007",
# "27229",
# "30189",
# "66136",
# "91228",
# "43157",
# "07186",
# "74010",
# "36044",
# "64445",
# "75101",
# "88160",
# "55029",
# "06088",
# "52121",
# "08105",
# "79191",
# "56260",
# "54395",
# "50502",
# "10387",
# "68066",
# "23096",
# "29232",
# "90010",
# "78646",
# "11069",
# "39300",
# "42218",
# "70550",
# "46042",
# "49007",
# "58194",
# "02408",
# "65440",
# "47001",
# "81004",
# "41018",
# "94028",
# "77288",
# "48095",
# "73065",
# "03190",
# "18033",
# "62041",
# "17300",
# "89024",
# "92050",
# "71270",
# "83137",
# "61001",
# "09122",
# "04070"
]

API_NAVITIA = "https://api.sncf.com/v1/coverage/sncf/journeys?key=6cf28a3a-59c3-4c82-8cbf-8fa5e64b01da&from=admin:fr:{0}&to=admin:fr:{1}&datetime={2}&min_nb_journeys=10"
DURATION_SEARCH = "DURATION_SEARCH"
CO2_SEARCH = "CO2_SEARCH"
travel_results = []

#gmaps = googlemaps.Client(key="AIzaSyDV675gkBNyn314zSeMTT0cMGxE9ju14B0")

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
                travel_results.append(list(tuple(agent_genome)))
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

for (waypoint1, waypoint2) in combinations(all_waypoints, 2):
    try:

        route = requests.get(API_NAVITIA.format(waypoint1, waypoint2, "20200730T152506"))

        """ route = gmaps.distance_matrix(origins=[waypoint1],
                                      destinations=[waypoint2],
                                      mode="driving", # Change this to "walking" for walking directions,
                                                      # "bicycling" for biking directions, etc.
                                      language="English",
                                      units="metric")
        """

        response = json.loads(route.text)

        mid_duration = 0
        mid_co2 = 0
        for journey in response["journeys"]:
            mid_duration += journey["duration"]
            mid_co2 += journey["co2_emission"]["value"]

        waypoint_co2[frozenset([waypoint1, waypoint2])] = mid_co2/len(response["journeys"])
        waypoint_durations[frozenset([waypoint1, waypoint2])] = mid_duration/len(response["journeys"])
    
    except Exception as e:
        print("Error with finding the route between %s and %s." % (waypoint1, waypoint2))

with open("my-waypoints-dist-dur.tsv", "w") as out_file:
    out_file.write("\t".join(["waypoint1",
                              "waypoint2",
                              "co2_gEC",
                              "duration_s"]))
    
    for (waypoint1, waypoint2) in waypoint_co2.keys():
        out_file.write("\n" +
                       "\t".join([waypoint1,
                                  waypoint2,
                                  str(waypoint_co2[frozenset([waypoint1, waypoint2])]),
                                  str(waypoint_durations[frozenset([waypoint1, waypoint2])])]))

waypoint_co2 = {}
waypoint_durations = {}
all_waypoints = set()

waypoint_data = pd.read_csv("my-waypoints-dist-dur.tsv", sep="\t")

for i, row in waypoint_data.iterrows():
    waypoint_co2[frozenset([int(row.waypoint1), int(row.waypoint2)])] = row.co2_gEC
    waypoint_durations[frozenset([int(row.waypoint1), int(row.waypoint2)])] = row.duration_s
    all_waypoints.update([row.waypoint1, row.waypoint2])

run_genetic_algorithm()

(unique, counts) = np.unique(travel_results, return_counts=True)
Alist = [[('Mon', 'Wed')], [('Mon')], [('Tue')],[('Mon', 'Wed')] ]
v = Counter(chain(*Alist))
print(unique)
print(v)
