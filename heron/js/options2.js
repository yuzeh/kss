(function() {
  // imports
  var set = Util.set;
  var inc = Util.inc;
  var get = Util.get;

  // constants
  // TODO: Set up
  var SERVER_COMPLETION_URL = '';
  
  function notifyServerOfCompletion() {
    if (!get('hasNotifiedServerOfCompletion')) {
      set('hasNotifiedServerOfCompletion', 1);
      // TODO: set up
      $.post(SERVER_COMPLETION_URL,
        { uid : localStorage['uid'] },
        function(data, textStatus, jqXhr) { });
    }
  }

  $(function() {
    var progress = Math.floor(get('progress'));
    $('#heron_id').text(localStorage['uid']);
    $('#completion_progress').css('width', '' + progress + '%');
    if (progress == 100) {
      $('#done_msg').css('visibility','');
    }
  });
})();
