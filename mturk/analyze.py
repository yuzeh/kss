#!/usr/bin/env python2.7
import time
import inspect
import json
import hashlib
import viz
import argparse
import itertools

## Code for loading/saving the functions that were called before
FUNCTION_HASH_FNAME = 'PLOT_CACHE'
def loadFunctionHashes(fname):
  try: return json.load(open(fname))
  except IOError: return {}

def saveFunctionHashes(fname, fhash):
  json.dump(fhash, open(fname, 'w'))

def hashFunction(fn):
  m = hashlib.md5()
  m.update(inspect.getsource(fn))
  return m.hexdigest()

## Code for evaluating whether a function needs to be run, and then running
## that function if it does. Includes timing information.
def runFunction(bits, fn, args):
  if not bits[fn.__name__]:
    start_time = time.time()
    fn(*args)
    print('Function %s ran in %.2f s' % (fn.__name__, time.time() - start_time))
  else:
    print('Function %s unchanged, continuing' % fn.__name__)

def createFunctionBitmap(fnHash, module):
  bits = {}
  newHash = {}
  for u, v in inspect.getmembers(module):
    if inspect.isfunction(v):
      hash = hashFunction(v)
      newHash[v.__name__] = hash
      if v.__name__ in fnHash and fnHash[v.__name__] == hash:
        bits[v.__name__] = True
      else:
        bits[v.__name__] = False
  return (bits, newHash)

parser = argparse.ArgumentParser(description='Looks at AMT gathered data')
parser.add_argument('outdir')
parser.add_argument('infiles', type=argparse.FileType('r'), nargs='+')
parser.add_argument('--noplots', action='store_true')

if __name__ == '__main__':
  # Load old function hashes
  functionHashes = loadFunctionHashes(FUNCTION_HASH_FNAME)
  bits, newHash = createFunctionBitmap(functionHashes, viz)

  start_time = time.time()

  args = parser.parse_args()
  if args.outdir[-1] == '/': args.outdir = args.outdir[:-1]

  data = []
  for infile in args.infiles:
    datum = viz.collectData(infile)
    data.append(datum)

  data.sort(key=lambda x: x.user)

  print('Data loaded and compiled in %.3f s' % (time.time() - start_time))

  # Process bigram stuff
  bigrams = [viz.compileBigramModel(d) for d in data]

  for d in data:
    runFunction(bits, viz.saveSinglePlots, (d, args.outdir))

  viz.mkdir_p('%s/ALL' % args.outdir)
  runFunction(bits, viz.createMultiHistograms,
      ('Keystroke PLs',
       'Press length',
       '%s/ALL/keystrokePLs.pdf' % args.outdir,
       [d.keystrokePLs[d.keystrokePLs < 3] for d in data],
       [d.user for d in data]))

  for i in range(viz.NUMBER_OF_KEYCODES):
    if all(i in d.keystrokePLs_key for d in data):
      datum = [d.keystrokePLs_key[i] for d in data]
      runFunction(bits, viz.createMultiHistograms,
          ('Keystroke PLs (Key=%s)' % viz.KC2KEY[i],
           'Press length',
           '%s/ALL/keystrokePLs_key_%d.pdf' % (args.outdir, i),
           [d[d < 3] for d in datum],
           [d.user for d in data]))

  for x in data[0].keystrokePLs_domain.iterkeys():
    if all(x in d.keystrokePLs_domain for d in data):
      datum = [d.keystrokePLs_domain[x] for d in data]
      runFunction(bits, viz.createMultiHistograms,
          ('Keystroke PLs (Domain=%s)' % x,
           'Press length',
           '%s/ALL/keystrokePLs_key_%s.pdf' % (args.outdir, x),
           [d[d < 3] for d in datum],
           [d.user for d in data]))

  if len(data) > 1:
    for (d1, d2) in itertools.combinations(data, 2):
      runFunction(bits, viz.compareTwoUsers, (d1, d2, args.outdir))

  print('Process completed in %.3f s' % (time.time() - start_time))

  # Save the function hashes
  saveFunctionHashes(FUNCTION_HASH_FNAME, newHash)

