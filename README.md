# aws-lambda-deploy
A collection of sample tools to enable canary deployments of [AWS Lambda](https://aws.amazon.com/lambda) functions.

Full background and examples can be found in [Implementing Canary Deployments of AWS Lambda Functions with Alias Traffic Shifting](https://aws.amazon.com/blogs/compute/implementing-canary-deployments-of-aws-lambda-functions-with-alias-traffic-shifting/) on the AWS Compute Blog.

## Installation
Please ensure you have the [AWS CLI](https://aws.amazon.com/cli) installed and configured with [credentials](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

The install script uses SAM to deploy relevant resources to your AWS account:
```bash
$ git clone https://github.com/awslabs/aws-lambda-deploy
$ cd aws-lambda-deploy
$ export BUCKET_NAME=[S3_BUCKET_NAME_FOR_BUILD_ARTIFACTS]
$ ./install.sh
```

## Simple deployment function
This simple Python script runs as a Lambda function and deploys another function by incrementally increasing the weight of the new function version over a prescribed number of steps, while checking the health of the new version. 

If the health check fails, the alias is rolled back to its initial version. The health check is implemented as a simple check against the existence of Errors metrics in CloudWatch for the alias and new version.

```bash
# Rollout version 2 incrementally over 10 steps, with 120s between each step
$ aws lambda invoke --function-name SimpleDeployFunction --log-type Tail --payload \
   '{"function-name": "MyFunction",
   "alias-name": "MyAlias",
   "new-version": "2",
   "steps": 10,
   "interval" : 120,
   "type": "linear"
   }' output
```

## Deployment workflow
This state machine performs essentially the same task as the simple deployment function, but it runs as an asynchronous workflow in AWS Step Functions, with a maximum timeout of 1 year.

The step function will incrementally update the new version weight based on the "steps" parameter, waiting for some time based on the "interval" parameter, and performing health checks between updates. If the health check fails, the alias will be rolled back to the original version and the workflow will fail.

```bash
$ export STATE_MACHINE_ARN=`aws cloudformation describe-stack-resources --stack-name aws-lambda-deploy-stack --logical-resource-id DeployStateMachine --output text | cut  -d$'\t' -f3`
$ aws stepfunctions start-execution --state-machine-arn $STATE_MACHINE_ARN --input '{
"function-name": "MyFunction",
"alias-name": "MyAlias",
"new-version": "2",
"steps": 10,
"interval": 120,
"type": "linear"}'

```
