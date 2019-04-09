"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import boto3
from datetime import datetime, date, timedelta

def handler(event, context):
    print(event)

    func_name = event['function-name']
    version = event['new-version']
    alias_name = event['alias-name']

    return health_check(func_name, version, alias_name)

def health_check(func_name, version, alias_name):
    # note: implement custom health checks here
    success = health_check_metrics_errors(func_name, alias_name, version)

    return "SUCCEEDED" if success else "FAILED"

# Return False if any error metrics were emitted in the last minute for the function/alias/new version combination
def health_check_metrics_errors(func_name, alias_name, new_version):
    client = boto3.client('cloudwatch')

    func_plus_alias = func_name + ":" + alias_name
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=1)

    response = client.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Errors',
        Dimensions=[
            {
                'Name': 'FunctionName',
                'Value': func_name
            },
            {
                'Name': 'Resource',
                'Value': func_plus_alias
            },
            {
                'Name': 'ExecutedVersion',
                'Value': new_version
            }
        ],
        StartTime=start_time,
        EndTime=now,
        Period=60,
        Statistics=['Sum']
    )
    datapoints = response['Datapoints']
    for datapoint in datapoints:
        if datapoint['Sum'] > 0:
            print("Failing health check because error metrics were found for new version: {0}".format(datapoints))
            return False

    return True
