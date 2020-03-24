import pytest
from tibanna.exceptions import (
    AWSEMErrorHandler,
    AWSEMJobErrorException
)
from tibanna.utils import printlog


def test_general_awsem_error_msg():
    eh = AWSEMErrorHandler()
    res = eh.general_awsem_error_msg('somejobid')
    assert res == 'Job encountered an error check log using tibanna log --job-id=somejobid [--sfn=stepfunction]'


def test_general_awsem_check_log_msg():
    eh = AWSEMErrorHandler()
    res = eh.general_awsem_check_log_msg('somejobid')
    assert res == 'check log using tibanna log --job-id=somejobid [--sfn=stepfunction]'


def test_awsem_exception_no_peak_called():
    log = "sometext some text some other text " + \
          "Exception: File is empty (1234567890abcdefg.regionPeak.gz) some other text"
    eh = AWSEMErrorHandler()
    res = eh.parse_log(log)
    assert res
    with pytest.raises(AWSEMJobErrorException) as exec_info:
        raise res
    assert 'No peak called' in str(exec_info)


def test_awsem_exception_not_enough_space_for_input():
    log = "sometext some text some other text " + \
          "download failed: s3://somebucket/somefile to ../../data1/input/somefile " + \
          "[Errno 28] No space left on device " + \
          "some other text some other text"
    eh = AWSEMErrorHandler()
    res = eh.parse_log(log)
    assert res
    with pytest.raises(AWSEMJobErrorException) as exec_info:
        raise res
    assert 'Not enough space for input files' in str(exec_info)


def test_awsem_exception_cwl_missing_input():
    log = "Workflow error, try again with --debug for more information:\n" + \
          "Invalid job input record:\n" + \
          "workflow_gatk-GenotypeGVCFs_plus_vcf-integrity-check.cwl:28:5: Missing required input parameter\n" + \
          "                                                     'chromosomes'\n" + \
          "some text some text"
    eh = AWSEMErrorHandler()
    res = eh.parse_log(log)
    assert res
    with pytest.raises(AWSEMJobErrorException) as exec_info:
        raise res
    assert 'CWL missing input' in str(exec_info)
    assert 'chromosomes' in str(exec_info)
