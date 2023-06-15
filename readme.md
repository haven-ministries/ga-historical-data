# Google Analytics Historical Data

This repo is for extracting google analytics data from Universal Anlaytics before migrating to GA4. 

### Resources

- [Google Analytics Query Sandbox](https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet?apix_params=%7B%22resource%22%3A%7B%22reportRequests%22%3A%5B%7B%22viewId%22%3A%2259914626%22%2C%22dateRanges%22%3A%5B%7B%22startDate%22%3A%222005-01-01%22%2C%22endDate%22%3A%222023-07-01%22%7D%5D%2C%22metrics%22%3A%5B%7B%22expression%22%3A%22ga%3Ausers%22%7D%2C%7B%22expression%22%3A%22ga%3AnewUsers%22%7D%2C%7B%22expression%22%3A%22ga%3Asessions%22%7D%2C%7B%22expression%22%3A%22ga%3Abounces%22%7D%2C%7B%22expression%22%3A%22ga%3Atransactions%22%7D%2C%7B%22expression%22%3A%22ga%3AtransactionRevenue%22%7D%5D%2C%22dimensions%22%3A%5B%7B%22name%22%3A%22ga%3AuserAgeBracket%22%7D%2C%7B%22name%22%3A%22ga%3Adate%22%7D%5D%2C%22pageSize%22%3A10000%7D%5D%7D%7D&apix=true#Dimension)
- [Dimensions & Metrics Explorer](https://ga-dev-tools.google/dimensions-metrics-explorer/)