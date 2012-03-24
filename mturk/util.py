# util.py - a bunch of utilities that collect features from data stream

from collections import namedtuple, OrderedDict

KeystrokeData = namedtuple('KeystrokeData',
   ['timestamp', 'pressLength', 'isInputElement', 'keycode'])

_VALID_KEYS = {-1,40,37,38,39,33,34,32,8,46,16,17,18,13}
_ANON  = -1
_ENTER = 13
_SHIFT = 16
_CTRL  = 17
_ALT   = 18
_SPACE = 32

def getKeystrokeLengths(stream, keys=_VALID_KEYS):
  for keystroke in stream:
    if keystroke.keycode in keys:
      yield keystroke.pressLength

# Some functions defined for special keys
getAllKeystrokeLengths = lambda s: getKeystrokeLengths(s)
getAnonKeystrokeLengths = lambda s: getKeystrokeLengths(s, {-1})
getBackKeystrokeLengths = lambda s: getKeystrokeLengths(s, {8})
getCtrlKeystrokeLengths = lambda s: getKeystrokeLengths(s, {17})
getArrowKeystrokeLengths = lambda s: getKeystrokeLengths(s, {37,38,39,40})
getEnterKeystrokeLengths = lambda s: getKeystrokeLengths(s, {13})
getPgNavKeystrokeLengths = lambda s: getKeystrokeLengths(s, {33,34})
getShiftKeystrokeLengths = lambda s: getKeystrokeLengths(s, {16})
getSpaceKeystrokeLengths = lambda s: getKeystrokeLengths(s, {32})
getDeleteKeystrokeLengths = lambda s: getKeystrokeLengths(s, {46})

def getWordData(stream):
  """Generator that parses the stream and returns three data points for each
    word recognized: word duration, word length, whether shift was pressed"""
  # TODO check how throwing out words with backspace/arrow keys attached
  currentlyInWord = False
  throwOutWord = False
  shiftPressed = False
  initialTimestamp = None
  finalTimeStamp = None
  characterCount = 0

  for keystroke in stream:
    if not currentlyInWord:
      if keystroke.isInputElement and keystroke.keycode == -1:
        # start new word
        currentlyInWord = True
        initialTimestamp = keystroke.timestamp
        finalTimestamp = keystroke.timestamp + 1000 * keystroke.pressLength
        characterCount += 1
    else:
      if keystroke.keycode in {_ENTER, _SPACE} or not keystroke.isInputElement:
        # stop new word
        wordDuration = finalTimestamp - initialTimestamp
        wordLength = characterCount
        if not throwOutWord: yield (wordDuration / 1000.0, wordLength, shiftPressed)
        characterCount = 0
        throwOutWord = False
        shiftPressed = False
        currentlyInWord = False
      else:
        if keystroke.keycode == _SHIFT: shiftPressed = True
        if keystroke.keycode in _VALID_KEYS - {_ANON, _SHIFT, _CTRL, _ALT}:
          throwOutWord = True
        if keystroke.keycode == -1:
          characterCount += 1
          finalTimestamp = keystroke.timestamp + 1000 * keystroke.pressLength

def getKeyOverlaps(stream):
  prevEnd = None
  for k in stream:
    if prevEnd is not None: 
      yield (k.timestamp - prevEnd) / 1000.0
    prevEnd = k.timestamp + 1000 * k.pressLength

def getWordPauses(stream):
  currentlyInWord = False
  previousTimestamp = None

  for keystroke in stream:
    if not currentlyInWord:
      if keystroke.isInputElement and keystroke.keycode == -1:
        # start new word
        currentlyInWord = True
        if previousTimestamp is not None:
          yield (keystroke.timestamp - previousTimestamp) / 1000.0
    else:
      if keystroke.keycode in {_ENTER, _SPACE} or not keystroke.isInputElement:
        # stop new word
        previousTimestamp = keystroke.timestamp + 1000 * keystroke.pressLength
        currentlyInWord = False

def getModifierDelays(stream, modifier):
  isModifierPressed = False
  modifierEnd = 0
  for keystroke in stream:
    if keystroke.keycode == modifier:
      isModifierPressed = True
      modifierEnd = keystroke.timestamp + 1000 * keystroke.pressLength
    elif isModifierPressed:
      yield (keystroke.timestamp - modifierEnd) / 1000.0
      isModifierPressed = False

def getKeyToKeys(stream, key):
  lastPress = None
  for keystroke in stream:
    if keystroke.keycode == key:
      if lastPress is not None: yield (keystroke.timestamp - lastPress) / 1000.0
      lastPress = keystroke.timestamp + 1000 * keystroke.pressLength

def filterKeystrokes(stream, cutoff=2):
  "Filters keystrokes by length. Doesn't accept keystrokes that are too long"
  return [x for x in stream if x.pressLength < cutoff]

def segmentStream(stream, delay=1200):
  "Segments a full stream into sessions based on inter-key delay"
  lastTimestamp = None
  streams = []
  currentStream = []

  for k in stream:
    if lastTimestamp == None:
      currentStream.append(k)
    else:
      if k.timestamp - lastTimestamp > delay * 1000: # new stream
        streams.append(currentStream)
        currentStream = []
      currentStream.append(k)
    lastTimestamp = k.timestamp + 1000 * k.pressLength

  if not currentStream == []:
    streams.append(currentStream)

  return streams

def openStream(name):
  "Returns a list with the keystrokes corresponding to the filename"
  ret = []
  with open(name) as fp:
    for line in fp:
      data = line.strip().split(' ')
      data[0] = int(data[0])
      data[1] = float(data[1])
      data[2] = bool(data[2])
      data[3] = int(data[3])
      ret.append(KeystrokeData._make(data))
  
  return ret

# v2 of this script lies below

class Object(object):
  def __init__(self, **args):
    self.__dict__.update(args)
  def __repr__(self):
    return '<%s>' % str('\n '.join('%s : %s' % (k, repr(v))
      for (k, v) in self.__dict__.iteritems()))

def openJsonStream(fp):
  "Opens a stream of user inputs in JSON form"
  import json
  ret = json.load(fp, object_pairs_hook=OrderedDict)
  for i in range(len(ret)):
    entry = ret[i]['data']
    if entry['event'] == 'keystrokes':
      keystrokes = [Object(**k) for k in entry['keystrokes']]
      entry['keystrokes'] = keystrokes
      newEntry = Object(**entry)
    else:
      newEntry = Object(**entry)
    ret[i] = newEntry
 
  return ret

def segmentJsonStream(stream):
  """Ideally, the JSON stream should already be segmented with
  sessionStart/sessionEnd events, but this handles any error in
  data serialization"""
  sessions = []
  currentSession = None
  currentPage = Object(url=None, keystrokes=[])
  for item in stream:
    if item.event == 'sessionStart':
      currentSession = []
      currentPage = Object(url=None, keystrokes=[])
    elif item.event == 'sessionEnd':
      if currentSession is None: # meaning malformed data, ignore
        print("WARN: sessionEnd before sessionStart at %d" % (item.timestamp,))
      currentSession.append(currentPage)
      sessions.append(Object(data=currentSession, time=item.time))
      currentSession = None
    elif item.event == 'keystrokes':
      url = item.url
      if url != currentPage.url:
        currentSession.append(currentPage)
        currentPage = Object(url=url, keystrokes=[])
      currentPage.keystrokes.extend(item.keystrokes)
  return sessions

