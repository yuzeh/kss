// A dumb package that will relay messages from webpage to remote storage
(function() {

  DATA_URL: 'http://localhost:8081/storeData';
  
  // Receives data, sends it off to a server for storage.
  receiveData = function(msg) {
    var msgString = JSON.stringify(msg);
    console.log(msgString);
    // $.post(DATA_URL, msgString);
  };

  chrome.extension.onConnect.addListener(function(port) {
    console.assert(port.name == "kss_data");
    port.onMessage.addListener(receiveData);
  });
  
})();
