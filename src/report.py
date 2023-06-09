import json as json


class Report:
    def __init__(self, from_json_file_name: str = None, page_size: int = 10_000):
        data = None
        if not from_json_file_name == None:
            with open(from_json_file_name) as file:
                data = json.load(file)
        self.name = None if data["name"] == None else data["name"]
        self.category = None if data["category"] == None else data["category"]
        self.metrics = None if data["metrics"] == None else list(
            data["metrics"])
        self.dimensions = None if data["dimensions"] == None else data["dimensions"]
        self.filters = None if data["filters"] == None else data["filters"]
        self.filter_operator = None if data["filterOperator"] == None else data["filterOperator"]
        self.page_size = 10000
        self.start_date = "2005-01-01"
        self.end_date = "2023-07-01"

    def __str__(self):
        metrics_str = "Metrics:"
        if self.metrics:
            metrics = self.metrics
            # Calculate the midpoint for splitting into two columns
            half_len = (len(metrics) + 1) // 2
            metrics_col1 = metrics[:half_len]
            metrics_col2 = metrics[half_len:]
            metrics_str += "\n" + \
                "\n".join([f"    - {m1:<20}{m2:<20}" for m1,
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
