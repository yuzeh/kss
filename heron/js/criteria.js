(function() {

  // imports from util.js
  var set = Util.set;
  var get = Util.get;
  var inc = Util.inc;

  function updateProgress() {
    var progress = new Array();
    for (var c in Kss.CRITERIA) {
      progress.push(Math.min(100, int(100 * get(c) / Kss.CRITERIA(c))));
    }

    // So much code to do an average in javascript
    var total = 0;
    for (var i = 0; i < progress.length; ++i) {
      total += progress[i];
    }

    progress = total / 4;
    set('progress', progress);
    
    if (progress == 100) { // Done, open options page
      chrome.tabs.create({'url':chrome.extension.getURL('options.html')});
    }
  }

  Util.addWatcher(function (key, val) {
    if (key in Kss.CRITERIA) updateProgress();
  });
})();
