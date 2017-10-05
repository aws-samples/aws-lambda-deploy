"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
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