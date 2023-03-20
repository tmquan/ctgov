import requests
import argparse
import datetime
import pandas as pd
from typing import List


class ClinicalTrialsDownloader(object):
    def __init__(self, rows: int = 100, columns: List[str] = None):
        self.base_url = "https://clinicaltrials.gov/api/query/study_fields"
        self.rows = rows
        self.columns = columns if columns else []

    def download_data(self) -> pd.DataFrame:
        payload = {
            "max_rnk": self.rows,
            "fmt": "json",
            "fields": ",".join(self.columns),
        }
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

def main():
    parser = argparse.ArgumentParser(
        description="Fetch clinical trial data from ClinicalTrials.gov")
    parser.add_argument(
        "--columns", 
        nargs='+', 
        default=[
            "NCTId", 
            "BriefTitle", 
            "BriefSummary",
            "Condition", 
            "LeadSponsorName",
            "StartDate", 
            "PrimaryCompletionDate"
        ], 
        help="A list of columns to include in the output CSV file")
    parser.add_argument("--rows", type=int, default=100,
                        help="The number of rows to fetch from ClinicalTrials.gov")
    parser.add_argument("--output", default="clinical_trials",
                        help="The output CSV file name (without extension)")


    args = parser.parse_args()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{args.output}_{args.rows}_{timestamp}.csv"
    
    #
    downloader = ClinicalTrialsDownloader(args.rows, args.columns)
    data_frame = downloader.download_data()
    print(data_frame)

    # Write the data to output filename
    data_frame.to_csv(file_name)
    
if __name__ == "__main__":
    main()
