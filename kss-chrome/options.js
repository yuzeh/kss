var port = chrome.extension.connect({ name : "kss_options" });
port.onMessage.addListener(function(msg) {
  if (msg.email) $('#email').text(msg.email);
  if (msg.userid) $('#userid').val(msg.userid);
});

function save_options() {
  port.postMessage({
    method: 'SET',
    email: $('#email').text(),
    userid: $('#userid').val()
  });
}

function openPopupWindow(openid) {
  var w = window.open('/kss/auth?openid_identifier='+encodeURIComponent(openid),
    'openid_popup', 'width=450,height=500,location=1,status=1,resizable=yes');
}

port.postMessage({ method: 'GET' });
$('#save-button').click(save_options);
$('#google_oid').click(function(){
  openPopupWindow('google.com/accounts/o8/id');
});

chrome.extension.sendRequest({method: 'getDataView'}, function(response) {
  if (response) {
    $('#data-view').text(response);
  }
  prettyPrint();
});
