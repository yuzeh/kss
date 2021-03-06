(function() {

  // Poor man's imports
  var get = Util.get;
  var set = Util.set;
  var inc = Util.inc;

  // At the end of a session, this function checks for many properties of a
  // user session.
  function checkForSessions() {
    var currentTime = (new Date()).getTime();
    if (currentTime - get('tLastActivity') > Kss.SESSION_CUTOFF) {
      // End current session

      // Increment total time
      var elapsed = (get('tLastActivity') - get('tSessionStartTime')) / 1000;
      inc('totalTime', elapsed);

      // Check if this session is useable
      var goodSession = get('tNumKeystrokes') >= Kss.KEYSTROKE_CRITERIA &&
                        get('tNumEvents') >= Kss.EVENT_CRITERIA;
      
      // Increment session counter
      inc('numSessions');
      if (goodSession) inc('numGoodSessions');
     
      // Log this data
      Util.storeData({
        'event' : 'sessionEnd',
        'timestamp' : get('tLastActivity'),
        'isGood' : goodSession,
        'time' : elapsed,
      });

      // Reset temporary session counters
      set('tNumKeystrokes', 0);
      set('tNumEvents', 0);

      // Wait for new session to start
      set('tWaitingForSession', 1);
      
    } else {
      // Set a timer to check whenever this the current lastActivity expires
      setTimeout(checkForSessions,
        get('tLastActivity') + Kss.SESSION_CUTOFF - currentTime + 500);
    }
  }

  function startNewSessionListener(msg) {
    // If waiting for a new session, start the session.
    if (get('tWaitingForSession')) {
      set('tWaitingForSession', 0);
      set('tSessionStartTime', msg.timestamp);
      Util.storeData({
        'event' : 'sessionStart',
        'timestamp' : msg.timestamp,
      });
      checkForSessions();
    } 
  }

  Util.addStoreDataListener(startNewSessionListener);
  Util.checkForSessions = checkForSessions;
})();
