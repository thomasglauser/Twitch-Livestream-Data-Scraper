# Twitch Livestream Data Scraper

![Twitch Scraper 1](https://github.com/AUThomasCH/Twitch-Livestream-Data-Scraper/workflows/Twitch%20Scraper%201/badge.svg)

## Overview

This application periodically saves certain livestream data through a Github Action Workflow through the Twitch API.
The data is then stored in a Google Cloud SQL instance.

## Dependencies

- [A Google Cloud SQL Instance](https://cloud.google.com/sql)
- Python 3.8
- [python requests](https://github.com/psf/requests)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [mysql-connector-python](https://github.com/mysql/mysql-connector-python)

## Setup

### Get a Twitch API Token

1. Register a Twitch developer application: https://dev.twitch.tv/console/apps
2. Generate a new client secret.
3. Now you have a client_id and a client_secret. Both values ​​must be saved in a Github secret. The GitHub action workflow will use those values for API authentication. The secrets must be named as follows:
   - TWITCH_CLIENT_ID
   - TWITCH_CLIENT_SECRET

### Setup a Google Cloud SQL instance

1. Setup a Google Cloud SQL instance.
2. Create a new user with password authentication.
3. Store the MySQL user credentials in GitHub Secrets as follows:
   - MYSQL_USER
   - MYSQL_PW
4. Setup the Cloud SQL-Proxy and generate a private key. https://cloud.google.com/sql/docs/mysql/connect-external-app#proxy
5. Store the value of the private key in the GitHub Secret GCP_SQL_KEY
6. Store the value of the MySQL connection name in the GitHub Secret GCP_SQL_INSTANCE

### Configure the Scraper

1. Define the workflow schedule according to the crontab format. See https://crontab.guru/ for help.
2. Define the Twitch user_id to scrape in the env variable TWITCH_USER_ID in the scraper.yml file.
3. Define the MySQL Database name where the data is stored in the env variable MYSQL_DB in the scraper.yml file.
4. Define if you want to store the data if the livestream is offline. This is defined in the env var STORE_IF_OFFLINE

## DB scheme:

```sh
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
```

## Table:

```sh
mysql> SELECT * FROM stream_data;

+-------------+-----------+-------------+---------------------------------------------------+---------+----------------+---------------------+---------------------+
| STREAM_LIVE | USER_ID   | STREAM_ID   | STREAM_TITLE                                      | GAME_ID | GAME_NAME      | START_TIMESTAMP     | CHECK_TIMESTAMP     |
+-------------+-----------+-------------+---------------------------------------------------+---------+----------------+---------------------+---------------------+
|           1 | XXXXXXXXX | XXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     | 65876   | Cyberpunk 2077 | 2020-12-19 10:03:59 | 2020-12-19 12:25:26 |
|           1 | XXXXXXXXX | XXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     | 65876   | Cyberpunk 2077 | 2020-12-19 10:03:59 | 2020-12-19 12:31:40 |
|           1 | XXXXXXXXX | XXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     | 65876   | Cyberpunk 2077 | 2020-12-19 10:03:59 | 2020-12-19 12:32:00 |
|           1 | XXXXXXXXX | XXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     | 65876   | Cyberpunk 2077 | 2020-12-19 10:03:59 | 2020-12-19 12:32:43 |
|           1 | XXXXXXXXX | XXXXXXXXXXX | XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX     | 65876   | Cyberpunk 2077 | 2020-12-19 10:03:59 | 2020-12-19 13:04:21 |
+-------------+-----------+-------------+---------------------------------------------------+---------+----------------+---------------------+---------------------+
```

| Database value  |                Description                |
| --------------- | :---------------------------------------: |
| STREAM_LIVE     |       True if the streamer is live        |
| USER_ID         |           The streamers user_id           |
| STREAM_ID       |     The ID of the current livestream      |
| STREAM_TITLE    |         The current stream title          |
| GAME_ID         |        The ID of the current game         |
| GAME_NAME       |       The name of the current game        |
| START_TIMESTAMP | The timestamp when the livestream started |
| CHECK_TIMESTAMP |   The timestamp of the data scraper run   |

**All timestamps are in UTC time!**

## Contributing

I welcome direct contributions to the Twitch Livestream Data Scraper code base. Thank you!

## License

This is open source software
[licensed as GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).
