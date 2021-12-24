import psycopg2
from config.config import config
from fastapi import FastAPI, HTTPException
import json
import logging

# create logger
logger = logging.getLogger('db_functions.py')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

DATABASE_EXCEPTION = "DATABASE EXCEPTION"


def insert(data):
    """ Connect to the PostgreSQL database server """
    conn = None
    cards = data["cards"]

    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        logger.info("updating cards in database...")
        for card in cards:
            sku_value = card["sku_value"]
            card_name = card["card_name"]
            available = card["available"]
            sql = """INSERT INTO gpus(sku_value,card_name,available)
            VALUES(%s,%s,%s)  ON CONFLICT (sku_value) DO UPDATE SET available = EXCLUDED.available"""
            # execute a statement
            logger.info("inserting card: %s in to database", str(card_name))
            cur.execute(sql, (sku_value, card_name, available))
            conn.commit()
        # close communication with the database
        cur.close()
        logger.info("cards updated in database")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION)
    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed.')


def get_card(sku_value):
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        temp_dict = {}
        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        logger.info("reading cards in database...")
        sql = """SELECT * FROM gpus WHERE sku_value = %s """
        cur.execute(sql, (sku_value,))
        gpu_records = cur.fetchall()

        logger.info("record found :%s", gpu_records)
        json_object = []

        temp_dict["sku_value"] = gpu_records[0][0]
        temp_dict["card_name"] = gpu_records[0][1]
        temp_dict["available"] = gpu_records[0][2]
        json_object.append(temp_dict)
    except (Exception, psycopg2.Error) as error:
        logger.error("Error while fetching data from PostgreSQL %s", error)
        if len(gpu_records) == 0:
            logger.error(error)
            raise HTTPException(status_code=409, detail="no sku with that number exists in database")
        else:
            logger.error(error)
            raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION)
    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed.')
    return temp_dict


def get_all_cards():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        logger.info("reading cards in database...")
        sql = """SELECT * FROM gpus"""
        cur.execute(sql)
        gpu_records = cur.fetchall()
        json_object = []
        for row in gpu_records:
            temp_dict = {"sku_value": row[0], "card_name": row[1], "available": row[2]}
            json_object.append(temp_dict)
    except (Exception, psycopg2.Error) as error:
        logger.error("Error while fetching data from PostgreSQL %s", error)
        raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION)
    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed.')
    return_data = {"cards": json_object}
    app_json = json.dumps(return_data)
    app_json = json.loads(app_json)
    logger.info("cards in databse : %s", str(app_json))
    return app_json


# get card by availability
def get_card_available(available):
    """ Connect to the PostgreSQL database server """
    conn = None

    try:
        # read connection parameters
        params = config()
        temp_dict = {}
        # connect to the PostgreSQL server
        logger.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
        logger.info("reading cards in database...")
        sql = """SELECT * FROM gpus WHERE available = %s """
        cur.execute(sql, (available,))
        gpu_records = cur.fetchall()
        json_object = []
        for row in gpu_records:
            temp_dict = {"sku_value": row[0], "card_name": row[1], "available": row[2]}
            json_object.append(temp_dict)
    except (Exception, psycopg2.Error) as error:
        logger.error("Error while fetching data from PostgreSQL %s", error)
        raise HTTPException(status_code=500, detail=DATABASE_EXCEPTION)
    finally:
        if conn is not None:
            conn.close()
            logger.info('Database connection closed.')
    return_data = {"cards": json_object}
    app_json = json.dumps(return_data)
    app_json = json.loads(app_json)
    logger.info("records found %s", app_json)
    return app_json
