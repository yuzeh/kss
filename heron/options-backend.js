// Another dumb package to relay localStorage stuff with the settings page
(function() {
  function set(msg) {
    if (msg.email) localStorage['email'] = msg.email;
    if (msg.userid) localStorage['userid'] = msg.userid;
  }

  var optionsPort;
  chrome.extension.onConnect.addListener(function(port) {
    if (port.name == 'kss_options') {
      optionsPort = port;
      port.onMessage.addListener(function (msg) {
        if (msg.method == 'SET') {
          set(msg);
        } else if (msg.method == 'GET') {
          port.postMessage({
            email: localStorage['email'] || '',
            userid: localStorage['userid'] || ''
          });
        }
      });
    } else if (port.name == 'kss_oid_callback') {
      port.onMessage.addListener(function (msg) {
        // Relay message to kss_options
        optionsPort.postMessage(msg);
      });
    }
  });

  chrome.extension.onRequest.addListener(function(request, sender, sendResponse) {
    if (request.method == "getDataView") {
      if (localStorage['data-view']) sendResponse(localStorage['data-view']);
      else sendResponse(null);
    }
  });
})();

