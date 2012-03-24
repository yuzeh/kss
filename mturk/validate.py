#!/usr/bin/env python2.7
import argparse
import collections
import json
import hashlib
import sys

def md5(s): return hashlib.md5(s).hexdigest()
def getTimestamp(d): return d['data']['timestamp']

SALT = 'AI Lab'

parser = argparse.ArgumentParser(description='validate user data')
parser.add_argument('infile', type=argparse.FileType('r'))
parser.add_argument('--hours', type=float, default=5)
parser.add_argument('--nosort', action='store_true')

if __name__ == '__main__':
  args = parser.parse_args()
  obj = json.load(args.infile, object_pairs_hook=collections.OrderedDict)
  
  # Validate all the entries to make sure they meet the hash
  for entry in obj:
    entryHash = md5('AI Lab'
                    + json.dumps(entry['data'],separators=(',',':')))
    if entryHash != entry['hash']:
      raise ValueError('Object does not hash properly: '
                       + json.dumps(entry))
      sys.exit(-1)

  # Check that all the times match and sum up to args.hours hours
  if args.nosort:
    timeline = obj
  else:
    timeline = sorted(obj, key=getTimestamp)

  totalTime = 0
  q = collections.deque()

  for event in timeline:
    item = event['data']
    if item['event'] == 'sessionStart':
      q.append(item['timestamp'])
    elif item['event'] == 'sessionEnd':
      if len(q) == 0:
        print("Warning: sessionEnd before sessionStart at timestamp %d"
              % (item['timestamp'],))
      else:
        startTime = q.popleft()
        endTime = item['timestamp']
        totalTime += (endTime - startTime)

  totalHours = float(totalTime) / 60 / 60 / 1000

  assert(totalHours >= args.hours)
  print(len(q))
  print("Total Hours: %.3f" % (totalHours,))
