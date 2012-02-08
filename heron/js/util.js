var Util = Util || {};

(function() {
 
  // Constants
  var SALT = 'AI Lab';
  
  // Instance vars
  var isStoring = false;
  var storeDataListeners = new Array();

  function addStoreDataListener(listener) {
    storeDataListeners.push(listener);
  }
  
  function removeStoreDataListener(listener) {
    var index = storeDataListeners.indexOf(listener);
    if (index != -1) storeDataListeners.splice(index,1);
    else throw new Error("Listener not found");
  }
  
  function get(key) { return parseInt(localStorage[key]); }
  function set(key, val) { localStorage[key] = val; }
  function inc(key, amt) { 
    var amt = amt || 1;
    set(key, get(key) + amt);
    return get(key); 
  }

  // Stores the event, and a hash of the event for verification
  function storeData(msg) {
    localStorage['data-view'] = JSON.stringify(msg, null, 2);
    
    for (var i = 0; i < storeDataListeners.length; ++i)
      storeDataListeners[i](msg);

    console.log(msg);

    var message = {};
    var count = get('logCount');
    var key = 'log-' + count;
    message['data'] = msg;
    message['hash'] = hex_md5(SALT + JSON.stringify(msg, null));
    localStorage[key] = JSON.stringify(message, null);
    inc('logCount');
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
  Util.addStoreDataListener = addStoreDataListener;
  Util.removeStoreDataListener = removeStoreDataListener;

  addStoreDataListener(function(msg) {
    inc('tNumEvents');
    set('tLastActivity', (new Date()).getTime());
    if (msg.event == 'keystrokes') {
      inc('numKeystrokes', msg.keystrokes.length);
      inc('tNumKeystrokes', msg.keystrokes.length);
    }
  });

})();
