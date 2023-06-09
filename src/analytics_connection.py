from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import calendar
import pandas as pd


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
