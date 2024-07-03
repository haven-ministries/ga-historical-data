"""
Module: report_generator

This module provides a `Report` class that allows for the creation and configuration of
report requests based on JSON input files. The reports can be customized with various
parameters including metrics, dimensions, filters, and pagination.

Classes:
--------
Report:
    Represents a report configuration and provides methods to generate report requests.

Example usage:
--------------
# Initialize a Report instance from a JSON configuration file
report = Report(from_json_file_name="report_config.json")

# Generate a report request
report_request = report.generate(view_id="123456", start_date="2022-01-01", end_date="2022-12-31")

# Print the string representation of the report
print(report)
"""
import json
# from src.date_utils import Day, Month, Year


# pylint: disable=too-many-instance-attributes
class Report:
    """
    A class to represent a report and its associated configurations.

    Attributes:
    ----------
    name : str
        The name of the report.
    category : str
        The category of the report.
    metrics : list
        A list of metrics for the report.
    dimensions : list
        A list of dimensions for the report.
    filters : list
        A list of filters for the report.
    filter_operator : str
        The operator for combining filters.
    page_size : int
        The number of rows per page in the report.
    start_date : str
        The start date for the report.
    end_date : str
        The end date for the report.
    chunk_by : str
        The granularity of the report (day, month, year).

    Methods:
    -------
    generate(view_id: str, start_date: str = "2000-01-01", end_date: str = "2023-07-01") -> dict:
        Generates the report request dictionary.
    __str__():
        Returns a string representation of the report.
    """

    def __init__(self, from_json_file_name: str = None, page_size: int = 10_000):
        """
        Constructs all the necessary attributes for the Report object.

        Parameters:
        ----------
        from_json_file_name : str, optional
            The file name of the JSON file to load the report configuration from (default is None).
        page_size : int, optional
            The number of rows per page in the report (default is 10,000).
        """
        data = None

        if from_json_file_name is not None:
            with open(from_json_file_name, encoding="utf-8") as file:
                data = json.load(file)

        self.name = data["name"] if "name" in data else None
        self.category = data["category"] if "category" in data else None
        self.metrics = list(data["metrics"]) if "metrics" in data else None
        self.dimensions = data["dimensions"] if "dimensions" in data else None
        self.filters = data["filters"] if "filters" in data else None
        self.filter_operator = data["filterOperator"] if "filterOperator" in data else None
        self.page_size = page_size
        self.start_date = None
        self.end_date = None

        if "chunkBy" in data:
            assert data["chunkBy"] in [
                "day", "month", "year"], "Chunk by must be one of the following: day, month, year"

        self.chunk_by = data["chunkBy"] if "chunkBy" in data else None

    def generate(self, view_id: str, start_date="2000-01-01", end_date="2023-07-01") -> dict:
        """
        Generates the report request dictionary.

        Parameters:
        ----------
        view_id : str
            The ID of the view for which the report is generated.
        start_date : str, optional
            The start date for the report (default is "2000-01-01").
        end_date : str, optional
            The end date for the report (default is "2023-07-01").

        Returns:
        -------
        dict
            The report request dictionary.
        """
        assert view_id is not None, "View ID must be specified"
        assert start_date is not None, "Start date must be specified"
        assert end_date is not None, "End date must be specified"
        assert self.dimensions is not None, "Dimensions must be specified"
        assert self.metrics is not None, "Metrics must be specified"

        if self.filters:
            assert self.filter_operator is not None, \
                "Filter operator must be specified if filters are specified"
            for filter_item in self.filters:
                assert "dimension" in filter_item, "Filter dimension must be specified"
                assert "operator" in filter_item, "Filter operator must be specified"
                assert "expressions" in filter_item, "Filter expressions must be specified"
        self.start_date = start_date
        self.end_date = end_date

        report_request = {
            "viewId": view_id,
            "dateRanges": [{"startDate": start_date, "endDate": end_date}],
            "metrics": [{"expression": f"ga:{metric}"} for metric in self.metrics],
            "dimensions": [{"name": f"ga:{dimension}"} for dimension in self.dimensions],
        }

        if self.filters:
            filters = []
            for filter_item in self.filters:
                filters.append({
                    "dimensionName": f"ga:{filter_item['dimension']}",
                    "expressions": filter_item["expressions"],
                    "operator": filter_item["operator"],
                    "not": filter_item["not"] if "not" in filter_item else False
                })
            report_request["dimensionFilterClauses"] = [{
                "filters": filters,
                "operator": self.filter_operator if self.filter_operator else "AND"
            }]

        report_request['pageSize'] = self.page_size
        report_request['samplingLevel'] = 'LARGE'

        return {"reportRequests": [report_request]}

    def __str__(self):
        """
        Returns a string representation of the report.

        Returns:
        -------
        str
            A formatted string representation of the report.
        """
        metrics_str = "Metrics:"
        if self.metrics:
            metrics = self.metrics
            # Calculate the midpoint for splitting into two columns
            half_len = (len(metrics) + 1) // 2
            metrics_col1 = metrics[:half_len]
            metrics_col2 = metrics[half_len:]
            metrics_str += "\n" + \
                "\n".join([f"    - {m1:<20} - {m2:<20}" for m1,
                          m2 in zip(metrics_col1, metrics_col2)])
            # If there's an odd number of metrics, add an empty space for alignment
            if len(metrics) % 2 != 0:
                metrics_str += "\n" + f"- {metrics[-1]}"
        else:
            metrics_str += "\n    No metrics specified"

        dimensions_str = "Dimensions:\n    - " + \
            "\n    - ".join(self.dimensions) if self.dimensions else "No dimensions specified"
        filters_str = "Filters:"

        if self.filters:
            filter_operator_str = "AND" if self.filter_operator == "AND" else "OR"
            for i, filter_item in enumerate(self.filters):
                filter_dimension = filter_item["dimension"]
                filter_operator = filter_item["operator"]
                filter_expressions = filter_item["expressions"]
                # not_operator = filter_item["not"]

                filter_str = f"    - {filter_dimension} doesn't equal \"{filter_expressions}\"" \
                    if filter_operator == "EXACT" \
                    else f"    - {filter_dimension} doesn't begin with \"{filter_expressions}\""
                filters_str += "\n" + filter_str
                if i < len(self.filters) - 1:
                    filters_str += f"\n{filter_operator_str}"
        else:
            filters_str += " No filters specified"

        start_end_date_str = f"({self.category}) {self.name}\n{self.start_date} - {self.end_date}"

        summary = f"{start_end_date_str}\n\n" \
                  f"{dimensions_str}\n\n" \
                  f"{metrics_str}\n\n" \
                  f"{filters_str}"

        # Calculate the width and height of the rectangle border
        width = max(len(line) for line in summary.split("\n")) + 4
        # height = summary.count("\n") + 4

        # Construct the rectangle border
        border = "+" + "-" * (width - 2) + "+"
        lines = summary.split("\n")
        content = "\n".join(f"| {line.ljust(width - 4)} |" for line in lines)
        result = f"{border}\n{content}\n{border}"

        return result
