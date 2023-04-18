import requests
import argparse
import datetime
import pandas as pd
from typing import List
from sqlalchemy import create_engine, text

class AACTClinicalTrialsDownloader(object):
    def __init__(
            self,
            prompt: str,
            columns: List[str] = None,
            db_credentials: str = None
    ):
        self.prompt = prompt
        self.db_credentials = db_credentials

    def download_data(self, query=None) -> pd.DataFrame:
        # Create a connection to the AACT database using the connection string
        engine = create_engine(self.db_credentials)

        # Define the SQL query based on the search term, selected columns, and number of rows
        if query is None:
            pass
        print(query)
        # Execute the SQL query and create a pandas DataFrame from the result
        df = pd.read_sql_query(
            query,
            con=engine,
            params={
                # "prompt": f"%{self.prompt}%",
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
    parser.add_argument("--output", default="ctgov", help="The output CSV file name (without extension)")

    args = parser.parse_args()

    # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{args.output}_{timestamp}.csv"

    #
    # downloader = ClinicalTrialsDownloader(
    #     rows=args.rows, 
    #     columns=args.columns, 
    #     prompt=args.prompt
    # )
    username = "ops600"
    password = "bPjfoGk9RrhOl9YenBTxftgHssiwID7j"
    hostname = "127.0.0.1"
    port = 32346
    database = "aact"

    db_credentials = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"

    downloader = AACTClinicalTrialsDownloader(
        prompt=args.prompt,
        db_credentials=db_credentials
    )
    # query = None
    query = text(f"""
        SELECT
            studies.nct_id,
            MAX(studies.brief_title) AS brief_title,
            MAX(studies.official_title) AS official_title,
            STRING_AGG(DISTINCT baseline_measurements.description, ' ') AS baseline_measurements,
            STRING_AGG(DISTINCT brief_summaries.description, ' ') AS brief_summaries,
            STRING_AGG(DISTINCT detailed_descriptions.description, ' ') AS detailed_descriptions,
            MAX(eligibilities.criteria) AS criteria, 
            MAX(eligibilities.gender) AS gender, 
            MAX(eligibilities.minimum_age) AS minimum_age, 
            MAX(eligibilities.maximum_age) AS maximum_age, 
            MAX(facilities.name) AS facilities, 
            MAX(facilities.city) AS city, 
            MAX(facilities.state) AS state, 
            MAX(facilities.zip) AS zip, 
            MAX(facilities.country) AS country, 
            MAX(participant_flows.recruitment_details) AS recruitment_details, 
            MAX(participant_flows.pre_assignment_details) AS pre_assignment_details, 
            MAX(studies.study_type) AS study_type
        FROM 
            ctgov.studies
        INNER JOIN ctgov.baseline_measurements ON baseline_measurements.nct_id = studies.nct_id 
        INNER JOIN ctgov.brief_summaries ON brief_summaries.nct_id = studies.nct_id 
        INNER JOIN ctgov.detailed_descriptions ON detailed_descriptions.nct_id = studies.nct_id 
        INNER JOIN ctgov.eligibilities ON eligibilities.nct_id = studies.nct_id 
        INNER JOIN ctgov.facilities ON facilities.nct_id = studies.nct_id 
        INNER JOIN ctgov.participant_flows ON participant_flows.nct_id = studies.nct_id 
        GROUP BY studies.nct_id;
    """)
    
    
    
    data_frame = downloader.download_data(query=query)
    print(data_frame)

    # Write the data to output filename
    data_frame.to_csv(file_name)


if __name__ == "__main__":
    main()
    # python DataDownloaderTrialToTrials.py --rows=437713 --output=ctgov
    # python DataDownloaderTrialToTrials.py --rows=10000 --output=ctgov --prompt=leukemia
