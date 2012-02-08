// A dumb package that will relay messages from webpage to remote storage
(function() {
  
  // Receives data, sends it off to a server for storage.
  // There is a browser-level lock on this function: only one instance
  // of this function can be called at a time.
  function createReceiveDataListener(port) {
    var receiveData = function(msg) {
      if (msg.event != 'keystrokes') return;
      if (Util.isLocked()) {
        setTimeout(function(){ receiveData(msg); }, 500);
      } else {
        Util.lock();
        Util.storeData(msg);
        localStorage['data-view'] = JSON.stringify(msg, null, 2);
        port.postMessage({ success : 1 });
        Util.unlock();
      }
    };

    return receiveData;
  }

  chrome.tabs.onActiveChanged.addListener(function(tabId, attachInfo) {
    chrome.tabs.get(tabId, function(tab) {
      Util.storeData({
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
        Util.storeData(msg);
      });
    }
  });

})();
