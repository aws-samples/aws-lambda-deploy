"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import boto3

def handler(event, context):
    print(event)

    func_name = event['function-name']
    version = event['new-version']
    alias_name = event['alias-name']

    # reset the routing config and set the primary version to the new version
    update_weight(func_name, alias_name, version)

    return event

def update_weight(func_name, alias_name, version):
    client = boto3.client('lambda')

    routing_config = {
        'AdditionalVersionWeights' : {}
    }

    res = client.update_alias(FunctionName=func_name, FunctionVersion=version,
                              Name=alias_name, RoutingConfig=routing_config)

    print(res)

    return
