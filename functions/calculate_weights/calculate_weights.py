"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

def handler(event, context):
    print(event)

    weights = generate_weights("linear", event['steps'])

    return weights

def generate_weights(type, steps):
    if type == "linear":
        values = linear(steps)
    else:
        raise Exception("Invalid function type: " + type)
    return values

def linear(num_points):
    delta = 1.0 / num_points
    prev = 0
    values = []
    # note: much more sophisticated weight functions can be generated using numpy
    for i in range(0, num_points):
        val = prev + delta
        values.append(round(val, 2))
        prev = val
    return values