import os
import urllib.parse as up
import psycopg2

up.uses_netloc.append("postgres")
url = up.urlparse('postgres://herdlqqw:5GkFSWjQSp1Plap4gGnE-kX6mY7J1QB9@packy.db.elephantsql.com:5432/herdlqqw')
conn = psycopg2.connect(database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port
)