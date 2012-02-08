// namespace Kss
var Kss = Kss || { };

(function() {
  
  // This was a holdover from when I was anonymizing keystrokes
  function isValidKeycode (k) {
    return true;
  }

  // Sends data from chrome page to background page
  var Data_ = Class.$extend({
    __init__: function() {
      var this_ = this;

      this._queue = Array();
      this.keystrokeHandler = function(k) { this_.queueKeystroke(k); };
      this._intervalId = null;
      this._lock = false;
    },

    // Queue a keystroke datapoint.
    queueKeystroke: function(keystroke) {
      var this_ = this;
      if (this._lock) {
        setTimeout(function() { this_.queueKeystroke(keystroke); }, 500);
      } else {
        if (!isValidKeycode(keystroke.keycode)) {
          keystroke.keycode = -1;
        }

        this._queue.push(keystroke);
      }
    },
    
    // Sends data via the provided port to the background page.
    sendData: function() {
      if (this._queue.length == 0) return;

      this._lock = true;
      var message = { 
        'event' : 'keystrokes',
        'keystrokes' : this._queue,
        'url': document.URL,
        'domain' : location.host,
        'timestamp' : (new Date()).getTime()
      };
      this._port.postMessage(message);
    },

    // Starts the Data gathering instance.
    // Will log a message that approximately means the page has loaded.
    // Starts a timer that checks how long it has been since a keystroke was
    //  received 
    start: function() {
      var this_ = this;
      this._port = chrome.extension.connect({name: "heron-data"});
      
      this._port.postMessage({
        'event' : 'load',
        'openedUrl' : document.URL,
        'timestamp' : (new Date()).getTime()
      });

      this._port.onMessage.addListener(function (msg) {
        if (msg.success) {
          console.log('Data sent to browser!');
          this_._queue = new Array();
          this_._lock = false;
        }
      });

      this._intervalId = setInterval(function(obj) {
        obj.sendData();
      }, Kss.PAGE_TO_BROWSER_INTERVAL, this);
    },

    stop: function() {
      clearInterval(this._intervalId);
      this.sendData();
      this._port.postMessage({
        'event' : 'unload',
        'closedUrl' : document.URL,
        'timestamp' : (new Date()).getTime()
      });
      this._port.disconnect();
    },
  });

  // Export class Data
  Kss.Data = Data_;
})();
