# Import modules
# ==================================
import datetime
import json
import os
import sys
from pathlib import Path

import mysql.connector
import requests
from dotenv import load_dotenv
from mysql.connector import errorcode

# ==================================

# Load .env
# ==================================
load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
# ==================================

# Read .env variables
# ==================================
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USER_ID = os.getenv("TWITCH_USER_ID")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PW = os.getenv("MYSQL_PW")
MYSQL_DB = os.getenv("MYSQL_DB")
STORE_IF_OFFLINE = os.getenv("STORE_IF_OFFLINE")
# ==================================

# DB config
# ==================================
cnx = mysql.connector.connect(
  host='127.0.0.1',
  user=MYSQL_USER,
  password=MYSQL_PW
)
# ==================================

# Stream data
# ==================================
STREAM_LIVE = ''
USER_ID = ''
STREAM_ID = ''
STREAM_TITLE = ''
GAME_ID = ''
GAME_NAME = ''
START_TIMESTAMP = ''
# ==================================

# Get system time
# ==================================
CHECK_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# ==================================

# Get the auth token from twitch
# ==================================
def authenticate(client_id, client_secret):
  try:
    global TWITCH_AUTH_TOKEN
    payload = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials', 'scope': 'analytics:read:extensions'}
    r = requests.post('https://id.twitch.tv/oauth2/token', params=payload)

    return json.loads(r.text)["access_token"]

  except Exception as e:
    print(sys.stderr, "Exception: %s" % str(e))
    sys.exit(1)
# ==================================

# Get stream data
# ==================================
def get_stream_data(client_id, auth_token, user_id):
  try:
    global STREAM_LIVE
    global USER_ID
    global STREAM_ID
    global STREAM_TITLE
    global GAME_ID
    global GAME_NAME
    global START_TIMESTAMP

    payload = {'user_id': user_id}
    headers = {'client-id': client_id, 'Authorization': 'Bearer ' +  auth_token}
    r = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=payload)

    response = json.loads(r.text)["data"][0]

    STREAM_LIVE = True
    USER_ID = response["user_id"]
    STREAM_ID = response["id"]
    STREAM_TITLE = response["title"]
    GAME_ID = response["game_id"]
    GAME_NAME = response["game_name"]
    START_TIMESTAMP = datetime.datetime.strptime(response["started_at"], '%Y-%m-%dT%H:%M:%SZ')
  except:
    STREAM_LIVE = False
    START_TIMESTAMP = '1000-01-01 00:00:00'
# ==================================

# Create DB table function
# ==================================
def create_database(cursor):
  try:
    cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(MYSQL_DB))
  except mysql.connector.Error as err:
    print("Failed creating DB: {}".format(err))
    sys.exit(1)
# ==================================

# Execute API calls
# ==================================
TWITCH_AUTH_TOKEN = authenticate(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
get_stream_data(TWITCH_CLIENT_ID, TWITCH_AUTH_TOKEN, TWITCH_USER_ID)
# ==================================

# Output data
# ==================================
print("Received data:")
print("======================================")
print('STREAM_LIVE:         ', STREAM_LIVE)
print('USER_ID:             ', USER_ID)
print('STREAM_ID:           ', STREAM_ID)
print('STREAM_TITLE:        ', STREAM_TITLE)
print('GAME_ID:             ', GAME_ID)
print('GAME_NAME:           ', GAME_NAME)
print('START_TIMESTAMP:     ', START_TIMESTAMP)
print('CHECK_TIMESTAMP:     ', CHECK_TIMESTAMP)
print("======================================")
print()
# ==================================

# Store data if manually selected or stream is live
# ==================================
if STORE_IF_OFFLINE == True or STREAM_LIVE == True:

# Database handling
# ==================================
  print("Database handling")
  print("======================================")

# DB scheme
# ==================================
  TABLES = {}
  TABLES['stream_data'] = (
      "CREATE TABLE `stream_data` ("
      "  `STREAM_LIVE` bool,"
      "  `USER_ID` VARCHAR(30),"
      "  `STREAM_ID` VARCHAR(30),"
      "  `STREAM_TITLE` VARCHAR(100),"
      "  `GAME_ID` VARCHAR(30),"
      "  `GAME_NAME` VARCHAR(30),"
      "  `START_TIMESTAMP` datetime,"
      "  `CHECK_TIMESTAMP` datetime"
      ") ENGINE=InnoDB")
# ==================================

  cursor = cnx.cursor()

# Check if DB exists
# ==================================
  try:
    cursor.execute("USE {}".format(MYSQL_DB))
  except mysql.connector.Error as err:
    print("DB {} does not exist yet!".format(MYSQL_DB))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
      create_database(cursor)
      print("DB {} created successfully.".format(MYSQL_DB))
      cnx.database = MYSQL_DB
    else:
      print("DB error: {}".format(err))
      sys.exit(1)
# ==================================

# Check if table exists
# ==================================
  for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
      print("Creating table {}: ".format(table_name), end='')
      cursor.execute(table_description)
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
        print("already exists.")
      else:
        print("DB error: {}".format(err))
        sys.exit(1)
    else:
      print("OK")
# ==================================

# Data insert
# ==================================
  add_stream_data = ("INSERT INTO stream_data "
                 "(STREAM_LIVE, USER_ID, STREAM_ID, STREAM_TITLE, GAME_ID, GAME_NAME, START_TIMESTAMP, CHECK_TIMESTAMP) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

  stream_data = (STREAM_LIVE, USER_ID, STREAM_ID, STREAM_TITLE, GAME_ID, GAME_NAME, START_TIMESTAMP, CHECK_TIMESTAMP)

  try:
    cursor.execute(add_stream_data, stream_data)
    cnx.commit()
    print("Data insertion successful.")
  except mysql.connector.Error as err:
    print("Data insertion failed: {}".format(err))
    sys.exit(1)

  cursor.close()
  cnx.close()
# ==================================

else:
  print("Data will not be stored to Database!")

print("======================================")
