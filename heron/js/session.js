(function() {

  // var SESSION_CUTOFF = 300000; // 5 minutes, in milliseconds
  // var KEYSTROKE_CRITERIA = 30;
  // var EVENT_CRITERIA = 30;
  
  var SESSION_CUTOFF = 10000; // 10 second sessions for debugging
  var KEYSTROKE_CRITERIA = 10;
  var EVENT_CRITERIA = 5;

  var get = Util.get;
  var set = Util.set;
  var inc = Util.inc;

  function checkForSessions() {
    var currentTime = (new Date()).getTime();
    if (currentTime - get('tLastActivity') > SESSION_CUTOFF) {
      // End current session
      inc('numSessions');
      var goodSession = get('tNumKeystrokes') >= KEYSTROKE_CRITERIA &&
                        get('tNumEvents') >= EVENT_CRITERIA;
      if (goodSession) inc('numGoodSessions');
      Util.storeData({
        'event' : 'sessionEnd',
        'timestamp' : currentTime,
        'isGood' : goodSession
      });

      // Reset temporary session counters
      set('tNumKeystrokes', 0);
      set('tNumEvents', 0);

      // Wait for new session to start
      set('tWaitingForSession', 1);
      
    } else {
      // Set a timer to check whenever this the current lastActivity expires
      setTimeout(checkForSessions,
        get('tLastActivity') + SESSION_CUTOFF - currentTime);
    }
  }

  function startNewSessionListener(msg) {
    // If waiting for a new session, start the session.
    if (get('tWaitingForSession')) {
      set('tWaitingForSession', 0);
      Util.storeData({
        'event' : 'sessionStart',
        'timestamp' : (new Date()).getTime(),
      });
      checkForSessions();
    }
  }

  Util.addStoreDataListener(startNewSessionListener);

})();
