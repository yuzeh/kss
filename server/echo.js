var http = require('http'),
      qs = require('querystring'),
   redis = require('redis');

// Gets the single key of a JSON object
function getSingletonJSON(obj) {
  var ret;
  for (var key in obj) {
    if (obj.hasOwnProperty(key)) {
      ret = key;
      break;
    }
  }
  console.assert(ret);
  return ret;
}

var client = redis.createClient();

var handleRequest = function (req, res) {
  if (req.method == 'POST') {
    var body = '';
    req.on('data', function (data) {
      body += data;
    });

    req.on('end', function () {
      var POST = qs.parse(body);
      var post = getSingletonJSON(POST);
      console.log(JSON.stringify(JSON.parse(post), null, 2));
    });

    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Yay!\n');

  } else {
    res.writeHead(400, {'Content-Type': 'text/plain'});
    res.end('Bad request\n');
  }
};

http.createServer(handleRequest).listen(8081, "yuze.no-ip.org");

console.log('Server running at http://yuze.no-ip.org:8081');

