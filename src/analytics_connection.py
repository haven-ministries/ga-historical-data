from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import calendar
import pandas as pd
from src.report import Report
from src.date_utils import Day, Month, Year, dateLoop
from datetime import datetime
from tqdm import tqdm


from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

load_dotenv()


class AnalyticsConnection:
    def __init__(self):
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
            "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"]
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

    def getAllData(self, report: Report):
        data_frames = []

        total_views = len(self.views.items())
        for idx, item in enumerate(self.views.items()):
            view_name, view_id = item
            print(
                f'\nGetting data for view: {view_name} ({idx+1} of {total_views})')
            try:
                df = self.getDataFrame(view_name, report=report)
                df["view_name"] = view_name
                data_frames.append(df)
            except:
                print(
                    f'Unable to retrieve data for view: {view_name}. Skipping...')

        return pd.concat(data_frames)

    def getReport(self, view_name: str, report: Report, start_date=datetime(2005, 1, 1), end_date=datetime(2023, 7, 1)):
        assert view_name in self.views, "View name must be one of the following: " + \
            ", ".join(self.views.keys())

        chunk_by = Month() if report.chunk_by == "month" else (
            Day() if report.chunk_by == "day" else Year())

        responses = []

        def get_response(start, end):
            body = report.generate(self.views[view_name], start.strftime(
                "%Y-%m-%d"), end.strftime("%Y-%m-%d"))
            response = self.client.reports().batchGet(body=body).execute()

            responses.append({"start_date": start,
                              "end_date": end, "response": response})

        dateLoop(start_date, end_date, chunk_by, get_response)

        return responses

    def getDataFrame(self, view_name: str, report=None, responses=None) -> pd.DataFrame:
        responses_with_meta = responses

        if responses_with_meta == None:
            assert report != None, "Either response or report must be provided"
            responses_with_meta = self.getReport(view_name, report)

        responses = [data['response'] for data in responses_with_meta]

        data_frames = []

        for response in responses:
            list = []
            for report in response.get('reports', []):
                columnHeader = report.get('columnHeader', {})
                dimensionHeaders = columnHeader.get('dimensions', [])
                metricHeaders = columnHeader.get(
                    'metricHeader', {}).get('metricHeaderEntries', [])
                rows = report.get('data', {}).get('rows', [])

                for row in rows:
                    dict = {}
                    dimensions = row.get('dimensions', [])
                    dateRangeValues = row.get('metrics', [])

                    for header, dimension in zip(dimensionHeaders, dimensions):
                        dict[header] = dimension

                    for i, values in enumerate(dateRangeValues):
                        for metric, value in zip(metricHeaders, values.get('values')):
                            if ',' in value or '.' in value:
                                dict[metric.get('name')] = float(value)
                            else:
                                dict[metric.get('name')] = int(value)
                    list.append(dict)
                df = pd.DataFrame(list)
                data_frames.append(df)
        return pd.concat(data_frames, ignore_index=True)
