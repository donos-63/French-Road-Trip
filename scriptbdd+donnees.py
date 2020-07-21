
# # Import des différentes bibliothèques 

import sys
import sqlite3  # C'est un provider (fournisseur de service) terme svt utilisé pour les bases de données
import os   # Le module os est un module  fournit par Python dont le but d’interagir avec le système d’exploitation, il permet ainsi de gérer l’arborescence des fichiers, de fournir des informations sur le système d’exploitation processus, variables systèmes, ainsi que de nombreuses fonctionnalités du systèmes…
import csv   # Import de la fonction permettant de travailler ac des fichiers CSV (writer, reader)

# AFFECTATION DES VARIABLES

DB_PATH = os.getcwd() + os.sep + "db_sncf.db" 
# DB_PATH = "C:\Users\utilisateur\Documents\2. PROJETS\PROJET 1 SNCF vacances ac Mathieu" + "\db_sncf.db"      chemin dur ne fonctionne pas

# SI LA BDD EXISTE ALORS ON LA SUPPRIME, SUPPRESSION DE LA BDD EXISTANTE
if os.path.exists(DB_PATH):
        bdd = sqlite3.connect(DB_PATH)
        bdd.close()
        os.remove(DB_PATH)

# CONNECTION A LA BDD + AJOUT SI ELLE N'EXISTE PAS
db_sncf = sqlite3.connect(DB_PATH)
cur = db_sncf.cursor()

# # CREATION TABLES
cur.execute('''CREATE TABLE prefecture (insee_code INTEGER PRIMARY KEY, postal_code INTEGER,
city TEXT, department INTEGER, region TEXT, statut TEXT, average_altitude FLOAT, area FLOAT,
population FLOAT, geo_lat FLOAT, geo_long FLOAT, id_geo TEXT, common_code INTEGER, canton_code INTEGER,
district_code INTEGER, departement_code INTEGER, area_code INTEGER);''')
print("Création de la table prefecture effectuée.")

cur.execute('''CREATE TABLE journey (insee_code_from INTEGER, isee_code_to INTEGER, co2 FLOAT, duration INTEGER);''')
print("Création de la table journey effectuée.")

# # ## SAUVEGARDE DE LA BDD
db_sncf.commit()
print("BDD sauvegardée.")

# with open('bdd_sncf.csv', newline='') as csvfile:   #  Si csvfile est un fichier, il doit être ouvert avec newline=''
#     bdd_sncf = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     i = 0
#     for row in bdd_sncf:
#         print(i)
#         str.split (";")
#         i = i + 1

# print("Fin de l'écriture de la BDD")


with open('bdd_sncf.csv', mode="r", encoding="utf-8") as file :
    dic = csv.DictReader(file)
    for row in dic :
        if not row["statut"].endswith("Préfecture"):
            continue
        v1 = row["insee_code"]
        v2 = row["postal_code"]
        v3 = row["city"]
        v4 = row["department"]
        v5 = row["region"]
        v6 = row["statut"]
        v7 = row["average_altitude"]
        v8 = row["area"]
        v9 = row["population"]
        v10 = row["geo_lat"]
        v11 = row["geo_long"]
        v12 = row["id_geo"]
        v13 = row["common_code"]
        v14 = row["canton_code"]
        v15 = row["district_code"]
        v16 = row["departement_code"]
        v17 = row["area_code"]



        variable = [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, v13, v14, v15, v16, v17]
        cur.execute("""INSERT OR IGNORE 
        INTO prefecture(insee_code, postal_code, city, department,region, statut, average_altitude, area,
        population, geo_lat, geo_long, id_geo, common_code, canton_code, district_code, departement_code, area_code) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", variable)
    db_sncf.commit()


