#!/usr/bin/env python2.7
from util import Object, openJsonStream, segmentJsonStream

import argparse
import math
from collections import defaultdict, Counter
from urlparse import urlparse
import os.path

import numpy as np
from scipy.stats import scoreatpercentile
import matplotlib
import matplotlib.pylab as plt

def IQR(data):
  return scoreatpercentile(data,75) - scoreatpercentile(data,25)

def createHistogram(title, xlabel, data, bins, filename):
  if len(data) == 0: return
  # Testing IQR thingy
  width = 2.0 * IQR(data) / (len(data)**(1.0/3.0))
  if width == 0.0:
    bins = 20
  else:
    bins = math.floor((max(data) - min(data)) / width * 1.1)

  fig = plt.figure(1)
  plt.cla()
  plt.title(title)
  plt.xlabel(xlabel)
  plt.hist(data, bins=bins)
  fig.savefig(filename)
  fig.clf()
  plt.close(fig)

parser = argparse.ArgumentParser(description='Looks at AMT gathered data')
parser.add_argument('infile', type=argparse.FileType('r'))
parser.add_argument('outdir')

if __name__ == '__main__':
  args = parser.parse_args()

  userName = os.path.split(args.infile.name)[1].split('.')[0]
  if args.outdir[-1] == '/': args.outdir = args.outdir[:-1]

  # initialize all the container vars
  keystrokePLs = []
  keystrokePLs_key = defaultdict(list)
  keystrokePLs_domain = defaultdict(list)
  keystrokeFreqs = [0] * 250

  sessionLengths = []
  keystrokesPressedPerSession = []
  timeSpentPressingKeys = []
  websitesVisitedPerSession = []
  domainsVisitedPerSession = []
  #websiteVisitLength = [] # can't currently get this one
  #websiteVisitLength_domain = defaultdict(list) # same here
  wordLengths = []
  wordDurations = []

  # Bigram model stuff
  bigramModel = [ [[] for i in range(225)] for j in range(225) ]

  # go through the segmented data and the non segmented data
  stream = openJsonStream(args.infile)
  sessions = segmentJsonStream(stream)

  for session in sessions:
    keystrokesPressed = 0
    timeSpent = 0.0
    domains = set() 
    websites = set()
    for page in session.data:
      if page.url is None:
        domain = '*'
        page.url = '*'
      else:
        domain = urlparse(page.url).netloc
      
      websites.add(page.url)
      domains.add(page.url)
      keystrokesPressed += len(page.keystrokes)

      previousKey = None
      for keystroke in page.keystrokes:
        pl = keystroke.pressLength
        kc = keystroke.keycode
        keystrokePLs.append(pl)
        keystrokePLs_key[kc].append(pl)
        keystrokePLs_domain[domain].append(pl)
        keystrokeFreqs[kc] += 1

        if previousKey is not None:
          bigramModel[previousKey][kc].append(pl)
        previousKey = kc

        timeSpent += keystroke.pressLength

    sessionLengths.append(session.time)
    keystrokesPressedPerSession.append(keystrokesPressed)
    if session.time > 0.0:
      timeSpentPressingKeys.append(timeSpent / float(session.time))
    websitesVisitedPerSession.append(len(websites))
    domainsVisitedPerSession.append(len(domains))
  # TODO: finish

  # convert everything to numpy arrays
  keystrokePLs = np.array(keystrokePLs)
  keystrokePLs = keystrokePLs[keystrokePLs < 3]
  createHistogram(
    'Keystroke Press Lengths for ' + userName,
    'Seconds',
    keystrokePLs, 100,
    '%s/%s_keystrokePLs.pdf' % (args.outdir, userName)
  )
  
  for (k,v) in keystrokePLs_key.iteritems():
    v = np.array(v)
    v = v[v < 3]
    keystrokePLs_key[k] = v
    createHistogram(
      'Keystroke Press Lengths for %s, keycode: %d' % (userName, k),
      'Seconds',
      v, 100,
      '%s/%s_keystrokePLs_key_%d.pdf' % (args.outdir, userName, k)
    )

  for (k,v) in keystrokePLs_domain.iteritems():
    v = np.array(v)
    v = v[v < 3]
    keystrokePLs_domain[k] = v
    createHistogram(
      'Keystroke Press Lengths for %s, domain: %s' % (userName, k),
      'Seconds',
      v, 100,
      '%s/%s_keystrokePLs_domain_%s.pdf' % (args.outdir, userName, k)
    )

  sessionLengths = np.array(sessionLengths)
  createHistogram(
    'Session Lengths for %s' % userName,
    'Seconds',
    sessionLengths, 20,
    '%s/%s_sessionLengths.pdf' % (args.outdir, userName)
  )

  keystrokesPressedPerSession = np.array(keystrokesPressedPerSession)
  createHistogram(
    'Keystrokes/Session for %s' % userName,
    'Number of Keystrokes',
    keystrokesPressedPerSession, 20,
    '%s/%s_keystrokesPerSession.pdf' % (args.outdir, userName)
  )

  timeSpentPressingKeys = np.array(timeSpentPressingKeys)
  createHistogram(
    'Time spent Pressing Keys per Session for %s' % userName,
    'Percentage',
    timeSpentPressingKeys, 20,
    '%s/%s_timeSpentPressingKeys.pdf' % (args.outdir, userName)
  )

  websitesVisitedPerSession = np.array(websitesVisitedPerSession)
  createHistogram(
    'Websites Visited per Session for %s' % userName,
    'Number of Websites',
    websitesVisitedPerSession, 20,
    '%s/%s_websitesVisitedPerSession.pdf' % (args.outdir, userName)
  )

  domainsVisitedPerSession = np.array(domainsVisitedPerSession)
  createHistogram(
    'Domains Visited per Session for %s' % userName,
    'Number of Domains',
    domainsVisitedPerSession, 20,
    '%s/%s_domainsVisitedPerSession.pdf' % (args.outdir, userName)
  )

  wordLengths = np.array(wordLengths)
  wordDurations = np.array(wordDurations)

