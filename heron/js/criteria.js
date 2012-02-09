(function() {

  // imports from util.js
  var set = Util.set;
  var get = Util.get;
  var inc = Util.inc;

  function updateProgress() {
    var progress = 0, count = 0;
    for (var c in Kss.CRITERIA) {
      progress += Math.min(100, Math.floor(100 * get(c) / Kss.CRITERIA[c]));
      ++count;
    }

    progress /= count;
    set('progress', progress);
    
    if (!get('completionPageHasFired') && progress >= 99.9) {
      set('completionPageHasFired', 1);
      chrome.tabs.create({'url':chrome.extension.getURL('options.html')});
    }
  }

  Util.addWatcher(function (key, val) {
    if (key in Kss.CRITERIA) updateProgress();
  });
})();
