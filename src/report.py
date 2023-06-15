import json as json
from src.date_utils import Day, Month, Year


class Report:
    def __init__(self, from_json_file_name: str = None, page_size: int = 10_000):
        data = None

        if not from_json_file_name == None:
            with open(from_json_file_name) as file:
                data = json.load(file)

        self.name = data["name"] if "name" in data else None
        self.category = data["category"] if "category" in data else None
        self.metrics = list(data["metrics"]) if "metrics" in data else None
        self.dimensions = data["dimensions"] if "dimensions" in data else None
        self.filters = data["filters"] if "filters" in data else None
        self.filter_operator = data["filterOperator"] if "filterOperator" in data else None
        self.page_size = page_size

        if "chunkBy" in data:
            assert data["chunkBy"] in [
                "day", "month", "year"], "Chunk by must be one of the following: day, month, year"

        self.chunk_by = data["chunkBy"] if "chunkBy" in data else None

    def generate(self, view_id: str, start_date="2000-01-01", end_date="2023-07-01") -> dict:
        assert not view_id == None, "View ID must be specified"
        assert not start_date == None, "Start date must be specified"
        assert not end_date == None, "End date must be specified"
        assert not self.dimensions == None, "Dimensions must be specified"
        assert not self.metrics == None, "Metrics must be specified"

        if self.filters:
            assert not self.filter_operator == None, "Filter operator must be specified if filters are specified"
            for filter_item in self.filters:
                assert "dimension" in filter_item, "Filter dimension must be specified"
                assert "operator" in filter_item, "Filter operator must be specified"
                assert "expressions" in filter_item, "Filter expressions must be specified"

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
                not_operator = filter_item["not"]

                filter_str = f"    - {filter_dimension} doesn't equal \"{filter_expressions}\"" if filter_operator == "EXACT" else f"    - {filter_dimension} doesn't begin with \"{filter_expressions}\""
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
        height = summary.count("\n") + 4

        # Construct the rectangle border
        border = "+" + "-" * (width - 2) + "+"
        lines = summary.split("\n")
        content = "\n".join(f"| {line.ljust(width - 4)} |" for line in lines)
        result = f"{border}\n{content}\n{border}"

        return result
