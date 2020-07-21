import sys  
import sqlite3 
import os  
import csv



def insee_code_par_prefecture():      
    bdd = sqlite3.connect(DB_PATH)  # Connexion à la BDD
    cur = bdd.cursor()
    cur.execute('SELECT insee_code FROM prefecture')
    result = cur.fetchall()
    for insee in result:
        print(insee)
    bdd.close()
    return result

# Chemin d'accès
DB_PATH = os.getcwd() + os.sep + "db_sncf.db" 

insee_code_par_prefecture()

def nom_de_ville():      
    bdd = sqlite3.connect(DB_PATH) 
    cur = bdd.cursor()
    cur.execute('SELECT city FROM prefecture')
    result = cur.fetchall()
    for city in result:
        print(city)
    bdd.close()
    return result

# Chemin d'accès
DB_PATH = os.getcwd() + os.sep + "db_sncf.db" 

nom_de_ville()