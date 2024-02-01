

import psycopg2
from psycopg2 import sql
import bcrypt

db_params={
    'host':'localhost',
    'user':'postgres',
    'password':'snehakukku',
    'database':'taskManagement',

}

# Connect to PostgreSQL database
connection = psycopg2.connect(**db_params)
cursor = connection.cursor()


def encrypt_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')