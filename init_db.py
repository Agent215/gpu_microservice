import psycopg2 
from config import config
from fastapi import FastAPI, HTTPException
import json


DATABASE_EXCEPTION = "DATABASE EXCEPTION"

def insert(data):
    """ Connect to the PostgreSQL database server """
    conn = None
    cards = data["cards"]

    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        print("updating cards in database...")
        for card in cards:
            sku_value = card["sku_value"]
            card_name = card["card_name"]
            available = card["available"]
            sql = """INSERT INTO gpus(sku_value,card_name,available)
            VALUES(%s,%s,%s)  ON CONFLICT (sku_value) DO UPDATE SET available = EXCLUDED.available"""
	        # execute a statement
            cur.execute(sql, (sku_value,card_name,available))
            conn.commit()
        # close communication with the database
        cur.close()
        print("cards updated in database")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION) 
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def get_card(sku_value):
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        temp_dict = {}
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        print("reading cards in database...")
        sql = """SELECT * FROM gpus WHERE sku_value = %s """
        cur.execute(sql,(sku_value,))
        gpu_records = cur.fetchall()
        print(len(gpu_records))
        
        print(gpu_records)
        json_object = []
        
        temp_dict["sku_value"] = gpu_records[0][0]
        temp_dict["card_name"] = gpu_records[0][1]
        temp_dict["available"] = gpu_records[0][2]
        print("sku_value = ", gpu_records[0][0] )
        print("card_name = ",  gpu_records[0][1])
        print("available  = ",  gpu_records[0][2], "\n")
        json_object.append(temp_dict)
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
        if len(gpu_records) == 0:
            raise HTTPException(status_code=409, detail="no sku with that number exists in database")
        else:
            raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    if temp_dict is not None:
        print(temp_dict)
    return temp_dict

def get_all_cards():
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        print("reading cards in database...")
        sql = """SELECT * FROM gpus"""
        cur.execute(sql)
        gpu_records = cur.fetchall()
        json_object = []
        for row in gpu_records:
            temp_dict = {}
            temp_dict["sku_value"] = row[0]
            temp_dict["card_name"] = row[1]
            temp_dict["available"] = row[2]
            print("sku_value = ", row[0], )
            print("card_name = ", row[1])
            print("available  = ", row[2], "\n")
            json_object.append(temp_dict)
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)
        raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return_data = {}
    return_data["cards"] = json_object
    app_json = json.dumps(return_data)
    app_json = json.loads(app_json)
    print(app_json)
    return app_json
if __name__ == '__main__':
    connect()