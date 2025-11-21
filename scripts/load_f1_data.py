from io import StringIO

import pandas as pd
import requests
from agno.utils.log import log_error, log_info
from sqlalchemy import create_engine

from db.url import get_db_url

s3_uri = "https://agno-public.s3.amazonaws.com/f1"

# List of files and their corresponding table names
files_to_tables = {
    f"{s3_uri}/constructors_championship_1958_2020.csv": "constructors_championship",
    f"{s3_uri}/drivers_championship_1950_2020.csv": "drivers_championship",
    f"{s3_uri}/fastest_laps_1950_to_2020.csv": "fastest_laps",
    f"{s3_uri}/race_results_1950_to_2020.csv": "race_results",
    f"{s3_uri}/race_wins_1950_to_2020.csv": "race_wins",
}


def load_f1_data():
    log_info("Loading F1 data into DB...")

    # Create database engine
    engine = create_engine(get_db_url())

    # Load each CSV file into corresponding table
    for file_path, table_name in files_to_tables.items():
        log_info(f"Loading {file_path} into {table_name} table...")
        try:
            # Download CSV from S3
            response = requests.get(file_path, verify=False)
            response.raise_for_status()

            # Read CSV data
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)

            # Load into PostgreSQL (replace if exists)
            df.to_sql(table_name, engine, if_exists="replace", index=False)

            log_info(f"{table_name}: {len(df)} rows loaded")

        except Exception as e:
            log_error(f"Failed to load {table_name}: {e}")
            raise

    log_info("F1 data load complete! 🏁")


if __name__ == "__main__":
    # Disable SSL verification warnings for S3
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    load_f1_data()
