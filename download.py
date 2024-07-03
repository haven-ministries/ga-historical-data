"""
This script uses the AnalyticsConnection class to fetch Google Analytics 
data based on predefined reports and save the data in CSV format.

Dependencies:
- src.analytics_connection.AnalyticsConnection
- src.report.Report
"""
from src.analytics_connection import AnalyticsConnection
from src.report import Report


def main():
    """
    The main function to execute the data fetching and saving process.

    It defines a list of reports to be processed, initializes the AnalyticsConnection, 
    and iterates over the reports to fetch and save the data for specified view names.
    """
    reports = [
        {"category": "acquisition", "name": "campaigns"},
        {"category": "acquisition", "name": "channels"},
        {"category": "acquisition", "name": "referrals"},
        {"category": "acquisition", "name": "source_medium"},
        {"category": "audience", "name": "affinity_categories"},
        {"category": "audience", "name": "age"},
        {"category": "audience", "name": "branding"},
        {"category": "audience", "name": "browser"},
        {"category": "audience", "name": "devices"},
        {"category": "audience", "name": "gender"},
        {"category": "audience", "name": "in_market_segmentation"},
        {"category": "audience", "name": "language"},
        # {"category": "audience", "name": "location"},
        {"category": "audience", "name": "new_vs_returning_users"},
        {"category": "audience", "name": "operating_system"},
        {"category": "audience", "name": "other_categories"},
        {"category": "audience", "name": "screen_resolution"},

        {"category": "behavior", "name": "all_pages"},
        {"category": "behavior", "name": "landing_pages"},

        {"category": "behavior", "name": "search_terms"},
        {"category": "conversions", "name": "product_performance"},
        {"category": "conversions", "name": "sales_performance"},
    ]

    # client = AnalyticsConnection()
    # report = Report(from_json_file_name=f"reports/{category}/{name}.json")
    # df = client.getAllData(report)
    # df.to_csv(f"data/{category}/{name}.csv")

    view_names = [
        # "HavenToday.org",
        # "Player",
        "HavenToday.ca",
        "GetAnchor.com",
        "AnchorToday",
        "AnchorSample",
        "Haven90DayBibleChallenge",
        "ElFaro90DayBibleChallenge"
    ]

    client = AnalyticsConnection()
    for idx, report_item in enumerate(reports):
        category = report_item["category"]
        name = report_item["name"]

        print(f"Downloading {category}/{name} ({idx + 1} of {len(reports)})")

        report = Report(from_json_file_name=f"reports/{category}/{name}.json")
        # print(report)
        # df = client.getAllData(report)

        client.save_csv_chunks(view_names, report, name,
                               category, start_year=2018, end_year=2023)
        # df.to_csv(f"data/{category}/{name}.csv")


if __name__ == '__main__':
    main()
