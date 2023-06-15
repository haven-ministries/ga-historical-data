from src.analytics_connection import AnalyticsConnection
from src.report import Report


def main():
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
        {"category": "audience", "name": "location"},
        {"category": "audience", "name": "mobile"},
        {"category": "audience", "name": "new_vs_returning_users"},
        {"category": "audience", "name": "operating_system"},
        {"category": "audience", "name": "other_categories"},
        {"category": "audience", "name": "screen_resolution"},
        {"category": "behavior", "name": "all_pages_with_filters"},
        {"category": "behavior", "name": "all_pages"},
        {"category": "behavior", "name": "landing_pages"},
        {"category": "behavior", "name": "search_terms"},
        {"category": "conversions", "name": "product_performance"},
    ]

    # client = AnalyticsConnection()
    # report = Report(from_json_file_name=f"reports/{category}/{name}.json")
    # df = client.getAllData(report)
    # df.to_csv(f"data/{category}/{name}.csv")

    client = AnalyticsConnection()
    for idx, report_item in enumerate(reports):
        category = report_item["category"]
        name = report_item["name"]

        print(f"Downloading {category}/{name} ({idx} of {len(reports)})")

        report = Report(from_json_file_name=f"reports/{category}/{name}.json")
        df = client.getAllData(report)
        df.to_csv(f"data/{category}/{name}.csv")


if __name__ == '__main__':
    main()
