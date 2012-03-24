import util

import matplotlib.pyplot as plt
from scipy.cluster.vq import *

import argparse
from itertools import chain
import os

parser = argparse.ArgumentParser(description='Plots stuff')
parser.add_argument('dir', help='Directory to look up everything')
parser.add_argument('odir', help='Directory to save images to')

keyCombos = [{-1}, {8}, {17}, {37,38,39,40}, {13}, {33,34}, {16}, {32}, {46}]
names = ['anon','back','ctrl','arrow','enter','pgnav','shift','space','delete']

def createDirectoryIfNotExist(dir):
  if not os.access(dir, os.F_OK):
    os.mkdir(dir)

def main(args):
  createDirectoryIfNotExist(args.odir)

  userList = os.listdir(args.dir)
  for user in userList:
    createDirectoryIfNotExist(args.odir + '/' + user)
    sites = os.listdir(args.dir + '/' + user)
    for site in sites:
      relName = user + '/' + site
      createDirectoryIfNotExist(args.odir + '/' + relName)
      stream = util.filterKeystrokes(util.openStream(args.dir + '/' + relName))
      sessions = util.segmentStream(stream)

      # We want histograms of keystroke usage per user
      allLengths = list(util.getAllKeystrokeLengths(stream))
      if len(allLengths) > 0:
        plt.clf()
        plt.hist(list(allLengths), 200)
        plt.savefig(args.odir + '/' + user + '/all-kl-' + site + '.png')

      for i in range(len(keyCombos)):
        lengths = list(util.getKeystrokeLengths(stream, keyCombos[i]))
        if len(lengths) > 0:
          plt.clf()
          plt.hist(list(lengths), 200)
          plt.savefig(args.odir + '/' + user + '/' + names[i] + '-kl-' + site + '.png')

      # Also want histograms of word data, per user
      wordData = zip(*chain(*[util.getWordData(s) for s in sessions]))
      if len(wordData) > 0 and len(wordData[0]) > 0:
        plt.clf()
        plt.hist(list(d for d in wordData[0] if abs(d) < 10), 200)
        plt.savefig(args.odir + '/' + user + '/word-dur-' + site + '.png')
        plt.clf()
        plt.hist(list(wordData[1]), 200)
        plt.savefig(args.odir + '/' + user + '/word-len-' + site + '.png')

      # Key overlaps
      #keyOverlaps = list(chain.from_iterable(util.getKeyOverlaps(s) for s in sessions))
      keyOverlaps = list(x for x in util.getKeyOverlaps(stream) if abs(x) < 5)
      if len(keyOverlaps) > 0:
        plt.clf()
        plt.hist(keyOverlaps, 100)
        plt.savefig(args.odir + '/' + user + '/overlap-' + site + '.png')

      # Word pauses
      wordPauses = list(x for x in util.getWordPauses(stream) if abs(x) < 60)
      if len(wordPauses) > 0:
        plt.clf()
        plt.hist(wordPauses, 100)
        plt.savefig(args.odir + '/' + user + '/word-pause-' + site + '.png')

      # Time between shift key and modified key
      shiftTime = list(x for x in util.getModifierDelays(stream, util._SHIFT) if abs(x) < 5)
      if len(shiftTime) > 0:
        plt.clf()
        plt.hist(shiftTime, 100)
        plt.savefig(args.odir + '/' + user + '/shift-delay-' + site + '.png')

      # Time between shift-to-shift
      shiftShift= list(x for x in util.getModifierDelays(stream, util._SHIFT) if abs(x) < 1200)
      if len(shiftShift) > 0:
        plt.clf()
        plt.hist(shiftShift, 100)
        plt.savefig(args.odir + '/' + user + '/shift-shift-' + site + '.png')


if __name__ == '__main__':
  args = parser.parse_args()
  main(args)
