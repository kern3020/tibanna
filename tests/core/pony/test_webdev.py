from uuid import uuid4
from dcicutils.ff_utils import (
    generate_rand_accession,
    get_authentication_with_server,
    post_metadata,
    get_metadata,
    patch_metadata
)
from core.utils import run_workflow
from core.pony_utils import get_wfr_uuid, post_random_file
import gzip
import time


def testrun_md5_input_json_w_extra_file_object_name(env='webdev'):
    """Creates a random file object with no md5sum/content_md5sum and run md5 workflow.
    It waits for 6 mintues till the workflow run finishes and checks the input file object
    has been updated.
    """
    bucket = "elasticbeanstalk-fourfront-" + env + "-wfoutput"
    ff_key = get_authentication_with_server(ff_env='fourfront-' + env)
    newfile = post_random_file(bucket, ff_key)
    uuid = newfile['uuid']
    accession = newfile['accession']
    wf_uuid = "c77a117b-9a58-477e-aaa5-291a109a99f6"
    input_json = {
        "config": {
          "ebs_type": "io1",
          "ebs_iops": 500,
          "json_bucket": "4dn-aws-pipeline-run-json",
          "shutdown_min": 30,
          "log_bucket": "tibanna-output",
          "key_name": "4dn-encode",
          "password": ""
        },
        "_tibanna": {
          "env": "fourfront-webdev",
          "run_type": "md5_test_extra"
        },
        "parameters": {},
        "app_name": "md5",
        "workflow_uuid": wf_uuid,
        "input_files": [
                        {"workflow_argument_name": "input_file",
                         "bucket_name": bucket,
                         "uuid": uuid,
                         "object_key": accession + '.pairs.gz.px2',
                         "format_if_extra": "pairs_px2"
                         }
        ],
        "output_bucket": bucket,
        "wfr_meta": {"notes": "extra file md5 trigger test from test_webdev.py"}
    }
    resp = run_workflow(input_json)
    print(resp)

    # check result
    time.sleep(6*60)  # wait for 6 minutes
    filemeta = get_metadata(uuid, key=ff_key, add_on='?datastore=database')
    content_md5sum = filemeta.get('extra_files')[0].get('content_md5sum')
    md5sum = filemeta.get('extra_files')[0].get('md5sum')
    wfr_uuid = get_wfr_uuid(resp['_tibanna']['exec_arn'])
    wfr_meta = get_metadata(wfr_uuid, key=ff_key, add_on='?datastore=database')
    assert 'input_files' in wfr_meta
    assert 'format_if_extra' in wfr_meta['input_files'][0]
    assert md5sum
    assert content_md5sum
    print(content_md5sum)
    print(md5sum)
    patch_metadata({'status': 'deleted'}, uuid, key=ff_key)
    patch_metadata({'status': 'deleted'}, wfr_uuid, key=ff_key)


def testrun_md5(env='webdev'):
    """Creates a random file object with no md5sum/content_md5sum and run md5 workflow.
    It waits for 6 mintues till the workflow run finishes and checks the input file object
    has been updated.
    """
    bucket = "elasticbeanstalk-fourfront-" + env + "-wfoutput"
    ff_key = get_authentication_with_server(ff_env='fourfront-' + env)
    newfile = post_random_file(bucket, ff_key)
    uuid = newfile['uuid']
    accession = newfile['accession']
    input_json = {
        "config": {
          "ebs_type": "io1",
          "ebs_iops": 500,
          "json_bucket": "4dn-aws-pipeline-run-json",
          "shutdown_min": 30,
          "log_bucket": "tibanna-output",
          "key_name": "4dn-encode",
          "password": ""
        },
        "_tibanna": {
          "env": "fourfront-webdev",
          "run_type": "md5_test"
        },
        "parameters": {},
        "app_name": "md5",
        "workflow_uuid": "c77a117b-9a58-477e-aaa5-291a109a99f6",
        "input_files": [
                        {"workflow_argument_name": "input_file",
                         "bucket_name": bucket,
                         "uuid": uuid,
                         "object_key": accession + '.pairs.gz'
                         }
        ],
        "output_bucket": bucket,
        "wfr_meta": {"notes": "processed file md5 trigger test from test_webdev.py"}
    }
    resp = run_workflow(input_json)
    print(resp)

    # check result
    time.sleep(6*60)  # wait for 6 minutes
    filemeta = get_metadata(uuid, key=ff_key, add_on='?datastore=database')
    assert 'md5sum' in filemeta
    assert 'content_md5sum' in filemeta
    content_md5sum = filemeta.get('content_md5sum')
    md5sum = filemeta.get('md5sum')
    assert md5sum
    assert content_md5sum
    print(content_md5sum)
    print(md5sum)
    patch_metadata({'status': 'deleted'}, uuid, key=ff_key)
    wfr_uuid = get_wfr_uuid(resp['_tibanna']['exec_arn'])
    patch_metadata({'status': 'deleted'}, wfr_uuid, key=ff_key)
