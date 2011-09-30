var http = require('http'),
      qs = require('querystring'),
   redis = require('redis');

var client = redis.createClient();

var handleRequest = function (req, res) {
  if (req.method == 'POST') {
    var body = '';
    req.on('data', function (data) {
      body += data;
    });

    req.on('end', function () {
      var POST = qs.parse(body);
      console.log(POST);
    });

    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Yay!\n');

  } else {
    res.writeHead(400, {'Content-Type': 'text/plain'});
    res.end('Bad request\n');
  }
};

http.createServer(handleRequest).listen(8081, "yuze.stanford.edu");

console.log('Server running at http://yuze.stanford.edu:8081');

