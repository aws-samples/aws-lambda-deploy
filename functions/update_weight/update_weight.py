"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import boto3

def handler(event, context):
    print(event)

    weights = event['weights']
    func_name = event['function-name']
    version = event['new-version']
    alias_name = event['alias-name']

    if 'current-weight' in event:
        current_weight = event['current-weight']
        next_weight = get_next_weight(weights, current_weight)
    else:
        next_weight = weights[0]

    update_weight(func_name, alias_name, version, next_weight)

    return next_weight

def get_next_weight(weights, current_weight):
    index = weights.index(current_weight)
    return weights[index+1]

def update_weight(func_name, alias_name, version, next_weight):
    print("next weight: {0}".format(next_weight))
    client = boto3.client('lambda')

    weights = {
        version : next_weight
    }
    routing_config = {
        'AdditionalVersionWeights' : weights
    }

    res = client.update_alias(FunctionName=func_name, Name=alias_name, RoutingConfig=routing_config)

    print(res)

    return
