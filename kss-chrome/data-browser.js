// A dumb package that will relay messages from webpage to remote storage
(function() {

  // One constant
  var VALID_KEYCODES = [40,37,38,39,33,34,32,8,46,16,17,18,13];
  
  function isValidKeycode (k) {
    for (var j in VALID_KEYCODES) {
      if (j == k) return true;
    }
    return false;
  }

  var DATA_URL = 'http://yuze.no-ip.org/kss';
  var MAX_TEMP = 5;

  var isSending = false;
  var tempStorage = [];

  function sendDataToServer() {
    isSending = true;
    
    var data = {
      userid: localStorage['userid'],
      payload: tempStorage
    };

    localStorage['data-view'] = JSON.stringify(data, null, 2);
    var dataString = JSON.stringify(data);

    $.post(DATA_URL, dataString);

    tempStorage = [];
    isSending = false;
  };

  // Receives data, sends it off to a server for storage.
  function receiveData(msg) {
    if (isSending) {
      setTimeout(function(){ receiveData(msg); }, 500);
    } else {
      msg.location = hex_md5(msg.location);

      // Discard keycode when pressed in a input element
      if (msg.isInputElement) {
        msg.keycode = -1;
      } else if (!isValidKeycode(msg.keycode)) {
        msg.keycode = -1;
      }

      tempStorage.push(msg);
      if (tempStorage.length > MAX_TEMP) {
        sendDataToServer();
      }
    }
  };

  chrome.extension.onConnect.addListener(function(port) {
    if (port.name == "kss_data") {
      port.onMessage.addListener(receiveData);
    }
  });
  
})();
