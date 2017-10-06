#!/bin/bash

# Set this to a bucket owned by you
export STACK_NAME=aws-lambda-deploy-stack

rm -rf build
mkdir build
zip -jr build/health_check.zip functions/health_check/*
zip -jr build/calculate_weights.zip functions/calculate_weights/*
zip -jr build/rollback.zip functions/rollback/*
zip -jr build/update_weight.zip functions/update_weight/*
zip -jr build/finalize.zip functions/finalize/*
zip -jr build/simple.zip functions/simple/*

aws cloudformation package \
    --template-file template.yml \
    --s3-bucket $BUCKET_NAME \
    --output-template-file packaged-template.yml

aws cloudformation deploy \
    --template-file packaged-template.yml \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides BucketName=$BUCKET_NAME