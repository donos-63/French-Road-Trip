import psycopg2 #provider bdd postgres
import urllib.parse as urlp

class Connector:
    """Provide methods to connect to the saas database
    """

    def __init__(self):
        """on create, initialise connection to db
        """
        self.conn = self.__connection()

    def __enter__(self):
        """on method used
        """
        return self

    def __exit__(self, type, value, tb):
        """on instance relased

        Args:
            __exit__ based arguments
        """
        if not self.conn == None:
            self.conn.close()

    def __connection(self):
        """This function will return SQL Lite connection

        Returns:
            [Connection]: connection instance to the database
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
         
        return conn

    def execute_query(self, sql, args = None):
        """Execute sql query with returns

        Args:
            sql ([str]): sql query 
            args ([str[]], optional): query arguments

        Returns:
            [cursor]: resultset
        """
        cur = self.conn.cursor()
        cur.execute(sql, args)

        return cur

    def execute_nonquery(self, sql, args = None):
        """Execute sql query with returns

        Args:
            sql ([str]): sql query 
            args ([str[]], optional): query arguments
        """
        cur = self.conn.cursor()
        cur.execute(sql, args)

    def commit(self):
        """commit transaction
        """
        self.conn.commit()

    def rollback(self):
        """rollback transaction
        """
        self.conn.rollback()
