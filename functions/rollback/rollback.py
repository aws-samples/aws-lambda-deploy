"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import boto3

def handler(event, context):
    print(event)

    func_name = event['function-name']
    alias_name = event['alias-name']

    # reset the routing config
    rollback(func_name, alias_name)

    return event

def rollback(func_name, alias_name):
   client = boto3.client('lambda')
   routing_config = {
       'AdditionalVersionWeights' : {}
   }
   res = client.update_alias(FunctionName=func_name, Name=alias_name,
                             RoutingConfig=routing_config)
   print(res)

   return
