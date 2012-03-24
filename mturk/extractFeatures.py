# extractFeatures.py - takes streams of data and extracts features, creating 
#   a input vector from the histogram/sufficient statistics of the features.
#   Also contains utilities to write out the data in matlab format.

import util
import viz

import numpy
import scipy.io as sio

import argparse
import os


#FEATURE_INDICES = [0,8,9,10,12,13,14,15]
FEATURE_INDICES = range(len(viz.FEATURES))
_NAN = float('nan')

def extractFeatureVectors(data, statisticFn):
  userList = os.listdir(data)
  count = 0
  for user in userList: # collect all segmented data
    userdir = data + '/' + user
    for site in os.listdir(userdir):
      path = userdir + '/' + site
      stream = util.filterKeystrokes(util.openStream(path))
      sessions = util.segmentStream(stream, 600)
      for session in sessions:
        # Generate each feature
        anyEmptyFeatures = False
        vector = [count]
        for ind in FEATURE_INDICES:
          features = viz.collectFeatures(session, viz.FEATURES[ind])
          #if len(features) < 2:
          #  anyEmptyFeatures = True
          #  break
          vector.extend(statisticFn(features))
        if not anyEmptyFeatures: yield vector
    count += 1

def _getMeanAndStdev(dataPoints):
  if len(dataPoints) == 0: return [_NAN,_NAN]
  if len(dataPoints) == 1: return [dataPoints[0],_NAN]
  mean = sum(dataPoints) / len(dataPoints)
  stdev = sum((x-mean) ** 2 for x in dataPoints) / (len(dataPoints) - 1)
  return [mean, stdev]
  
def extractSufficientStatistics(data):
  return extractFeatureVectors(data, _getMeanAndStdev)

parser = argparse.ArgumentParser(description='extracts features to matlab')
parser.add_argument('dir', help='Directory to look up everything')
parser.add_argument('out', help='Output file name')

if __name__ == '__main__':
  args = parser.parse_args()
  data = list(extractSufficientStatistics(args.dir))
  sio.savemat(args.out, {'data':numpy.array(data)})
  print len(data)
