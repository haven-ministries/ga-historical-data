from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import calendar
import pandas as pd

def initialize_anlyticsreporting(key_file: str = '../Credentials\client_secrets.json', scopes: [str] = ['https://www.googleapis.com/auth/analytis.readonly']):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        '../Credentials\client_secrets.json', ['https://www.googleapis.com/auth/analytics.readonly'])
    analytics = build('analyticsreporting','v4',credentials=credentials)
    return analytics

def get_report(analytics_object, view_id: str, start_date: str, end_date: str):
    return analytics_object.reports().batchGet(body =
        {
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [
                        {'expression': 'ga:newUsers'},
                        {'expression': 'ga:percentNewSessions'},
                        {'expression': 'ga:sessions'},
                        {'expression': 'ga:bounceRate'},
                        {'expression': 'ga:avgSessionDuration'},
                        {'expression': 'ga:pageviews'},
                        {'expression': 'ga:transactions'},
                        {'expression': 'ga:transactionRevenue'}
                    ],
                    'dimensions': [
                        {'name': 'ga:landingPagePath'},
                        {'name': 'ga:date'}
                    ],
                    'dimensionFilterClauses': [
                        {
                            'filters': [
                                {
                                    'dimensionName': 'ga:landingPagePath',
                                    'expressions': '/',
                                    'operator': 'EXACT',
                                    'not': 'TRUE'
                                },
                                {
                                    'dimensionName': 'ga:landingPagePath',
                                    'expressions': '/?',
                                    'operator': 'BEGINS_WITH',
                                    'not': 'TRUE'
                                }
                            ],
                            'operator': 'AND'
                        }
                    ],
                    'pageSize': 10000
                }
            ]
        }
    ).execute()

def get_dataframe(response):
    list = []
    for report in response.get('reports',[]):
        columnHeader = report.get('columnHeader',{})
        dimensionHeaders = columnHeader.get('dimensions',[])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries',[])
        rows = report.get('data',{}).get('rows',[])
        
        for row in rows:
            dict = {}
            dimensions = row.get('dimensions',[])
            dateRangeValues = row.get('metrics',[])
            
            for header,dimension in zip(dimensionHeaders, dimensions):
                dict[header] = dimension
                
            for i, values in enumerate(dateRangeValues):
                for metric,value in zip(metricHeaders, values.get('values')):
                    if ',' in value or '.' in value:
                        dict[metric.get('name')] = float(value)
                    else:
                        dict[metric.get('name')] = int(value)
            list.append(dict)
        df = pd.DataFrame(list)
        return df

def get_reports_by_month(start_year: str) -> []:
    start_dates = []
    end_dates = []
    reports = []
    today = date.today()
    
    # Fill Start and end dates
    for year in range(start_year, today.year+1):
        for month in range(1,13,1):
            if (year==today.year and month>today.month):
                break
            month_str = '0'+str(month) if month<10 else str(month)
            day_start = '01'
            day_end = calendar.monthrange(year,month)[1]
            start_dates.append('{0}-{1}-{2}'.format(year,month_str,day_start))
            end_dates.append('{0}-{1}-{2}'.format(year,month_str,day_end))
    
    analytics = initialize_anlyticsreporting()
    VIEW_ID = '59914626' # Act: HavenToday.org, Property: HavenToday.org, View: HavenToday.org
    
    for start_date,end_date in zip(start_dates,end_dates):
        reports.append(get_report(analytics, VIEW_ID,start_date,end_date))
        if (len(get_dataframe(reports[-1]).index) >=9999):
            raise ValueError('ERROR: Google Analytics Returned Query Larger than 10k Rows ({0} to {1})'.format(start_date,end_date))
        
    return reports

def combine_reports(reports: []) -> pd.DataFrame:
    dataframes = []
    
    for report in reports:
        dataframes.append(get_dataframe(report))
        
    df = pd.concat(dataframes,ignore_index=True)
    
    df.columns = df.columns.str.replace('ga:','')
    
    return df

def main():
    reports_2016 = get_reports_by_month(2016)
    df = combine_reports(reports_2016)
    df.to_csv('../Raw/Google_Sheets/Web_Traffic_Data.csv',index=True,index_label='Index')

if __name__ == '__main__':
    main()