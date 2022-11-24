import psycopg2
import os
from urllib.parse import urlparse


URL = os.environ['DATABASE_URL']



result = urlparse(URL)

username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
conexion = psycopg2.connect(
    database = database,
    user = username,
    password = password,
    host = hostname,
    port = port
)


cursor = conexion.cursor()
