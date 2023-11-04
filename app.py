import os
from datetime import datetime, timezone
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

CREATE_ROOMS_TABLE = (
  "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
)

CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, 
  date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""


INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"

INSERT_TEMP = (
  "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"
)

GLOBAL_NUMBER_OF_DAYS = (
  """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""
)
GLOBAL_AVG = """SELECT AVG(temperature) as average FROM temperatures;"""

app = Flask(__name__)
db_url_connection = os.getenv("DATABASE_URL")
db_connection = psycopg2.connect(db_url_connection)

@app.post("/api/room")
def create_room():
  request_body = request.get_json()
  room_name = request_body["name"]

  with db_connection:
    with db_connection.cursor() as cursor:
      cursor.execute(CREATE_ROOMS_TABLE)
      cursor.execute(INSERT_ROOM_RETURN_ID, (room_name,))
      room_id = cursor.fetchone()[0]
      
  return {"room_id": room_id, "message": f"Room {room_name} created."}, 201


@app.post("/api/temperatures")
def create_temperature():
  request_body = request.get_json()
  temperature = request_body["temperature"]
  room_id = request_body["room_id"]
  
  try:
    date = datetime.strptime(request_body["date"], "%m-%d-%Y %H:%M:%S")
  except KeyError:
    date = datetime.now(timezone.utc)
  
  with db_connection:
    with db_connection.cursor() as cursor:
      cursor.execute(CREATE_TEMPS_TABLE)
      cursor.execute(INSERT_TEMP, (room_id, temperature, date))
  
  return { "message": "Temperature added" }, 201


@app.get("/api/average")
def get_global_average():
  with db_connection:
    with db_connection.cursor() as cursor:
      cursor.execute(GLOBAL_AVG)
      average = cursor.fetchone()[0]
      cursor.execute(GLOBAL_NUMBER_OF_DAYS)
      days = cursor.fetchone()[0]
  
  return { "average": round(average, 2), "days": days }, 200
