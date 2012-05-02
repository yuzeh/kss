#!/usr/bin/env python2.7
from util import Object, openJsonStream, segmentJsonStream
from keycodes import KEYCODES

import argparse
from collections import defaultdict, Counter, namedtuple
import errno
import itertools
import math
import os
import os.path
from urlparse import urlparse

import numpy as np
from scipy.stats import scoreatpercentile
import matplotlib
matplotlib.use('pdf')
import matplotlib.cm as cm
import matplotlib.pylab as plt
from matplotlib.colors import LogNorm

Inf = float('Inf')
NUMBER_OF_KEYCODES = 230
KEY2KC = KEYCODES
KC2KEY = dict((v,k) for k,v in KEY2KC.iteritems())

# Start new code to make this file more maintainable

from string import Formatter as _F
import copy

OutputInfo = namedtuple('OutputInfo', ['name', 'title', 'xlabel', 'ylabel'])

class KeywordOutputInfo(object):
  """A factory for OutputInfo objects, which uses a template based on the
  provided base OutputInfo object.

  Usage:
  >>> template = OutputInfo('{foo}', '{bar}', '23', '{foo}{bar}')
  >>> kOutput = KeywordOutputInfo(template)
  >>> kOutput.format(foo='a', bar=1)
  OutputInfo(name='a', title='1', xlabel='23', ylabel='a1')

  >>> kOutput = KeywordOutputInfo(template)
  >>> newFormat = kOutput.bind(foo='a')
  >>> newFormat.format(bar=1)
  OutputInfo(name='a', title='1', xlabel='23', ylabel='a1')
  """

  def __init__(self, base):
    """Constructor takes one argument: a template OutputInfo object with
    a format string with *only* name-format objects (e.g. '%(foo)s')."""
    self.base = base
    self.keywords = {}

  def bind(self, **kwargs):
    """Returns a new KeywordOutputInfo instance with the given keywords
    already bound."""
    ret = KeywordOutputInfo(self.base)
    ret.keywords.update(**kwargs)
    return ret

  def format(self, **kwargs):
    """Returns an OutputInfo object with all of the format fields from the
    template string filled in."""
    tempKeywords = copy.deepcopy(self.keywords)
    tempKeywords.update(kwargs)
    args = [b.format(**tempKeywords) for b in self.base]
    return OutputInfo(*args)

## Leave in as long as I'm testing this module
if __name__ == "__main__":
  import doctest
  import sys
  doctest.testmod()
  sys.exit(0)

# Some example uses of KeywordOutputInfo (which are useful in my case)
SingleBigramFormat = KeywordOutputInfo(OutputInfo(
    '{outdir}/{user}/bigram_{type}.pdf', '', 'Key #2', 'key #1'))
KPLHistFormat = KeywordOutputInfo(OutputInfo(
    '{outdir}/{user}/keystrokePLs_{type}_{item}.pdf',
    'Keystroke Press Lengths for {user}, {type}: {item}',
    'Seconds',
    ''))
KPLKeyHistFormat = KPLHistFormat.bind(type='key')
KPLDomainHistFormat = KPLHistFormat.bind(type='domain')
KPLAllHistFormat = KPLHistFormat.bind(type='', item='')

SingleHistFormat = KeywordOutputInfo(OutputInfo(
    '{outdir}/{user}/{field}.pdf',
    '{data_descrip} for {user}',
    '{data_xlabel}',
    ''))

SLFormat = SingleHistFormat.bind(
    field='SL',
    data_descrip='Session Lengths',
    data_xlabel='Seconds')
KPerSFormat = SingleHistFormat.bind(
    field='KPerS',
    data_descrip='Keystrokes per Session',
    data_xlabel='Number of Keystrokes')
KPTimePerSFormat = SingleHistFormat.bind(
    field='KPTimePerS',
    data_descrip='Time Spent Pressing Keys per Session',
    data_xlabel='Percentage')
WVPerSFormat = SingleHistFormat.bind(
    field='WVPerS',
    data_descrip='Websites Visited per Session',
    data_xlabel='Count')
DVPerSFormat = SingleHistFormat.bind(
    field='DVPerS',
    data_descrip='Domains Visited per Session',
    data_xlabel='Count')

## Begin code for PlotInfo classes

## kwargGenerators (now just getBins)
def getBins(data):
  """Sets proper number of bins for data to be displayed by histogram"""
  width = 2.0 * IQR(data) / ( len(data) ** ( 1. / 3. ) )
  if width == 0.0: bins = 20
  else: bins = math.floor((max(data) - min(data)) / width * 1.1)
  return ('bins', bins)

PlotInfo = namedtuple('PlotInfo',
    ('fn', 'field', 'outformat', 'kwargGenerators', 'options'))

SL = PlotInfo(plt.hist, 'SL', SLFormat, [getBins], [])
KPerS = PlotInfo(plt.hist, 'KPerS', KPerSFormat, [getBins], [])
KPTimePerS = PlotInfo(plt.hist, 'KPTimePerS', KPTimePerSFormat, [getBins], [])
WVPerS = PlotInfo(plt.hist, 'WVPerS', WVPerSFormat, [getBins], [])
DVPerS = PlotInfo(plt.hist, 'DVPerS', DVPerSFormat, [getBins], [])

def requestPlot(data, fn, outputInfo, kwargs, opts):
  """This function is called every time the user wants to create a plot."""
  plt.figure()

  # Plot specific code
  fn(data, **kwargs)
  plt.title(outputInfo.title)
  plt.xlabel(outputInfo.xlabel)
  plt.ylabel(outputInfo.ylabel)

  # Process other plot options
  if 'colorbar' in plotInfo.options:
    plt.colorbar()

  plt.savefig(outputInfo.name)
  plt.close()

def getPlot(data, pi, runtimeArgs):
  """Gets a certain plot about a certain person. With runtimeArgs attached."""
  # process data (which right now is just extracting the field)
  pData = getattr(data, pi.field)

  # First form outputInfo object
  outputInfo = pi.outformat.format(
      outdir=runtimeArgs.outdir,
      user=data.user,
      field=pi.field)

  # Then, form kwargs
  def a(obj):
    if hasattr(obj, '__call__'): return obj(pData)
    else: return obj
  kwargs = dict(a(g) for g in pi.kwargGenerators)

  # Request the plot!
  requestPlot(pData, pi.fn, outputInfo, kwargs, pi.options)

def singlePlots(data):
  """Saves all histograms for a single user."""
  # TODO implement
  pass

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else: raise

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
  plt.plot(edges[:-1] - np.diff(edges) / 2.0,np.array(pts).T)
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
  mkdir_p('%s/%s_%s' % (outdir, data1.user, data2.user))
  plt.savefig('%s/%s_%s/kPLpeakDiff.pdf' % (outdir, data1.user, data2.user))
  plt.close()

  visualizeDifferenceBigramModel(data1, data2, outdir)

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

def compileBigramModel(data):
  CENTER_FN = np.mean
  COUNT_CUTOFF = 5
  TIME_CUTOFF = 2.0
  bigramModel = data.bigramModel
  keycodes = sorted(list(KEYCODES.values()))
  keyToIndex = dict((v,k) for (k,v) in enumerate(keycodes))
  fullLength = np.zeros([len(keycodes)] * 2) + -Inf
  gap        = np.zeros([len(keycodes)] * 2) + -Inf
  startStart = np.zeros([len(keycodes)] * 2) + -Inf
  for (k,v) in bigramModel.iteritems():
    for (m,n) in v.iteritems():
      (fl, g, ss) = zip(*n)
      if len(fl) >= COUNT_CUTOFF and abs(CENTER_FN(fl)) < TIME_CUTOFF:
        fullLength[keyToIndex[k],keyToIndex[m]] = CENTER_FN(fl)
      if len(g ) >= COUNT_CUTOFF and abs(CENTER_FN(g )) < TIME_CUTOFF:
        gap[keyToIndex[k],keyToIndex[m]] = CENTER_FN(g)
      if len(ss) >= COUNT_CUTOFF and abs(CENTER_FN(ss)) < TIME_CUTOFF:
        startStart[keyToIndex[k],keyToIndex[m]] = CENTER_FN(ss)

  bigram = Object()
  bigram.fullLength  = fullLength
  bigram.gap         = gap
  bigram.startStart  = startStart

  import scipy.io as sio
  sio.savemat('%s_bigram.mat' % data.user,
      {'fullLength': fullLength, 'gap': gap, 'startStart': startStart })
  return bigram

def keyBigramImshow(data, fname):
  plt.figure()
  plt.imshow(data, interpolation='none')
  plt.colorbar()
  plt.xlabel('Key #2'); plt.ylabel('Key #1')
  plt.savefig(fname)
  plt.close()

def visualizeDifferenceBigramModel(data1, data2, outdir):
  """Takes data from two users and computes the difference in each of their
  bigrams"""
  b1 = compileBigramModel(data1)
  b2 = compileBigramModel(data2)

  fullLength = b1.fullLength - b2.fullLength
  gap = b1.gap - b2.gap
  startStart = b1.startStart - b2.startStart

  fullLength[np.isinf(fullLength)] = -Inf
  gap[np.isinf(gap)] = -Inf
  startStart[np.isinf(startStart)] = -Inf

  keyBigramImshow(fullLength, '%s/%s_%s/bigram_fullLength_diff.pdf'
      % (outdir, data1.user, data2.user))
  keyBigramImshow(gap, '%s/%s_%s/bigram_gap_diff.pdf'
      % (outdir, data1.user, data2.user))
  keyBigramImshow(startStart, '%s/%s_%s/bigram_startStart_diff.pdf'
      % (outdir, data1.user, data2.user))

def visualizeBigramModel(data, outdir):
  b = compileBigramModel(data)

  keyBigramImshow(b.fullLength,
      '%s/%s/bigram_fullLength.pdf' % (outdir, data.user))
  keyBigramImshow(b.gap,
      '%s/%s/bigram_gap.pdf' % (outdir, data.user))
  keyBigramImshow(b.startStart,
      '%s/%s/bigram_start-start.pdf' % (outdir, data.user))

def visualizeBigramModelText(data):
  bigramModel = data.bigramModel
  print('Bigram Model for user %s' % data.user)

  # pairs we want to visualize
  allKeys = set(KC2KEY.iterkeys())
  for (k,v) in bigramModel.iteritems():
    print('  Key1( %-6s )' % KC2KEY[k])
    for (m,n) in v.iteritems():
      (fl, gap, ss) = zip(*n)
      print('    Key2( %-6s ) count: %d' % (KC2KEY[m], len(n)))
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

  mkdir_p('%s/%s' % (outdir, user))
  keystrokePLs = keystrokePLs[keystrokePLs < 3]
  createHistogram(
    'Keystroke Press Lengths for ' + user,
    'Seconds', keystrokePLs,
    '%s/%s/keystrokePLs.pdf' % (outdir, user)
  )

  for (k,v) in keystrokePLs_key.iteritems():
    v = v[v < 3]
    createHistogram(
      'Keystroke Press Lengths for %s, keycode: %d' % (user, k),
      'Seconds', v,
      '%s/%s/keystrokePLs_key_%d.pdf' % (outdir, user, k)
    )

  for (k,v) in keystrokePLs_domain.iteritems():
    v = v[v < 3]
    createHistogram(
      'Keystroke Press Lengths for %s, domain: %s' % (user, k),
      'Seconds', v,
      '%s/%s/keystrokePLs_domain_%s.pdf' % (outdir, user, k)
    )

  createHistogram(
    'Session Lengths for %s' % user,
    'Seconds', sessionLengths,
    '%s/%s/sessionLengths.pdf' % (outdir, user)
  )

  createHistogram(
    'Keystrokes/Session for %s' % user,
    'Number of Keystrokes', keystrokesPressedPerSession,
    '%s/%s/keystrokesPerSession.pdf' % (outdir, user)
  )

  createHistogram(
    'Time spent Pressing Keys per Session for %s' % user,
    'Percentage', timeSpentPressingKeys,
    '%s/%s/timeSpentPressingKeys.pdf' % (outdir, user)
  )

  createHistogram(
    'Websites Visited per Session for %s' % user,
    'Number of Websites', websitesVisitedPerSession,
    '%s/%s/websitesVisitedPerSession.pdf' % (outdir, user)
  )

  createHistogram(
    'Domains Visited per Session for %s' % user,
    'Number of Domains', domainsVisitedPerSession,
    '%s/%s/domainsVisitedPerSession.pdf' % (outdir, user)
  )

  # create bar chart with domains on the x-axis
  N = len(domainVisits.keys())
  ind = np.arange(N)
  width = 0.8
  domains, counts = zip(*domainVisits.iteritems())
  plt.bar(ind, counts, width)
  plt.title('Domains visited by %s' % user)
  plt.xticks(ind + width / 2, domains, rotation='vertical')
  plt.gcf().subplots_adjust(bottom=0.5)
  plt.savefig('%s/%s/domainVisits.pdf' % (outdir, user))
  plt.close()

  visualizeBigramModel(data, outdir)
