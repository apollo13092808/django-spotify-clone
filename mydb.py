import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

# establishing the connection
conn = psycopg2.connect(
    user=os.getenv(key="DB_USER"),
    password=os.getenv(key="DB_PASSWORD"),
    host=os.getenv(key="DB_HOST"),
    port=os.getenv(key="DB_PORT"),
)
conn.autocommit = True

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Preparing query to create a database
sql = f'CREATE DATABASE {os.getenv(key="DB_NAME")};'

# Creating a database
cursor.execute(sql)
print('Database successfully created!')

# Closing the connection
conn.close()
