"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
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
