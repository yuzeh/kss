#!/usr/bin/env python2.7
from util import Object, openJsonStream, segmentJsonStream
from keycodes import KEYCODES

import argparse
import math
from collections import defaultdict, Counter
import itertools
from urlparse import urlparse
import os.path

import numpy as np
from scipy.stats import scoreatpercentile
import matplotlib
import matplotlib.pylab as plt

key2kc = KEYCODES
kc2key = dict((v,k) for k,v in key2kc.iteritems())

def IQR(data):
  return scoreatpercentile(data,75) - scoreatpercentile(data,25)

def createHistogram(title, xlabel, data, filename):
  if len(data) == 0: return
  # Testing IQR thingy
  width = 2.0 * IQR(data) / (len(data)**(1.0/3.0))
  if width == 0.0:
    bins = 20
  else:
    bins = math.floor((max(data) - min(data)) / width * 1.1)
  plt.figure()
  plt.title(title)
  plt.xlabel(xlabel)
  plt.hist(data, bins=bins)
  plt.savefig(filename)
  plt.clf()
  plt.close()

def findCommonEdges(*args):
  d = np.concatenate(args)
  width = 3.0 * IQR(d) / (len(d) ** (1/3.0))
  if width == 0.0:
    bins = 20
  else:
    bins = math.ceil((max(d) - min(d)) / width * 1.1)
  h, edges = np.histogram(d, bins=bins)
  return edges

def createMultiHistograms(title, xlabel, fname, data, users):
  edges = findCommonEdges(*data)
  pts = []
  for i in range(len(data)):
    h, edges = np.histogram(data[i], bins=edges, normed=True)
    pts.append(h)
  plt.figure()
  plt.title(title)
  plt.xlabel(xlabel)
  plt.plot(edges[:-1] - np.diff(edges) / 2.0, np.array(pts).T)
  plt.savefig(fname)
  plt.clf()
  plt.close()

def compareTwoUsers(data1, data2, outdir):
  """Compares data for two users. Currently plots difference in peaks for
  the users on presslengths for different keycodes."""
  def computePeakDifference(d1,d2):
    edges = findCommonEdges(d1, d2)
    h1, e = np.histogram(d1, bins=edges, normed=True)
    h2, e = np.histogram(d2, bins=edges, normed=True)
    a1, a2 = np.argmax(h1), np.argmax(h2)
    diff = (edges[a1] + edges[a1+1] - edges[a2] - edges[a2+1]) / 2.0
    return diff

  commonKeys = set(data1.keystrokePLs_key.keys()) \
             & set(data2.keystrokePLs_key.keys())
  peakDiffs = []
  for key in commonKeys:
    dat1 = data1.keystrokePLs_key[key]
    dat2 = data2.keystrokePLs_key[key]
    peakDiffs.append(computePeakDifference(dat1, dat2))
  peakDiffs.append(computePeakDifference(data1.keystrokePLs,
                                         data2.keystrokePLs))
  edges = findCommonEdges(peakDiffs)
  plt.figure()
  plt.hist(peakDiffs, bins=edges)
  plt.title('Peak Differences for Keystroke PL for %s and %s'
              % (data1.user, data2.user))
  plt.xlabel('Time (seconds)')
  plt.savefig('%s/%s_%s_kPLpeakDiff.pdf' % (outdir, data1.user, data2.user))
  plt.close()

def collectData(infile):
  data = Object()
  userName = os.path.split(infile.name)[1].split('.')[0]

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
  domainVisits = Counter()
  websiteVisitLength = [] # can't currently get this one
  websiteVisitLength_domain = defaultdict(list) # same here
  wordLengths = [] # TODO implement
  wordDurations = [] # TODO implement

  # Bigram model stuff
  bigramModel = defaultdict(lambda: defaultdict(list))

  # go through the segmented data (this is just a lot of code)
  stream = openJsonStream(infile)
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
      domains.add(domain)
      domainVisits.update([domain])
      keystrokesPressed += len(page.keystrokes)

      page.keystrokes.sort(key=lambda x: x.timestamp)
      pKey = None
      pStart = 0
      pEnd = 0
      for keystroke in page.keystrokes:
        pl = keystroke.pressLength
        kc = keystroke.keycode
        start = keystroke.timestamp / 1000.0
        end = start + pl

        keystrokePLs.append(pl)
        keystrokePLs_key[kc].append(pl)
        keystrokePLs_domain[domain].append(pl)
        keystrokeFreqs[kc] += 1

        if pKey is not None:
          bigramModel[pKey][kc].append((end-pStart, start-pEnd, start-pStart))
        pKey = kc
        pStart = start
        pEnd = end

        timeSpent += keystroke.pressLength

    sessionLengths.append(session.time)
    keystrokesPressedPerSession.append(keystrokesPressed)
    if session.time > 0.0:
      timeSpentPressingKeys.append(timeSpent / float(session.time))
    websitesVisitedPerSession.append(len(websites))
    domainsVisitedPerSession.append(len(domains))

  # store them all in data.
  data.keystrokePLs = np.array(keystrokePLs)
  data.keystrokePLs_key = dict(
     (k,np.array(v)) for (k,v) in keystrokePLs_key.iteritems())
  data.keystrokePLs_domain = dict(
     (k,np.array(v)) for (k,v) in keystrokePLs_domain.iteritems())
  data.keystrokeFreqs = np.array(keystrokeFreqs)
  data.sessionLengths = np.array(sessionLengths)
  data.keystrokesPressedPerSession = np.array(keystrokesPressedPerSession)
  data.timeSpentPressingKeys = np.array(timeSpentPressingKeys)
  data.websitesVisitedPerSession = np.array(websitesVisitedPerSession)
  data.domainsVisitedPerSession = np.array(domainsVisitedPerSession)
  data.domainVisits = domainVisits
  data.websiteVisitLength = websiteVisitLength # TODO implement
  data.websiteVisitLength_domain = websiteVisitLength_domain # TODO implement
  data.wordLengths = np.array(wordLengths) # TODO implement
  data.wordDurations = np.array(wordDurations) # TODO implement
  data.bigramModel = bigramModel
  data.user = userName

  # TODO: finish
  return data

def visualizeBigramModel(data, outdir):
  bigramModel = data.bigramModel
  keycodes = sorted(list(KEYCODES.values()))
  keyToIndex = dict((v,k) for (k,v) in enumerate(keycodes))
  fullLength = np.zeros([len(keycodes)] * 2)
  gap        = np.zeros([len(keycodes)] * 2)
  startStart = np.zeros([len(keycodes)] * 2)
  for (k,v) in bigramModel.iteritems():
    for (m,n) in v.iteritems():
      (fl, g, ss) = zip(*n)
      if len(fl) > 0: fullLength[keyToIndex[k],keyToIndex[m]] = np.mean(fl)
      if len(g ) > 0: gap[keyToIndex[k],keyToIndex[m]] = np.mean(g)
      if len(ss) > 0: startStart[keyToIndex[k],keyToIndex[m]] = np.mean(ss)
    # normalize!
    if np.sum(fullLength[keyToIndex[k]]) > 0:
      fullLength[keyToIndex[k]] /= np.sum(fullLength[keyToIndex[k]])
    if np.sum(gap[keyToIndex[k]]) > 0:
      gap[keyToIndex[k]] /= np.sum(gap[keyToIndex[k]])
    if np.sum(startStart[keyToIndex[k]]) > 0:
      startStart[keyToIndex[k]] /= np.sum(startStart[keyToIndex[k]])

  fullLength = np.array(fullLength)
  gap = np.array(gap)
  startStart = np.array(startStart)

  plt.figure()
  plt.imshow(fullLength, interpolation='none')
  plt.savefig('%s/%s_bigram_fullLength.pdf' % (outdir, data.user))
  plt.close()

  plt.figure()
  plt.imshow(gap, interpolation='none')
  plt.savefig('%s/%s_bigram_gap.pdf' % (outdir, data.user))
  plt.close()

  plt.figure()
  plt.imshow(startStart, interpolation='none')
  plt.savefig('%s/%s_bigram_start-start.pdf' % (outdir, data.user))
  plt.close()

def visualizeBigramModelText(data):
  bigramModel = data.bigramModel
  print('Bigram Model for user %s' % data.user)

  # pairs we want to visualize
  allKeys = set(kc2key.iterkeys())
  for (k,v) in bigramModel.iteritems():
    print('  Key1( %-6s )' % kc2key[k])
    for (m,n) in v.iteritems():
      (fl, gap, ss) = zip(*n)
      print('    Key2( %-6s ) count: %d' % (kc2key[m], len(n)))
      print('      Full Length: meanPL: %f - stdevPL: %f'
                    % (np.mean(fl), np.std(fl)))
      print('      Gap        : meanPL: %f - stdevPL: %f'
                    % (np.mean(gap), np.std(gap)))
      print('      Start-start: meanPL: %f - stdevPL: %f'
                    % (np.mean(ss), np.std(ss)))

def saveSinglePlots(data, outdir):
  # unload all data
  keystrokePLs = data.keystrokePLs
  keystrokePLs_key = data.keystrokePLs_key
  keystrokePLs_domain = data.keystrokePLs_domain
  keystrokeFreqs = data.keystrokeFreqs
  sessionLengths = data.sessionLengths
  keystrokesPressedPerSession = data.keystrokesPressedPerSession
  timeSpentPressingKeys = data.timeSpentPressingKeys
  websitesVisitedPerSession = data.websitesVisitedPerSession
  domainsVisitedPerSession = data.domainsVisitedPerSession
  domainVisits = data.domainVisits
  user = data.user

  keystrokePLs = keystrokePLs[keystrokePLs < 3]
  createHistogram(
    'Keystroke Press Lengths for ' + user,
    'Seconds', keystrokePLs,
    '%s/%s_keystrokePLs.pdf' % (outdir, user)
  )

  for (k,v) in keystrokePLs_key.iteritems():
    v = v[v < 3]
    createHistogram(
      'Keystroke Press Lengths for %s, keycode: %d' % (user, k),
      'Seconds', v,
      '%s/%s_keystrokePLs_key_%d.pdf' % (outdir, user, k)
    )

  for (k,v) in keystrokePLs_domain.iteritems():
    v = v[v < 3]
    createHistogram(
      'Keystroke Press Lengths for %s, domain: %s' % (user, k),
      'Seconds', v,
      '%s/%s_keystrokePLs_domain_%s.pdf' % (outdir, user, k)
    )

  createHistogram(
    'Session Lengths for %s' % user,
    'Seconds', sessionLengths,
    '%s/%s_sessionLengths.pdf' % (outdir, user)
  )

  createHistogram(
    'Keystrokes/Session for %s' % user,
    'Number of Keystrokes', keystrokesPressedPerSession,
    '%s/%s_keystrokesPerSession.pdf' % (outdir, user)
  )

  createHistogram(
    'Time spent Pressing Keys per Session for %s' % user,
    'Percentage', timeSpentPressingKeys,
    '%s/%s_timeSpentPressingKeys.pdf' % (outdir, user)
  )

  createHistogram(
    'Websites Visited per Session for %s' % user,
    'Number of Websites', websitesVisitedPerSession,
    '%s/%s_websitesVisitedPerSession.pdf' % (outdir, user)
  )

  createHistogram(
    'Domains Visited per Session for %s' % user,
    'Number of Domains', domainsVisitedPerSession,
    '%s/%s_domainsVisitedPerSession.pdf' % (outdir, user)
  )

  # create bar chart with domains on the x-axis
  N = len(domainVisits.keys())
  ind = np.arange(N)
  width = 0.8
  domains, counts = zip(*domainVisits.iteritems())
  plt.bar(ind, counts, width)
  plt.title('Domains visited by %s' % user)
  plt.xticks(ind + width / 2, domains, rotation='vertical')
  plt.savefig('%s/%s_domainVisits.pdf' % (outdir, user))
  plt.gcf().subplots_adjust(bottom=1.0)
  plt.close()

  visualizeBigramModel(data, outdir)

parser = argparse.ArgumentParser(description='Looks at AMT gathered data')
parser.add_argument('outdir')
parser.add_argument('infiles', type=argparse.FileType('r'), nargs='+')
parser.add_argument('--noplots', action='store_true')

if __name__ == '__main__':
  args = parser.parse_args()
  if args.outdir[-1] == '/': args.outdir = args.outdir[:-1]

  users = []
  data = []
  for infile in args.infiles:
    datum = collectData(infile)
    data.append(datum)
    if not args.noplots: saveSinglePlots(datum, args.outdir)

  createMultiHistograms(
     'Keystroke PLs', 'Press length', '%s/ALL_keystrokePLs.pdf' % args.outdir,
     [d.keystrokePLs[d.keystrokePLs<3] for d in data], [d.user for d in data])

  for i in range(230):
    if all(i in d.keystrokePLs_key for d in data):
      datum = [d.keystrokePLs_key[i] for d in data]
      createMultiHistograms(
        'Keystroke PLs (Key=%s)' % kc2key[i], 'Press length',
        '%s/ALL_keystrokePLs_key_%d.pdf' % (args.outdir, i),
        [d[d < 3] for d in datum], [d.user for d in data])

  for x in data[0].keystrokePLs_domain.iterkeys():
    if all(x in d.keystrokePLs_domain for d in data):
      datum = [d.keystrokePLs_domain[x] for d in data]
      createMultiHistograms(
        'Keystroke PLs (Domain=%s)' % x, 'Press length',
        '%s/ALL_keystrokePLs_key_%s.pdf' % (args.outdir, x),
        [d[d < 3] for d in datum], [d.user for d in data])

  if len(data) > 1: compareTwoUsers(data[0], data[1], args.outdir)

