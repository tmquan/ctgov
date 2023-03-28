import requests
import argparse
import datetime
import pandas as pd
from typing import List
from sqlalchemy import create_engine, text

class ClinicalTrialsDownloader(object):
    def __init__(self, rows: int = 100, columns: List[str] = None, prompt: str = None):
        self.base_url = "https://clinicaltrials.gov/api/query/study_fields"
        self.rows = rows
        self.prompt = prompt
        self.columns = columns if columns else []

    def download_data(self) -> pd.DataFrame:
        if self.prompt:
            payload = {
                "expr": self.prompt, 
                "max_rnk": self.rows,
                "fmt": "json",
                "fields": ",".join(self.columns),
            }
        else:
            payload = {
                "max_rnk": self.rows,
                "fmt": "json",
                "fields": ",".join(self.columns),
            }
        print(payload)
        response = requests.get(self.base_url, params=payload)

        if response.status_code == 200:
            data = response.json()
            trials_data = data["StudyFieldsResponse"]["StudyFields"]
            return self._create_dataframe(trials_data)
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    def _create_dataframe(self, trials_data: List[dict]) -> pd.DataFrame:
        df = pd.DataFrame(trials_data)
        # Remove 'Rank' column
        df.drop(columns=['Rank'], inplace=True)

        # Set 'NCTId' as index and remove the 'NCTId' column
        df.set_index(df['NCTId'].apply(lambda x: x[0]), inplace=True)
        df.drop(columns=['NCTId'], inplace=True)

        # Convert lists to appropriate data types
        for column in df.columns:
            # Remove double quotes from the DataFrame
            df[column] = df[column].apply(lambda x: x[0].replace('"', '') if isinstance(x[0], str) else x)
            df[column] = pd.to_datetime(df[column], errors='coerce') if 'Date' in column else df[column]
        return df


class AACTClinicalTrialsDownloader(object):
    def __init__(
            self,
            prompt: str,
            rows: int = 100,
            columns: List[str] = None,
            db_credentials: str = None
    ):
        self.prompt = prompt
        self.rows = rows
        self.columns = columns if columns else []
        self.db_credentials = db_credentials

    def download_data(self) -> pd.DataFrame:
        # Create a connection to the AACT database using the connection string
        engine = create_engine(self.db_credentials)

        # Define the SQL query based on the search term, selected columns, and number of rows
        query = text(f"""
            SELECT {', '.join(['s.'+column for column in self.columns])}
            FROM ctgov.studies s
        """)
        print(query)

        # Execute the SQL query and create a pandas DataFrame from the result
        df = pd.read_sql_query(
            query,
            con=engine,
            params={
                "prompt": f"%{self.prompt}%",
                "rows": self.rows
            } # type: ignore
        )

        # Set 'NCTId' as index and remove the 'NCTId' column
        df.set_index(df['nct_id'], inplace=True)
        df.drop(columns=['nct_id'], inplace=True)

        # Convert lists to appropriate data types
        for column in df.columns:
            # Remove double quotes from the DataFrame
            df[column] = df[column].apply(lambda x: x.replace('"', '') if isinstance(x, str) else x)
            df[column] = pd.to_datetime(df[column], errors='coerce') if 'date' in column else df[column]

        # Close the connection
        engine.dispose()

        return df

def main():
    parser = argparse.ArgumentParser(
        description="Fetch clinical trial data from ClinicalTrials.gov")
    parser.add_argument("--prompt", default=None, help="Search term")
    parser.add_argument(
        "--columns",
        nargs='+',
        default=[
            "NCT_ID",
            "brief_title",
            "study_type",
            "source",
            "start_date",
            "verification_date",
            "primary_completion_date"
        ],
        help="A list of columns to include in the output CSV file")
    parser.add_argument("--rows", type=int, default=100, help="The number of rows to fetch from ClinicalTrials.gov")
    parser.add_argument("--output", default="ctgov", help="The output CSV file name (without extension)")

    args = parser.parse_args()

    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{args.output}_{args.rows}_{timestamp}.csv"

    #
    # downloader = ClinicalTrialsDownloader(
    #     rows=args.rows, 
    #     columns=args.columns, 
    #     prompt=args.prompt
    # )
    
    username = "username"
    password = "password"
    hostname = "hostname"
    port = "port"
    database = "database"
    db_credentials = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"

    downloader = AACTClinicalTrialsDownloader(
        prompt=args.prompt,
        rows=args.rows, 
        columns=args.columns,  # type: ignore
        db_credentials=db_credentials
    )

    data_frame = downloader.download_data()
    print(data_frame)

    # Write the data to output filename
    data_frame.to_csv(file_name)


if __name__ == "__main__":
    main()
    # python DataDownloaderTrialToTrials.py --rows=437713 --output=ctgov
    # python DataDownloaderTrialToTrials.py --rows=10000 --output=ctgov --prompt=leukemia
