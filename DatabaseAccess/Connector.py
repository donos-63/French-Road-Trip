import psycopg2 #provider bdd postgres
import urllib.parse as urlp

class Connector:

    def __init__(self):
        self.conn = self.__connection()
        print("Connector class is initiated")

    def __connection(self):
        """
        This function will return SQL Lite connection
        """
        #Initialisation du provider de donnée
        urlp.uses_netloc.append("postgres")
        #todo mettre l'url dans les variables d'environnement (venv/pypi)
        url = urlp.urlparse('postgres://herdlqqw:5GkFSWjQSp1Plap4gGnE-kX6mY7J1QB9@packy.db.elephantsql.com:5432/herdlqqw')
        conn = psycopg2.connect(database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
            )
         
        print("Initialisation de l'accés aux données")
        return conn

    def execute_query(self, sql, args = None):
        cur = self.conn.cursor()
        cur.execute(sql, args)

        return cur

    def execute_nonquery(self, sql, args = None):
        cur = self.conn.cursor()
        cur.execute(sql, args)

    def commit(self):
        self.conn.commit()
