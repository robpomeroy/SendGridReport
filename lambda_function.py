from datetime import datetime
from datetime import timedelta
from json import loads
from os import environ
from sendgrid import SendGridAPIClient
from python_http_client.exceptions import HTTPError


def checkAPIUsage(headers):
    # Check if we have less than 10% of allowed API calls remaining
    if float(headers['x-ratelimit-remaining']) / float(headers['x-ratelimit-limit']) < 0.1:
        return 'Warning: remaining API calls less than 10%\n'

    return ''


def getSuppressionList(sg, suppressionType, params, headers):
    output = "{0} {1} {0}\n".format('#' * 12, suppressionType.upper())

    try:
        # Derive method from string passed in ('bounces' or 'blocks') and call
        method = getattr(sg.client.suppression, suppressionType)
        response = method.get(query_params=params, request_headers=headers)
    except HTTPError as e:
        output += str(e.to_dict)

    if response.status_code != 200:
        output += "Error: HTTP Status Code {0}\n".format(response.status_code)

    else:
        # Convert JSON response to list and iterate
        resultsList = loads(response.body.decode('utf-8'))
        if len(resultsList) > 0:
            output += "Created,Email,Reason,Status\n"
            for result in resultsList:
                # Each item in the list has four elements: created (Unix timestamp), email, reason, status
                result['reason'] = result['reason'].replace('\r\n', ' | ')
                output += "{0},{1},{2},{3}\n".format(datetime.fromtimestamp(result['created']).strftime(
                    '%Y-%m-%d %H:%M:%S'), result['email'], result['reason'], result['status'])
        else:
            output += "No {0} in this reporting period\n".format(
                suppressionType)

    output += checkAPIUsage(response.headers)
    return output


def lambda_handler(event, context):

    ################
    ## INITIALISE ##
    ################

    # Set up SendGrid API client
    sg = SendGridAPIClient(api_key=environ.get('SENDGRID_API_KEY'))
    headers = {'Accept': 'application/json'}
    output = ''

    ####################
    ## BOUNCES/BLOCKS ##
    ####################

    # For bounces and blocks, we'll retrieve the last 24 hours of data
    now = datetime.now()
    startTime = now - timedelta(days=1)

    # Suppressions API uses Unix timestamps for start_time and end_time
    params = {'start_time': int(startTime.timestamp()),
              'end_time': int(now.timestamp())}
    output += getSuppressionList(sg, 'bounces', params, headers) + '\n\n'
    output += getSuppressionList(sg, 'blocks', params, headers) + '\n\n'

    ###########
    ## STATS ##
    ###########

    # Stats API uses string (yyyy-mm-dd) for start_time and end_time.
    # Here we select the first day of the current month
    params = {'aggregated_by': 'month', 'start_date': datetime(
        now.year, now.month, 1).strftime('%Y-%m-%d')}
    output += "{0} STATS {0}\n".format('#' * 12)

    try:
        response = sg.client.stats.get(
            query_params=params, request_headers=headers)
    except HTTPError as e:
        output += str(e.to_dict)

    if response.status_code != 200:
        output += "Error: HTTP Status Code {0}\n".format(response.status_code)

    else:
        # Convert JSON response to list
        results = loads(response.body.decode('utf-8'))
        requestsThisMonth = results[0]['stats'][0]['metrics']['requests']
        output += "Requests (quota utilisation) so far this month: {0}\n".format(
            requestsThisMonth)

    output += checkAPIUsage(response.headers)

    return {
        'statusCode': 200,
        'body': output
    }
