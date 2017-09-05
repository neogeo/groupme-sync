import logging
import sys

import arrow
import boto3

import config

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdoutput = logging.StreamHandler(sys.stdout)
stdoutput.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(stdoutput)


def upload(filepath, key):
    s3 = boto3.resource('s3')

    logger.info('uploading {} to S3, located at {}'.format(key, filepath))
    total_time = arrow.now()

    with open(filepath, 'rb') as rb:
        s3.Bucket(config.S3_BUCKET).put_object(Key=key, Body=rb, Tagging='groupme=true')

    total_time = arrow.now() - total_time
    logger.info('finished uploading {} to S3. took {} seconds'.format(key, total_time))
