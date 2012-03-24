# viz.py - a bunch of utilities for vizualizing a data dump
import util

import argparse
from collections import namedtuple
from itertools import chain
import os
import sys

def collectFeatures(stream, feature):
  return [d for d in feature.fn(stream) if abs(d) < feature.cutoff]

def collectUserFeatures(data, user, featureFunction):
  directory = data + '/' + user
  features = []
  for site in os.listdir(directory):
    path = directory + '/' + site
    stream = util.filterKeystrokes(util.openStream(path))
    features.append(featureFunction(stream))
  return chain(*features)

def createDirectoryIfNotExist(dir):
  if not os.access(dir, os.F_OK):
    os.mkdir(dir)

def _getWordPauses(stream):
  streams = util.segmentStream(stream)
  return chain(*[util.getWordPauses(s) for s in streams])

def _getWordData(stream, index):
  streams = util.segmentStream(stream)
  ret = []
  for s in streams:
    data = list(util.getWordData(s))
    if len(data) > 0: ret.append(zip(*data)[index])

  return chain(*ret)

_getWordLengths   = lambda s: _getWordData(s, 1)
_getWordDurations = lambda s: _getWordData(s, 0)

parser = argparse.ArgumentParser(description='Plots stuff')
parser.add_argument('dir', help='Directory to look up everything')
parser.add_argument('odir', help='Directory to save images to')

Feature = namedtuple('Feature', ['name', 'fn', 'hist', 'cutoff'])
F = Feature

#FEATURES = [ 
#  F('kl-all'    , util.getAllKeystrokeLengths                     , 50, 0.75),
#  F('kl-anon'   , util.getAnonKeystrokeLengths                    , 50, 0.75),
#  F('kl-back'   , util.getBackKeystrokeLengths                    , 50, 0.75),
#  F('kl-ctrl'   , util.getCtrlKeystrokeLengths                    , 50, 0.75),
#  F('kl-arrow'  , util.getArrowKeystrokeLengths                   , 50, 0.75),
#  F('kl-enter'  , util.getEnterKeystrokeLengths                   , 50, 0.75),
#  F('kl-pgnav'  , util.getPgNavKeystrokeLengths                   , 50, 0.75),
#  F('kl-shift'  , util.getShiftKeystrokeLengths                   , 50, 0.75),
#  F('kl-space'  , util.getSpaceKeystrokeLengths                   , 50, 0.75),
#  F('kl-delete' , util.getDeleteKeystrokeLengths                  , 50, 0.75),
#  F('word-dur'  , _getWordDurations                               , 50, 10),
#  F('word-len'  , _getWordLengths                                 , 50, 30),
#  F('ko'        , util.getKeyOverlaps                             , 50, 2),
#  F('wp'        , _getWordPauses                                  , 50, 10),
#  F('md-shift'  , lambda s: util.getModifierDelays(s, util._SHIFT), 50, 10),
#  F('kk-shift'  , lambda s: util.getKeyToKeys(s, util._SHIFT)     , 50, 60),
#  F('kk-ctrl'   , lambda s: util.getKeyToKeys(s, util._CTRL)      , 50, 60)
#]

FEATURES = [ 
  F('kl-all'    , util.getAllKeystrokeLengths                     , 50, 2),
  F('kl-anon'   , util.getAnonKeystrokeLengths                    , 50, 2),
  F('kl-back'   , util.getBackKeystrokeLengths                    , 50, 2),
  F('kl-ctrl'   , util.getCtrlKeystrokeLengths                    , 50, 2),
  F('kl-arrow'  , util.getArrowKeystrokeLengths                   , 50, 2),
  F('kl-enter'  , util.getEnterKeystrokeLengths                   , 50, 2),
  F('kl-pgnav'  , util.getPgNavKeystrokeLengths                   , 50, 2),
  F('kl-shift'  , util.getShiftKeystrokeLengths                   , 50, 2),
  F('kl-space'  , util.getSpaceKeystrokeLengths                   , 50, 2),
  F('kl-delete' , util.getDeleteKeystrokeLengths                  , 50, 2),
  F('word-dur'  , _getWordDurations                               , 50, 10),
  F('word-len'  , _getWordLengths                                 , 50, 30),
  F('ko'        , util.getKeyOverlaps                             , 50, 2),
  F('wp'        , _getWordPauses                                  , 50, 10),
  F('md-shift'  , lambda s: util.getModifierDelays(s, util._SHIFT), 50, 10),
  F('kk-shift'  , lambda s: util.getKeyToKeys(s, util._SHIFT)     , 50, 60),
  F('kk-ctrl'   , lambda s: util.getKeyToKeys(s, util._CTRL)      , 50, 60)
]

if __name__ == '__main__':
  import matplotlib.pyplot as plt

  args = parser.parse_args()
  createDirectoryIfNotExist(args.odir)

  # do plots of user-vs-user stuff
  userList = os.listdir(args.dir)
  for v in FEATURES:
    userFeatures = {}
    allFeatures = []
    for user in userList:
      features = [f for f in collectUserFeatures(args.dir, user, v.fn)
                    if abs(f) < v.cutoff]

      if len(features) == 0: continue
      allFeatures.extend(features)
      userFeatures[user] = features

    # create histogram for all users
    plt.clf()
    bins = plt.hist(allFeatures, v.hist)[1]

    for user, features in userFeatures.iteritems():
      plt.clf()
      plt.hist(features, bins)
      plt.title('%s user %s' % (v.name, user))
      plt.savefig('%s/%s-%s.png' % (args.odir, v.name, user))

