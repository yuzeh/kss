(function() {

  var SESSION_CUTOFF = 300000; // 5 minutes, in milliseconds
  var KEYSTROKE_CRITERIA = 30;
  var KEYSTROKE_CRITERIA = 30;

  function get(key) { return parseInt(localStorage[key]); }
  function set(key,val) { localStorage[key] = val; }
  function inc(key) { set(key,get(key) + 1); return get(key); }

  function checkForSessions() {
    var currentTime = (new Date()).getTime();
    if (currentTime - get('tLastActivity') > SESSION_CUTOFF) {
      // End current session
      inc('numSessions');
      var goodSession = get('tNumKeystrokes') > KEYSTROKE_CRITERIA &&
                        get('tNumEvents') > EVENT_CRITERIA);
      if (goodSession) inc('numGoodSessions');
      storeData({
        'event' : 'sessionEnd',
        'timestamp' : currentTime,
        'isGood' : goodSession
      });

      // Wait for new session to start
      set('tWaitingForSession', 1);
      
    } else {
      // Set a timer to check whenever this the current lastActivity expires
      setTimeout(checkForSessions(),
        get('tLastActivity') + SESSION_CUTOFF - currentTime);
    }
  }
})();
