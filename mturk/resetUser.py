#!/usr/bin/env python2.7

import boto.mturk
import boto.mturk.connection
import boto.mturk.qualification
import argparse
from settings import *

parser = argparse.ArgumentParser(description='Resets a User for part 2')
parser.add_argument('worker_id')
parser.add_argument('--sandbox', action='store_true')

if __name__ == '__main__':
  args = parser.parse_args()

  if args.sandbox:
    qualificationId = QUALIFICATION_ID_S
    host = HOST
  else:
    qualificationId = QUALIFICATION_ID
    host = None

  connection = boto.mturk.connection.MTurkConnection(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    host=host)
  connection.assign_qualification(qualificationId, args.worker_id, 100, False)

