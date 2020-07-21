
# # Import des différentes bibliothèques 

import sys
import os   # Le module os est un module  fournit par Python dont le but d’interagir avec le système d’exploitation, il permet ainsi de gérer l’arborescence des fichiers, de fournir des informations sur le système d’exploitation processus, variables systèmes, ainsi que de nombreuses fonctionnalités du systèmes…
import csv   # Import de la fonction permettant de travailler ac des fichiers CSV (writer, reader)
import psycopg2 #provider bdd postgres
import urllib.parse as up
import collections
from zipfile import ZipFile

#Définition des chemins vers le référentiel des villes
CITY_REFERENTIAL_FOLDER = os.getcwd() + os.sep + "city_referential"  + os.sep 
CITY_REFERENTIAL_IN_PATH = CITY_REFERENTIAL_FOLDER + "city_referential.zip"
CITY_REFERENTIAL_OUT_PATH = CITY_REFERENTIAL_FOLDER + "city_referential.csv"

#dezip du référentiel de donnée pour intégration à la base de donnée
if not os.path.exists(CITY_REFERENTIAL_OUT_PATH):
    if not os.path.exists(CITY_REFERENTIAL_IN_PATH):
        print("Le fichier de référentiel des villes n'existe pas, import impossible")
        exit
    else :
        with ZipFile(CITY_REFERENTIAL_IN_PATH, 'r') as zipObj:
            zipObj.extractall(CITY_REFERENTIAL_FOLDER)
            print('Référentiel des villes extrait')


#Initialisation du provider de donnée
up.uses_netloc.append("postgres")
#todo mettre l'url dans les variables d'environnement (venv/pypi)
url = up.urlparse('postgres://herdlqqw:5GkFSWjQSp1Plap4gGnE-kX6mY7J1QB9@packy.db.elephantsql.com:5432/herdlqqw')
conn = psycopg2.connect(database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port
)

cur = conn.cursor()

# CREATION TABLES
cur.execute("SELECT to_regclass('prefecture');")
isTableExists = cur.fetchone()[0] == None

if isTableExists :
    cur.execute('''CREATE TABLE prefecture (insee_code INTEGER PRIMARY KEY, postal_code TEXT,
    city TEXT, department TEXT, region TEXT, statut TEXT, average_altitude FLOAT, area_size FLOAT,
    population FLOAT, geo_lat FLOAT, geo_long FLOAT, city_code INTEGER, canton_code INTEGER,
    district_code INTEGER, departement_code INTEGER, area_code INTEGER);''')
    print("Création de la table prefecture effectuée.")
else :
    print("La table 'prefecture' existe déjà")

cur.execute("SELECT to_regclass('journey');")
isTableExists = cur.fetchone()[0] == None

if isTableExists :
    cur.execute('''CREATE TABLE journey (insee_code_from INTEGER, isee_code_to INTEGER, co2 FLOAT, duration INTEGER);''')
    print("Création de la table journey effectuée.")
else :
    print("La table 'journey' existe déjà")

# # ## SAUVEGARDE DE LA BDD
#pas besoin sur un create
conn.commit()
#print("BDD sauvegardée.")

with open(CITY_REFERENTIAL_OUT_PATH, mode="r", encoding="utf-8") as file :
    dic = csv.DictReader(file, delimiter = ';')
    for row in dic :
        #la ville n'est pas une préfecture on passe à la ligne suivante
        if not row["Statut"].startswith("Préfecture") and not row["Statut"].startswith("Capital"): 
            continue

        #si la ville n'est pas en france métropolitaine (DOM et Corse) on passe à la ligne suivante
        if not row["Code INSEE"].isnumeric() or int(row["Code INSEE"]) >= 96000: 
            continue

        values = [ row["Code INSEE"],
                   row["Code Postal"],
                   row["Commune"],
                   row["Département"],
                   row["Région"],
                   row["Statut"],
                   row["Altitude Moyenne"],
                   row["Superficie"],
                   row["Population"],
                   row["geo_point_2d"].split(',')[0],
                   row["geo_point_2d"].split(',')[1],
                   row["Code Commune"],
                   row["Code Canton"],
                   row["Code Arrondissement"],
                   row["Code Département"],
                   row["Code Région"]
                ]

        cur.execute("""INSERT 
                        INTO prefecture (insee_code, 
                                        postal_code, 
                                        city, 
                                        department,
                                        region, 
                                        statut, 
                                        average_altitude, 
                                        area_size, 
                                        population, 
                                        geo_lat, 
                                        geo_long, 
                                        city_code, 
                                        canton_code, 
                                        district_code, 
                                        departement_code, 
                                        area_code) 
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        ;""", values)

    conn.commit()
    
    print('Base de donnée initialisée')


