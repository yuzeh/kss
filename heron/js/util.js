var Util = Util || {};

(function() {
 
  // Constants
  var SALT = 'AI Lab';

  function _removeFromArray(a,b) {
    var index = a.indexOf(b);
    if (index != -1) a.splice(index,1);
    else throw new Error("Item not found in array");
  }
  
  // Instance vars
  var storeDataListeners = new Array();

  function addStoreDataListener(listener) {
    storeDataListeners.push(listener);
  }
  
  function removeStoreDataListener(listener) {
    _removeFromArray(storeDataListeners, listener);
  }
  
  // BEGIN: localStorage modification module
  var watchers = new Array();

  function addWatcher(watcher) { watchers.push(watcher); }
  function removeWatcher(watcher) { _removeFromArray(watchers, watcher); }
  function get(key) { return parseInt(localStorage[key]); }
  function set(key, val) { 
    localStorage[key] = val;
    for (var i = 0; i < watchers.length; ++i) watchers[i](key,val);
  }

  function inc(key, amt) { 
    var amt = amt || 1;
    set(key, get(key) + amt);
    return get(key); 
  }
  // END: localStorage modification module

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
  
  // BEGIN: Lock module
  var isStoring = false;
  
  function lock() { isStoring = true; }
  function unlock() { isStoring = false; }
  function isLocked() { return isStoring; }
  // END: Lock module

  function normalizeUrl(url) {
    var uri = new Uri(url);
    return [uri.protocol(), '://', uri.host(), uri.path()].join('')
  }

  Util.storeData = storeData;
  Util.lock = lock;
  Util.unlock = unlock;
  Util.isLocked = isLocked;
  Util.get = get;
  Util.set = set;
  Util.inc = inc;
  Util.addWatcher = addWatcher;
  Util.removeWatcher = removeWatcher;
  Util.addStoreDataListener = addStoreDataListener;
  Util.removeStoreDataListener = removeStoreDataListener;
  Util.normalizeUrl = normalizeUrl;

  addStoreDataListener(function(msg) {
    inc('tNumEvents');
    set('tLastActivity', (new Date()).getTime());
    if (msg.event == 'keystrokes') {
      inc('numKeystrokes', msg.keystrokes.length);
      inc('tNumKeystrokes', msg.keystrokes.length);
    }
  });

})();
