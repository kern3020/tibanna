import random
import string
import logging
import boto3
import os
import mimetypes
from uuid import uuid4, UUID
from .vars import _tibanna, EXECUTION_ARN


LOG = logging.getLogger(__name__)


def printlog(message):
    print(message)
    LOG.info(message)


def _tibanna_settings(settings_patch=None, force_inplace=False, env=''):
    tbn = {"run_id": str(uuid4()),
           "env": env,
           "url": '',
           'run_type': 'generic',
           'run_name': '',
           }
    in_place = None
    if force_inplace:
        if not settings_patch.get(_tibanna):
            settings_patch[_tibanna] = {}
    if settings_patch:
        in_place = settings_patch.get(_tibanna, None)
        if in_place is not None:
            tbn.update(in_place)
        else:
            tbn.update(settings_patch)

    # generate run name
    if not tbn.get('run_name'):
        # aws doesn't like / in names
        tbn['run_name'] = "%s_%s" % (tbn['run_type'].replace('/', '-'), tbn['run_id'])

    if in_place is not None:
        settings_patch[_tibanna] = tbn
        return settings_patch
    else:
        return {_tibanna: tbn}


def randomize_run_name(run_name, sfn):
    arn = EXECUTION_ARN(run_name, sfn)
    client = boto3.client('stepfunctions', region_name='us-east-1')
    try:
        response = client.describe_execution(
                executionArn=arn
        )
        if response:
            if len(run_name) > 36:
                try:
                    UUID(run_name[-36:])
                    run_name = run_name[:-37]  # remove previous uuid
                except:
                    pass
            run_name += '-' + str(uuid4())

    except Exception:
        pass
    return run_name


# random string generator
def randomword(length):
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(choices) for i in range(length))


def create_jobid():
    return randomword(12)    # date+random_string


def read_s3(bucket, object_name):
    response = boto3.client('s3').get_object(Bucket=bucket, Key=object_name)
    printlog(str(response))
    return response['Body'].read().decode('utf-8', 'backslashreplace')


def does_key_exist(bucket, object_name, quiet=False):
    try:
        file_metadata = boto3.client('s3').head_object(Bucket=bucket, Key=object_name)
    except Exception as e:
        if not quiet:
            print("object %s not found on bucket %s" % (str(object_name), str(bucket)))
            print(str(e))
        return False
    return file_metadata


def upload(filepath, bucket, prefix='', public=True):
    """upload a file to S3 under a prefix.
    The original directory structure is removed
    and only the filename is preserved.
    If filepath is none, upload an empty file with prefix
    itself as key"""
    if public:
        acl='public-read'
    else:
        acl='private'
    s3 = boto3.client('s3')
    if filepath:
        dirname, filename = os.path.split(filepath)
        key = os.path.join(prefix, filename)
        printlog("filepath=%s, filename=%s, key=%s" % (filepath, filename, key))
        content_type = mimetypes.guess_type(filename)[0]
        if content_type is None:
            content_type = 'binary/octet-stream'
        try:
            s3.upload_file(filepath, bucket, key, ExtraArgs={'ACL': acl, 'ContentType': content_type})
        except Exception as e:
            s3.upload_file(filepath, bucket, key, ExtraArgs={'ACL': 'private', 'ContentType': content_type})
    else:
        try:
            s3.put_object(Body=b'', Bucket=bucket, Key=prefix, ACL=acl)
        except Exception as e:
            s3.put_object(Body=b'', Bucket=bucket, Key=prefix, ACL='private')
