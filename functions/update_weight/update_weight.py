"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
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