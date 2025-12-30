import httpx
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

RETENTION_DAYS = 365

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


"""
This script fetches weather forecast data from the CWA API, preprocesses it,
and inserts it into a MySQL database. It also deletes records older than 7 days.

cron job setup (every 6 hours):
0 */6 * * * /home/devuser/anaconda3/envs/practice1/bin/python /home/devuser/chiayi/practice1/cwa_api.py >> /home/devuser/chiayi/practice1/cwa_api.log 2>&1
"""

def db_connect():
    # Establish database connection using .env variables
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        connect_timeout=10
    )

def fetch_data(url: str) -> dict:
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()  # ensure the request was successful
            return response.json()
    except httpx.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        return {}

def preprocess_weather_data(data: dict) -> list:
    if not data or 'records' not in data:
        return []

    def transform_datetime_format(dt_str: str) -> tuple[int, int]:
        dt_obj = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return int(dt_obj.strftime('%Y%m%d')), int(dt_obj.strftime('%H%M'))

    processed_data = []
    target_elements = ['Wx', 'PoP', 'MinT', 'MaxT', 'CI']
    locations = data.get('records', {}).get('location', [])

    for location in locations:
        city_name = location.get('locationName')
        elems_dict = {el['elementName']: el.get('time', []) for el in location.get('weatherElement', [])}

        if not elems_dict:
            continue

        base_times = next(iter(elems_dict.values()))
        for i, time_period in enumerate(base_times):
            oneset_data = {'city_name': city_name} # Redefine oneset_data for each iteration
            try:
                oneset_data['start_date_id'], oneset_data['start_time_id'] = transform_datetime_format(time_period['startTime'])
                oneset_data['end_date_id'], oneset_data['end_time_id'] = transform_datetime_format(time_period['endTime'])

                for e in target_elements:
                    val = None
                    if e in elems_dict and i < len(elems_dict[e]):
                        val = elems_dict[e][i].get('parameter', {}).get('parameterName')
                    oneset_data[e.lower()] = val

                processed_data.append(oneset_data)
            except (IndexError, KeyError) as e:
                logging.warning(f"Data missing for {city_name} at index {i}: {e}")
                continue

    return processed_data

def execute_db_tasks(preprocessed_data: list):
    try:
        conn = db_connect()
        cursor = conn.cursor()

        cursor.execute("SELECT location_name, sk FROM dim_location") # Fetch location mapping
        location_map = {name: sk for name, sk in cursor.fetchall()}

        insert_data = []
        for r in preprocessed_data:
            sk = location_map.get(r['city_name'])
            if sk:
                insert_data.append((
                    sk, r['start_date_id'], r['start_time_id'], r['end_date_id'], r['end_time_id'],
                    r['wx'], r['pop'], r['mint'], r['maxt'], r['ci']
                ))

        if insert_data:
            # Original insert statement with IGNORE
            # batch_insert_sql = """INSERT IGNORE INTO fact_weather_forecast (location_sk, start_date_id, start_time_id,
            # end_date_id, end_time_id, wx, pop, mint, maxt, ci) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            # Modified to use ON DUPLICATE KEY UPDATE
            batch_insert_sql = """
INSERT INTO fact_weather_forecast (
    location_sk, start_date_id, start_time_id, end_date_id, end_time_id,
    wx, pop, mint, maxt, ci, data_pull_time
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
ON DUPLICATE KEY UPDATE
    wx = VALUES(wx),
    pop = VALUES(pop),
    mint = VALUES(mint),
    maxt = VALUES(maxt),
    ci = VALUES(ci),
    data_pull_time = NOW();
"""
            cursor.executemany(batch_insert_sql, insert_data)
            logging.info(f"{len(insert_data)} new or updated records successfully processed.")

        delete_sql = f"""DELETE FROM fact_weather_forecast WHERE data_pull_time < NOW() - INTERVAL {RETENTION_DAYS} DAY"""
        cursor.execute(delete_sql)
        logging.info(f"{cursor.rowcount} old records successfully deleted.")

        conn.commit()

    except mysql.connector.Error as err:
        logging.error(f"Database error occurred: {err}")
        if conn: conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def main():
    try:
        # Get authorization token from .env
        AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")
        if not AUTHORIZATION_TOKEN:
            logging.error("No Authorization Token found in .env")
            return
        request_url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={AUTHORIZATION_TOKEN}&sort=time"

        # Fetch data from the API
        logging.info("Starting CWA Data Fetch...")
        original_data = fetch_data(request_url)

        if original_data:
            # Preprocess the fetched data
            processed_data = preprocess_weather_data(original_data)
            if processed_data:
                execute_db_tasks(processed_data)
                logging.info("ETL Job Finished Successfully.")
            else:
                logging.warning("No valid data to process after preprocessing.")
        else:
            logging.error("Failed to fetch data from API.")

    except Exception as e:
        logging.error(f"執行失敗: {str(e)}")

if __name__ == "__main__":
    main()