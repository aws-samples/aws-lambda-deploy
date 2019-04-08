"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import time
import boto3
from datetime import datetime, date, timedelta
import logging

log = logging.getLogger('simple')
lambda_client = None

def handler(event, context):
	init()
	validate_input(event)

	func_name = event['function-name']
	version = event['new-version']
	alias_name = event['alias-name']
	steps = event['steps']
	interval = event['interval']
	weight_function = event.get('type', 'linear')
	health_check = event.get('health-check', True)

	weights = generate_weights(weight_function, steps)
	start_time = time.time()

	log.info("Calculated alias weight progression: {0}".format(weights))

	for weight in weights:
		update_weight(func_name, alias_name, version, weight)
		sleep(interval)

		if health_check:
			success = do_health_check(func_name, alias_name, version)
			if not success:
				rollback(func_name, alias_name)
				raise Exception("Health check failed, exiting")

	res = finalize(func_name, alias_name, version)
	end_time = time.time()

	log.info("Alias {0}:{1} is now routing 100% of traffic to version {2}".format(func_name, alias_name, version))
	log.info("Finished after {0}s".format(round(end_time - start_time, 2)))

	return res

def update_weight(func_name, alias_name, version, next_weight):
	log.info("Updating weight of alias {1}:{2} for version {0} to {3}".format(version, func_name, alias_name, next_weight))
	client = get_lambda_client()

	weights = {
		version : next_weight
	}
	routing_config = {
		'AdditionalVersionWeights' : weights
	}

	client.update_alias(FunctionName=func_name, Name=alias_name, RoutingConfig=routing_config)
	return

def sleep(sleep_time):
	time.sleep(sleep_time)

def validate_input(event):
	if not 'function-name' in event:
		raise Exception("'function-name' is required")
	if not 'new-version' in event:
		raise Exception("'new-version' is required")
	if not 'alias-name' in event:
		raise Exception("'alias-name' is required")
	if not 'interval' in event:
		raise Exception("'interval' is required")
	if not 'steps' in event:
		raise Exception("'steps' is required")

def do_health_check(func_name, alias_name, version):
	# implement custom health checks here (i.e. invoke, cloudwatch alarms, etc)
	return check_errors_in_cloudwatch(func_name, alias_name, version)

# Return False if any error metrics were emitted in the last minute for the function/alias/new version combination
def check_errors_in_cloudwatch(func_name, alias_name, new_version):
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
			log.info("Failing health check because error metrics were found for new version: {0}".format(datapoints))
			return False

	return True

def rollback(func_name, alias_name):
	log.info("Health check failed. Rolling back to original version")
	client = get_lambda_client()
	routing_config = {
		'AdditionalVersionWeights' : {}
	}
	client.update_alias(FunctionName=func_name, Name=alias_name, RoutingConfig=routing_config)
	log.info("Alias was successfully rolled back to original version")
	return

# Set the new version as the primary version and reset the AdditionalVersionWeights
def finalize(func_name, alias_name, version):
	client = get_lambda_client()
	routing_config = {
		'AdditionalVersionWeights' : {}
	}
	res = client.update_alias(FunctionName=func_name, FunctionVersion=version, Name=alias_name, RoutingConfig=routing_config)
	return res

def generate_weights(type, steps):
	if type == "linear":
		values = linear(steps)
	# implement other functions here
	else:
		raise Exception("Invalid function type: " + type)
	return values

def get_num_points(time, interval):
	return time / interval

def linear(num_points):
	delta = 1.0 / num_points
	prev = 0
	values = []
	for i in range(0, num_points):
		val = prev + delta
		values.append(round(val, 2))
		prev = val
	return values

def get_lambda_client():
	global lambda_client
	if lambda_client is None:
		lambda_client = boto3.client('lambda')
	return lambda_client

def init():
	logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
	for logging_handler in logging.root.handlers:
		logging_handler.addFilter(logging.Filter('simple'))

def main():
	# main() is useful for testing locally. not used when run in Lambda
	test_event = {
		'function-name': "echo",
		 'new-version': "1",
		 'alias-name': "myalias",
		 'steps': 10,
		 'interval': 5,
		 'type': "linear",
		 'health-check': True
	}
	log.info(handler(test_event, ""))

if __name__ == "__main__":
	main()
