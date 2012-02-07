var port = chrome.extension.connect({ name : "kss_oid_callback" });
var responseURL = (document.location+'').split('?')[1];
$.get('/kss/verify?' + responseURL, function(data) {
  data = JSON.parse(data);
  if (data.authenticated && !data.error) {
    port.postMessage({
      email: data.email,
      userid: data.claimedIdentifier
    });
    window.close();
  } else {
    console.log(data)
    $('body').text('Whoops, an error occurred!');
  }
});
