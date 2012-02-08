// A dumb package that will relay messages from webpage to remote storage
(function() {

  var SALT = 'AI Lab';
  
  var isStoring = false;

  // Stores the event, and a hash of the event for verification
  function storeData(msg) {
    console.log(msg);
    var message = {};
    var count = localStorage['_LOG_COUNT'];
    var key = 'log-' + count;
    message['data'] = msg;
    message['hash'] = hex_md5(SALT + JSON.stringify(msg,null));
    localStorage[key] = JSON.stringify(message,null);
    localStorage['_LOG_COUNT'] = parseInt(count) + 1;
  }

  // Receives data, sends it off to a server for storage.
  // There is a browser-level lock on this function: only one instance
  // of this function can be called at a time.
  function createReceiveDataListener(port) {
    var receiveData = function(msg) {
      if (msg.event != 'keystrokes') return;
      if (isStoring) {
        setTimeout(function(){ receiveData(msg); }, 500);
      } else {
        isStoring = true;
        storeData(msg);
        localStorage['data-view'] = JSON.stringify(msg, null, 2);
        port.postMessage({ success : 1 });
        isStoring = false;
      }
    };

    return receiveData;
  }

  chrome.tabs.onActiveChanged.addListener(function(tabId, attachInfo) {
    chrome.tabs.get(tabId, function(tab) {
      storeData({
        'event' : 'tabSwitch',
        'newUrl' : tab.url,
        'timestamp' : (new Date()).getTime()
      });
    });
  });

  chrome.extension.onConnect.addListener(function(port) {
    if (port.name == "heron-data") {
      port.onMessage.addListener(createReceiveDataListener(port));
      port.onMessage.addListener(function(msg) {
        if (msg.event != 'unload' && msg.event != 'load') return;
        storeData(msg);
      });
    }
  });

})();
