import datetime
import json
import os
import sendgrid
from dotenv import load_dotenv
from python_http_client.exceptions import HTTPError


def checkAPIUsage(headers):
    # Check if we have less than 10% of allowed API calls remaining
    if float(headers['x-ratelimit-remaining']) / float(headers['x-ratelimit-limit']) < 0.1:
        print("Warning: remaining API calls less than 10%")


def getSuppressionList(suppressionType, params, headers):
    print("\n{0} {1} {0}".format('#' * 12, suppressionType.upper()))
    try:
        # Derive method from string passed in ('bounces' or 'blocks') and call
        method = getattr(sg.client.suppression, suppressionType)
        response = method.get(query_params=params, request_headers=headers)
    except HTTPError as e:
        print(e.to_dict)

    if response.status_code != 200:
        print('Error: HTTP Status Code {0}'.format(response.status_code))

    # Convert JSON response to list and iterate
    resultsList = json.loads(response.body.decode('utf-8'))
    if len(resultsList) > 0:
        print("Created,Email,Reason,Status")
        for result in resultsList:
            # Each item in the list has four elements: created (Unix timestamp), email, reason, status
            result['reason'] = result['reason'].replace('\r\n', ' | ')
            print("{0},{1},{2},{3}".format(datetime.datetime.fromtimestamp(result['created']).strftime(
                '%Y-%m-%d %H:%M:%S'), result['email'], result['reason'], result['status']))
    else:
        print("No {0} in this reporting period".format(suppressionType))

    checkAPIUsage(response.headers)


# Set up SendGrid API client
load_dotenv()
sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
headers = {'Accept': 'application/json'}

# For bounces and blocks, we'll retrieve the last 24 hours of data
now = datetime.datetime.now()
startTime = now - datetime.timedelta(days=1)

# Suppressions API uses Unix timestamps for start_time and end_time
params = {'start_time': int(startTime.timestamp()),
          'end_time': int(now.timestamp())}
getSuppressionList("bounces", params, headers)
getSuppressionList("blocks", params, headers)

# Stats API uses string (yyyy-mm-dd) for start_time and end_time.
# Here we select the first day of the current month
params = {'aggregated_by': 'month', 'start_date': datetime.datetime(
    now.year, now.month, 1).strftime('%Y-%m-%d')}
print("\n{0} STATS {0}".format('#' * 12))
try:
    response = sg.client.stats.get(
        query_params=params, request_headers=headers)
except HTTPError as e:
    print(e.to_dict)

if response.status_code != 200:
    print('Error: HTTP Status Code {0}'.format(response.status_code))

# Convert JSON response to list
results = json.loads(response.body.decode('utf-8'))
requestsThisMonth = results[0]['stats'][0]['metrics']['requests']
print("Requests (quota utilisation) so far this month: {0}".format(
    requestsThisMonth))
checkAPIUsage(response.headers)
