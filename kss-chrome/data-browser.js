// A dumb package that will relay messages from webpage to remote storage
(function() {

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
