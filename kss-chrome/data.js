// namespace Kss
var Kss = Kss || {};

(function() {
  var Data_ = Class.$extend({
    __init__: function(batchSize) {
      var this_ = this;
      
      if (batchSize > 1) this._batchSize = 1;
      else this.batchSize = batchSize;

      this._queue = Array(batchSize);
      this._nDataPoints = 0;
      this.keystrokeHandler = function(k) { this_.queueKeystroke(k); };
    },

    // Queue a keystroke datapoint.
    queueKeystroke: function(keystroke) {
      this._queue[this._nDataPoints] = keystroke;
      ++(this._nDataPoints);
      if (this._nDataPoints == this.batchSize) this.sendData();
    },
    
    // Sends data via the provided port to the background page.
    sendData: function() {
      this._port.postMessage({ 'keystrokes' : this._queue });
      this._queue = new Array(this.batchSize);
      this._nDataPoints = 0;
    },

    // Starts the Data gathering instance.
    start: function() {
      this._port = chrome.extension.connect({name: "kss_data"});
    },

    stop: function() {
      this._port.disconnect();
    },
  });

  // Export class Data
  Kss.Data = Data_;
})();
