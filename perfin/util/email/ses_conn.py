import os

import boto3

from botocore.exceptions import ClientError

from perfin.util.es.es_conn import search
from perfin.util.es.queries import bucket_munger

from .builder import build_from_template


def send_email(date_range, equality, account):
    path = '{}/templates/stats_template.html.j2'.format(os.path.dirname(__file__))

    stats = search('stats', account, equality, date_range)
    # average = search('average', account, equality, date_range)
    top_trans = search('top_transactions', account, equality, date_range)

    stats = bucket_munger(stats['aggregations'])
    # average = bucket_munger(average['aggregations'])
    top_trans = bucket_munger(top_trans['aggregations'])

    queries = {
        'stats' : stats,
        # 'average' : average,
        'top_trans' : top_trans
    }
    html = build_from_template(path, queries)

    client = boto3.client('ses', region_name='us-east-1')

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    'mzakany@gmail.com',
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': 'summary stats',
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': 'Summary stats',
                },
            },
            Source='mzakany@gmail.com'
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
