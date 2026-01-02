import httpx
from sqlmodel import Session, create_engine
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import func
from datetime import datetime
import logging

from core.config import Config
from services.utils import fetch_location_map
from models.weather import *

"""
This script fetches weather forecast data from the CWA API, preprocesses it,
and inserts it into a MySQL database. It also deletes records older than 7 days.

cron job setup (every 6 hours):
0 */6 * * * cd /home/devuser/chiayi/practice1 && /home/devuser/anaconda3/envs/practice1/bin/python -m services.data_collector >> /home/devuser/chiayi/practice1/logs/cwa_fetch.log 2>&1
"""

AUTHORIZATION_TOKEN = Config.AUTHORIZATION_TOKEN
RETENTION_DAYS = 365

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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


# def cursor_insert_fcstdata(preprocessed_data: list):

#     def db_connect():
#         # Establish database connection using .env variables
#         return mysql.connector.connect(
#             host=Config.HOST,
#             user=Config.USER,
#             password=Config.PASSWORD,
#             database=Config.DATABASE,
#             connect_timeout=10
#         )

#     try:
#         conn = db_connect()
#         cursor = conn.cursor()

#         cursor.execute("SELECT location_name, sk FROM dim_location") # Fetch location mapping
#         location_map = {name: sk for name, sk in cursor.fetchall()}

#         insert_data = []
#         for r in preprocessed_data:
#             sk = location_map.get(r['city_name'])
#             if sk:
#                 insert_data.append((
#                     sk, r['start_date_id'], r['start_time_id'], r['end_date_id'], r['end_time_id'],
#                     r['wx'], r['pop'], r['mint'], r['maxt'], r['ci']
#                 ))

#         if insert_data:
#             # Original insert statement with IGNORE
#             # batch_insert_sql = """INSERT IGNORE INTO fact_weather_forecast (location_sk, start_date_id, start_time_id,
#             # end_date_id, end_time_id, wx, pop, mint, maxt, ci) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

#             # Modified to use ON DUPLICATE KEY UPDATE
#             batch_insert_sql = """
# INSERT INTO fact_weather_forecast (
#     location_sk, start_date_id, start_time_id, end_date_id, end_time_id,
#     wx, pop, mint, maxt, ci, data_pull_time
# ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
# ON DUPLICATE KEY UPDATE
#     wx = VALUES(wx),
#     pop = VALUES(pop),
#     mint = VALUES(mint),
#     maxt = VALUES(maxt),
#     ci = VALUES(ci),
#     data_pull_time = NOW();
# """
#             cursor.executemany(batch_insert_sql, insert_data)
#             logging.info(f"{len(insert_data)} new or updated records successfully processed.")

#         # delete_sql = f"""DELETE FROM fact_weather_forecast WHERE data_pull_time < NOW() - INTERVAL {RETENTION_DAYS} DAY"""
#         # cursor.execute(delete_sql)
#         # logging.info(f"{cursor.rowcount} old records successfully deleted.")

#         conn.commit()

#     except mysql.connector.Error as err:
#         logging.error(f"Database error occurred: {err}")
#         if conn: conn.rollback()
#     finally:
#         if conn and conn.is_connected():
#             cursor.close()
#             conn.close()


def session_insert_fcstdata(processed_data):
    engine = create_engine(Config.DATABASE_URL)
    with Session(engine) as session:
        loc_map = fetch_location_map(session)
        for item in processed_data:
            city = item.pop("city_name")
            item["location_sk"] = loc_map.get(city)

            # 建立 ORM 物件
            # record = Fact_Weather_Forecast(**item)
            # session.add(record)

        # 建立基礎的 insert 指令
        stmt = insert(Fact_Weather_Forecast).values(processed_data)
        on_duplicate_stmt = stmt.on_duplicate_key_update(
            wx=stmt.inserted.wx,
            pop=stmt.inserted.pop,
            mint=stmt.inserted.mint,
            maxt=stmt.inserted.maxt,
            ci=stmt.inserted.ci,
            data_pull_time=func.current_timestamp()
            # 注意：這裡不寫 sk，所以 ID 不會變
        )
        session.exec(on_duplicate_stmt)
        session.commit()
    logging.info(f"{len(processed_data)} new or updated records successfully processed.")


def main():
    try:
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
                # cursor_insert_fcstdata(processed_data)
                session_insert_fcstdata(processed_data)
                logging.info("ETL Job Finished Successfully.")
            else:
                logging.warning("No valid data to process after preprocessing.")
        else:
            logging.error("Failed to fetch data from API.")

    except Exception as e:
        logging.error(f"執行失敗: {str(e)}")

if __name__ == "__main__":
    main()