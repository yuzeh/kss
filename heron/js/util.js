var Util = Util || {};

(function() {
  
  var SALT = 'AI Lab';
  
  var isStoring = false;
  
  function get(key) { return parseInt(localStorage[key]); }
  function set(key,val) { localStorage[key] = val; }
  function inc(key) { set(key,get(key) + 1); return get(key); }

  // Stores the event, and a hash of the event for verification
  function storeData(msg) {
    console.log(msg);

    // If waiting for a new session, start the session.
    if (get('tWaitingForSession')) {
      set('tWaitingForSession', 0);
      storeData({
        'event' : 'sessionStart',
        'timestamp' : (new Date()).getTime(),
      });
    }

    var message = {};
    var count = localStorage['logCount'];
    var key = 'log-' + count;
    message['data'] = msg;
    message['hash'] = hex_md5(SALT + JSON.stringify(msg,null));
    localStorage[key] = JSON.stringify(message,null);
    localStorage['logCount'] = parseInt(count) + 1;
  }

  function lock() { isStoring = true; }
  function unlock() { isStoring = false; }
  function isLocked() { return isStoring; }

  Util.storeData = storeData;
  Util.lock = lock;
  Util.unlock = unlock;
  Util.isLocked = isLocked;
  Util.get = get;
  Util.set = set;
  Util.inc = inc;

})();
