from os import write
import psycopg2

def getConn():
    connStr = (
        "host='localhost' \
               dbname= 'swr_contingencyplans' user='postgres' password = '12345'"
        
    )
    conn = psycopg2.connect(connStr)
    return conn
    
