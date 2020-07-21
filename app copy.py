import pandas as pd
import googlemaps
from itertools import combinations
import numpy as np
import random

""" all_waypoints = ["USS Alabama, Battleship Parkway, Mobile, AL",
                 "Grand Canyon National Park, Arizona",
                 "Toltec Mounds, Scott, AR",
                 "San Andreas Fault, San Benito County, CA",
                 "Cable Car Museum, 94108, 1201 Mason St, San Francisco, CA 94108",
                 "Pikes Peak, Colorado",
                 "The Mark Twain House & Museum, Farmington Avenue, Hartford, CT",
                 "New Castle Historic District, Delaware",
                 "White House, Pennsylvania Avenue Northwest, Washington, DC",
                 "Cape Canaveral, FL",
                 "Okefenokee Swamp Park, Okefenokee Swamp Park Road, Waycross, GA",
                 "Craters of the Moon National Monument & Preserve, Arco, ID",
                 "Lincoln Home National Historic Site Visitor Center, 426 South 7th Street, Springfield, IL",
                 "West Baden Springs Hotel, West Baden Avenue, West Baden Springs, IN",
                 "Terrace Hill, Grand Avenue, Des Moines, IA",
                 "C. W. Parker Carousel Museum, South Esplanade Street, Leavenworth, KS",
                 "Mammoth Cave National Park, Mammoth Cave Pkwy, Mammoth Cave, KY",
                 "French Quarter, New Orleans, LA",
                 "Acadia National Park, Maine",
                 "Maryland State House, 100 State Cir, Annapolis, MD 21401",
                 "USS Constitution, Boston, MA",
                 "Olympia Entertainment, Woodward Avenue, Detroit, MI",
                 "Fort Snelling, Tower Avenue, Saint Paul, MN",
                 "Vicksburg National Military Park, Clay Street, Vicksburg, MS",
                 "Gateway Arch, Washington Avenue, St Louis, MO",
                 "Glacier National Park, West Glacier, MT",
                 "Ashfall Fossil Bed, Royal, NE",
                 "Hoover Dam, NV",
                 "Omni Mount Washington Resort, Mount Washington Hotel Road, Bretton Woods, NH",
                 "Congress Hall, Congress Place, Cape May, NJ 08204",
                 "Carlsbad Caverns National Park, Carlsbad, NM",
                 "Statue of Liberty, Liberty Island, NYC, NY",
                 "Wright Brothers National Memorial Visitor Center, Manteo, NC",
                 "Fort Union Trading Post National Historic Site, Williston, North Dakota 1804, ND",
                 "Spring Grove Cemetery, Spring Grove Avenue, Cincinnati, OH",
                 "Chickasaw National Recreation Area, 1008 W 2nd St, Sulphur, OK 73086",
                 "Columbia River Gorge National Scenic Area, Oregon",
                 "Liberty Bell, 6th Street, Philadelphia, PA",
                 "The Breakers, Ochre Point Avenue, Newport, RI",
                 "Fort Sumter National Monument, Sullivan's Island, SC",
                 "Mount Rushmore National Memorial, South Dakota 244, Keystone, SD",
                 "Graceland, Elvis Presley Boulevard, Memphis, TN",
                 "The Alamo, Alamo Plaza, San Antonio, TX",
                 "Bryce Canyon National Park, Hwy 63, Bryce, UT",
                 "Shelburne Farms, Harbor Road, Shelburne, VT",
                 "Mount Vernon, Fairfax County, Virginia",
                 "Hanford Site, Benton County, WA",
                 "Lost World Caverns, Lewisburg, WV",
                 "Taliesin, County Road C, Spring Green, Wisconsin",
                 "Yellowstone National Park, WY 82190"] """
all_waypoints = ["Bourg-en-Bresse",
"Laon",
"Moulins",
"Digne-les-Bains",
"Gap",
"Nice",
"Privas",
"Charleville-Mézières",
"Foix",
"Troyes",
"Carcassonne",
"Rodez",
"Marseille",
"Caen",
"Aurillac",
"Angoulême",
"La Rochelle",
"Bourges",
"Tulle",
"Ajaccio",
"Bastia",
"Dijon",
"Saint-Brieuc",
"Guéret",
"Périgueux",
"Besançon",
"Valence",
"Évreux",
"Chartres",
"Quimper",
"Nîmes",
"Toulouse",
"Auch",
"Bordeaux",
"Montpellier",
"Rennes",
"Châteauroux",
"Tours",
"Grenoble",
"Lons-le-Saunier",
"Mont-de-Marsan",
"Blois",
"Saint-Étienne",
"Le Puy-en-Velay",
"Nantes",
"Orléans",
"Cahors",
"Agen",
"Mende",
"Angers",
"Saint-Lô",
"Châlons-en-Champagne",
"Chaumont",
"Laval",
"Nancy",
"Bar-le-Duc",
"Vannes",
"Metz",
"Nevers",
"Lille",
"Beauvais",
"Alençon",
"Arras",
"Clermont-Ferrand",
"Pau",
"Tarbes",
"Perpignan",
"Strasbourg",
"Colmar",
"Lyon",
"Vesoul",
"Mâcon",
"Le Mans",
"Chambéry",
"Annecy",
"Paris (C)",
"Rouen",
"Melun",
"Versailles",
"Niort",
"Amiens",
"Albi",
"Montauban",
"Toulon",
"Avignon",
"La Roche-sur-Yon",
"Poitiers",
"Limoges",
"Épinal",
"Auxerre",
"Belfort",
"Évry-Courcouronnes",
"Nanterre",
"Bobigny",
"Créteil",
"Cergy"]

gmaps = googlemaps.Client(key="AIzaSyDV675gkBNyn314zSeMTT0cMGxE9ju14B0")

waypoint_distances = {}
waypoint_durations = {}

for (waypoint1, waypoint2) in combinations(all_waypoints, 2):
    try:
        route = gmaps.distance_matrix(origins=[waypoint1],
                                      destinations=[waypoint2],
                                      mode="driving", # Change this to "walking" for walking directions,
                                                      # "bicycling" for biking directions, etc.
                                      language="English",
                                      units="metric")

        # "distance" is in meters
        distance = route["rows"][0]["elements"][0]["distance"]["value"]

        # "duration" is in seconds
        duration = route["rows"][0]["elements"][0]["duration"]["value"]

        waypoint_distances[frozenset([waypoint1, waypoint2])] = distance
        waypoint_durations[frozenset([waypoint1, waypoint2])] = duration
    
    except Exception as e:
        print("Error with finding the route between %s and %s." % (waypoint1, waypoint2))

with open("my-waypoints-dist-dur.tsv", "w") as out_file:
    out_file.write("\t".join(["waypoint1",
                              "waypoint2",
                              "distance_m",
                              "duration_s"]))
    
    for (waypoint1, waypoint2) in waypoint_distances.keys():
        out_file.write("\n" +
                       "\t".join([waypoint1,
                                  waypoint2,
                                  str(waypoint_distances[frozenset([waypoint1, waypoint2])]),
                                  str(waypoint_durations[frozenset([waypoint1, waypoint2])])]))

waypoint_distances = {}
waypoint_durations = {}
all_waypoints = set()

waypoint_data = pd.read_csv("my-waypoints-dist-dur.tsv", sep="\t")

for i, row in waypoint_data.iterrows():
    waypoint_distances[frozenset([row.waypoint1, row.waypoint2])] = row.distance_m
    waypoint_durations[frozenset([row.waypoint1, row.waypoint2])] = row.duration_s
    all_waypoints.update([row.waypoint1, row.waypoint2])

def compute_fitness(solution):
    """
        This function returns the total distance traveled on the current road trip.
        
        The genetic algorithm will favor road trips that have shorter
        total distances traveled.
    """
    
    solution_fitness = 0.0
    
    for index in range(len(solution)):
        waypoint1 = solution[index - 1]
        waypoint2 = solution[index]
        solution_fitness += waypoint_distances[frozenset([waypoint1, waypoint2])]
        
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
    
def run_genetic_algorithm(generations=5000, population_size=100):
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

run_genetic_algorithm(generations=5000, population_size=100)
