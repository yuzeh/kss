// A dumb package that will relay messages from webpage to remote storage
(function() {

  var DATA_URL = 'http://yuze.no-ip.org:8081';
  var MAX_TEMP = 5;
  var isSending = false;

  var tempStorage = [];
 
  function sendDataToServer() {
    isSending = true;
    var data = {
      email: localStorage['email'],
      payload: tempStorage
    };
    console.log(JSON.stringify(data, null, 2));
    var dataString = JSON.stringify(data);

    $.post(DATA_URL, dataString);
    console.log(dataString);
    tempStorage = [];
    isSending = false;
  };

  // Receives data, sends it off to a server for storage.
  function receiveData(msg) {
    if (isSending) {
      setTimeout(function(){ receiveData(msg); }, 500);
    } else {
      tempStorage.push(msg);
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
