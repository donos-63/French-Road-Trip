
# # Import des différentes bibliothèques 

import sys
import os   # Le module os est un module  fournit par Python dont le but d’interagir avec le système d’exploitation, il permet ainsi de gérer l’arborescence des fichiers, de fournir des informations sur le système d’exploitation processus, variables systèmes, ainsi que de nombreuses fonctionnalités du systèmes…
import csv   # Import de la fonction permettant de travailler ac des fichiers CSV (writer, reader)
import psycopg2 #provider bdd postgres
import urllib.parse as up
import collections
from zipfile import ZipFile
from DatabaseAccess.Connector import Connector
import DatabaseAccess.sql_requests as requests

db_connector = Connector()

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

# CREATION TABLES
result = db_connector.execute_query("SELECT to_regclass('prefecture');")

if result.fetchone()[0] == None :
    db_connector.execute_nonquery(requests.SQL_CREATE_TABLE_PREFECTURE)
    print("Création de la table prefecture effectuée.")
else :
    print("La table 'prefecture' existe déjà")

result = db_connector.execute_query("SELECT to_regclass('journey');")

if result.fetchone()[0] == None :
    db_connector.execute_nonquery(requests.SQL_CREATE_TABLE_JOURNEY)
    print("Création de la table journey effectuée.")
else :
    print("La table 'journey' existe déjà")

# CREATION TABLES
result = db_connector.execute_query("SELECT to_regclass('substitute');")

if result.fetchone()[0] == None :
    db_connector.execute_nonquery(requests.SQL_CREATE_TABLE_SUBSTITUTE)
    print("Création de la table substitute effectuée.")
else :
    print("La table 'substitute' existe déjà")


# # ## SAUVEGARDE DE LA BDD
#pas besoin sur un create
db_connector.commit()
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

        db_connector.execute_nonquery(requests.SQL_INSERT_PREFECTURE, values)

        data = values
        values.pop(0)
        data.append(values)

    db_connector.commit()
    
    print('Base de donnée initialisée')


