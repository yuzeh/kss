// A dumb package that will relay messages from webpage to remote storage
(function() {

  var isStoring = false;

  var SALT = 'AI Lab';

  function storeData(msg) {
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
  function receiveData(msg) {
    if (isStoring) {
      setTimeout(function(){ receiveData(msg); }, 500);
    } else {
      isStoring = true;

      storeData(msg);
      localStorage['data-view'] = JSON.stringify(msg, null, 2);

      isStoring = false;
    }
  };

  chrome.extension.onConnect.addListener(function(port) {
    if (port.name == "kss_data") {
      port.onMessage.addListener(receiveData);
    }
  });
  
})();
