"""
This module provides the AnalyticsConnection class for interacting with
Google Analytics Reporting API and handling data extraction, processing,
and saving functionalities.

Dependencies:
- googleapiclient.discovery
- oauth2client.service_account
- pandas
- dotenv
- src.report.Report
- src.date_utils.Day, Month, Year, dateLoop
"""

from datetime import datetime
from typing import List
import os
import time
# import signal

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dotenv import load_dotenv
# import tenacity

from src.report import Report
from src.date_utils import Day, Month, Year, dateLoop

load_dotenv()

# Custom exception for timeout


class TimeoutException(Exception):
    pass

# Function to handle timeout


def timeout_handler(signum, frame):
    raise TimeoutException


class AnalyticsConnection:
    """
    A class to handle connections to Google Analytics Reporting API and retrieve analytics data.
    """

    def __init__(self):
        """
        Initializes the AnalyticsConnection with Google Analytics service account credentials.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_dict({
            "type": "service_account",
            "project_id": os.environ["PROJECT_ID"],
            "private_key_id": os.environ["PRIVATE_KEY_ID"],
            "private_key": os.environ["PRIVATE_KEY"],
            "client_email": os.environ["CLIENT_EMAIL"],
            "client_id": os.environ["CLIENT_ID"],
            "auth_uri": os.environ["AUTH_URI"],
            "token_uri": os.environ["TOKEN_URI"],
            "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER_X509_CERT_URL"],
            "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"],
            "universe_domain": "googleapis.com"
        })
        self.client = build('analyticsreporting', 'v4',
                            credentials=credentials)
        self.views = {
            "HavenToday.org": os.environ["HAVENTODAY_ORG_VIEW_ID"],
            "Player": os.environ["PLAYER_VIEW_ID"],
            "HavenToday.ca": os.environ["HAVENTODAY_CA_VIEW_ID"],
            "GetAnchor.com": os.environ["GET_ANCHOR_VIEW_ID"],
            "AnchorToday": os.environ["ANCHOR_TODAY_VIEW_ID"],
            "AnchorSample": os.environ["ANCHOR_SAMPLE_VIEW_ID"],
            "Haven90DayBibleChallenge": os.environ["HAVEN_90_DAY_BIBLE_CHALLENGE_VIEW_ID"],
            "ElFaro90DayBibleChallenge": os.environ["EL_FARO_90_DAY_BIBLE_CHALLENGE_VIEW_ID"]
        }

    def get_all_data(self, report: Report):
        """
        Retrieves data for all views and concatenates them into a single DataFrame.

        Args:
            report (Report): The report configuration to generate data.

        Returns:
            pd.DataFrame: A concatenated DataFrame containing data from all views.
        """
        data_frames = []

        total_views = len(self.views.items())
        for idx, item in enumerate(self.views.items()):

            # item is a tuple of (view_name, view_id)
            view_name, _ = item
            print(
                f'\nGetting data for view: {view_name} ({idx+1} of {total_views})')
            try:
                df = self.get_dataframe(view_name, report=report)
                df["view_name"] = view_name
                data_frames.append(df)

            # pylint: disable=bare-except
            except:
                print(
                    f'Unable to retrieve data for view: {view_name}. Skipping...')

        return pd.concat(data_frames)

    def get_report(self,
                   view_name: str,
                   report: Report,
                   start_date=datetime(2023, 1, 1),  # CHANGEME: 2005
                   end_date=datetime(2023, 7, 1)):
        """
        Generates a report for a specific view within the given date range.

        Args:
            view_name (str): The name of the view.
            report (Report): The report configuration to generate data.
            start_date (datetime, optional): The start date for the report. Defaults to
                datetime(2005, 1, 1).
            end_date (datetime, optional): The end date for the report. Defaults to
                datetime(2023, 7, 1).

        Returns:
            List[dict]: A list of responses containing the report data.
        """
        assert view_name in self.views, "View name must be one of the following: " + \
            ", ".join(self.views.keys())

        chunk_by = Month() if report.chunk_by == "month" else (
            Day() if report.chunk_by == "day" else Year())

        responses = []

        def get_response(start, end):
            body = report.generate(self.views[view_name], start.strftime(
                "%Y-%m-%d"), end.strftime("%Y-%m-%d"))

            max_attempts = 3
            attempt = 1
            retry_delay_seconds = 2
            # timeout_seconds = 5

            while attempt <= max_attempts:
                # signal.signal(signal.SIGALRM, timeout_handler)

                try:
                    # signal.alarm(timeout_seconds)
                    # pylint: disable=no-member
                    response = self.client.reports().batchGet(body=body).execute()

                    responses.append({"start_date": start,
                                      "end_date": end, "response": response})
                    break
                except Exception as e:
                    print(f'Error fetching data: {str(e)}')
                    attempt += 1
                    if attempt <= max_attempts:
                        print(
                            f'Attempt {attempt - 1} of {max_attempts} failed. Retryinug in 5 seconds...')
                        time.sleep(retry_delay_seconds)
                    else:
                        print(
                            f'Failed to fetch data after {max_attempts} attempts. Retrying in {retry_delay_seconds} seconds...')
                        raise e
                # finally:
                #     signal.alarm(0)

        dateLoop(start_date, end_date, chunk_by, get_response)

        return responses

    def get_dataframe(self, view_name: str, report=None, responses=None) -> pd.DataFrame:
        """
        Converts the API responses into a pandas DataFrame.

        Args:
            view_name (str): The name of the view.
            report (Report, optional): The report configuration to generate data.
                Required if responses are not provided.
            responses (List[dict], optional): A list of responses containing the report data.

        Returns:
            pd.DataFrame: A DataFrame containing the report data.
        """
        responses_with_meta = responses

        if responses_with_meta is None:
            assert report is not None, "Either response or report must be provided"
            responses_with_meta = self.get_report(view_name, report)

        responses = [data['response'] for data in responses_with_meta]

        data_frames = []

        # pylint: disable=too-many-nested-blocks
        for response in responses:
            metrics_list = []
            for report_from_response in response.get('reports', []):
                column_header = report_from_response.get('columnHeader', {})
                dimension_headers = column_header.get('dimensions', [])
                metric_headers = column_header.get(
                    'metricHeader', {}).get('metricHeaderEntries', [])
                rows = report_from_response.get('data', {}).get('rows', [])

                for row in rows:
                    metrics_dict = {}
                    dimensions = row.get('dimensions', [])
                    date_range_values = row.get('metrics', [])

                    for header, dimension in zip(dimension_headers, dimensions):
                        metrics_dict[header] = dimension

                    # enumerate(dateRangeValues) returns list of tuples (index, values)
                    for _, values in enumerate(date_range_values):
                        for metric, value in zip(metric_headers, values.get('values')):
                            if ',' in value or '.' in value:
                                metrics_dict[metric.get('name')] = float(value)
                            else:
                                metrics_dict[metric.get('name')] = int(value)
                    metrics_list.append(metrics_dict)
                df = pd.DataFrame(metrics_list)
                data_frames.append(df)
        return pd.concat(data_frames, ignore_index=True)

    def save_csv_chunks(self,
                        view_names: List[str],
                        report: Report,
                        table_name: str,
                        category: str,
                        start_year=2005,
                        end_year=2023):
        """
        Saves data for specified views in CSV format, chunked by year.

        Args:
            view_names (List[str]): A list of view names to retrieve data for.
            report (Report): The report configuration to generate data.
            table_name (str): The name of the table to save the data.
            category (str): The category for organizing the data.
        """
        for view in view_names:
            for year in range(start_year, end_year+1):
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31)
                print(f'{view}: Downloading Responses for year {year} of {end_year}')
                responses = self.get_report(view, report, start_date, end_date)
                print(f'{view}: Creating DF for year {year} of {end_year}')
                df = self.get_dataframe(view, responses=responses)
                print(f'{view}: Saving CSV for year {year} of {end_year}')

                if not os.path.exists(f'./data/{category}/{table_name}'):
                    os.makedirs(f'./data/{category}/{table_name}')
                df.to_csv(
                    f'./data/{category}/{table_name}/{view}_{year}.csv', index=False)
                print(f'{view}: Done saving CSV for year {year} of {end_year}\n\n')

            print(f'{view}: Done saving CSVs for all years\n\n')
        print('Done saving CSVs for all views\n\n')
