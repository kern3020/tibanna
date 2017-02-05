# -*- coding: utf-8 -*-
import boto3
import json

client = boto3.client('stepfunctions')
STEP_FUNCTION_ARN = 'arn:aws:states:us-east-1:643366669028:stateMachine:run_sbg_workflow_2'


def handler(event, context):
    '''
    this is triggered on completed file upload from s3 and
    event will be set to file data.
    '''
    # get file name
    filename = event['Records'][0]['s3']['object']['key']
    run_name = "validate_%s" % (filename.split('/')[0])

    # trigger the step function to run
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        name=run_name,
        input=make_input(event),
    )

    return response


def make_input(event):
    filename = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    uuid, key = filename.split('/')
    json_data = {"parameters": {},
                 "app_name": "md5",
                 "workflow_uuid": "d3f25cd3-e726-4b3c-a022-48f844474b41",
                 "input_files": [
                    {"workflow_argument_name": "input_file",
                     "bucket_name": bucket,
                     "uuid": uuid,
                     "object_key": key,
                     }
                 ],
                 "output_bucket": "elasticbeanstalk-encoded-4dn-wfoutput-files"
                 }

    return json.dumps(json_data)