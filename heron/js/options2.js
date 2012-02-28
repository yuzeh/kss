(function() {
  // imports
  var set = Util.set;
  var inc = Util.inc;
  var get = Util.get;

  // constants
  var COMPLETION_URL = 'https://ai.stanford.edu/~yuze/heron/completion.php';
  
  function notifyServerOfCompletion() {
    if (!get('hasNotifiedServerOfCompletion')) {
      var dat = { uid : localStorage['uid'], upw : localStorage['upw'] };
      $.post(COMPLETION_URL, dat, function(data, tS, jqXhr) {
        console.log(data);
        if (data != "success\n") { // TODO handle error
        } else {
          set('hasNotifiedServerOfCompletion', 1);
        }
      });
    }
  }

  function createTextFileDumpOfData(e) {
    var allTheData = [];
    var numEntries = get('logCount');
    for (var i = 0; i < numEntries; ++i)
      allTheData.push(JSON.parse(localStorage['log-'+i]));

    // Create file, write to filesystem
    var bb = new BlobBuilder();
    bb.append(JSON.stringify(allTheData,null));
    var blob = bb.getBlob('text/plain');
    saveAs(blob, 'data.json');
  }

  $(function() {
    if (get('hasLoadedRestartMessage')) $('.alert').alert('close');
    else set('hasLoadedRestartMessage', 1);

    var progress = Math.floor(get('progress'));
    $('#task_2').click(createTextFileDumpOfData);
    $('#heron_id').text(localStorage['uid']);
    $('#completion_progress').css('width', '' + progress + '%');

    if (progress == 100) {
      $('#done_msg').css('visibility','');
      notifyServerOfCompletion();
    }
  });
})();
