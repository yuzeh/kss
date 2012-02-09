// Config file for Kss namespace
var Kss = Kss || { };

Kss.PAGE_TO_BROWSER_INTERVAL = 5000;

// Kss.SESSION_CUTOFF = 300000; // 5 minutes, in milliseconds
// Kss.KEYSTROKE_CRITERIA = 30;
// Kss.EVENT_CRITERIA = 30;
// Kss.CRITERIA = {
//   'numGoodSessions' : 40,
//   'numUrls' : 100,
//   'numDomains' : 10,
//   'totalTime' : 5 * 60 * 60, // 5 hours
// };

Kss.SESSION_CUTOFF = 10000; // 10 second sessions for debugging
Kss.KEYSTROKE_CRITERIA = 5;
Kss.EVENT_CRITERIA = 5;

Kss.CRITERIA = {
  'numGoodSessions' : 3,
  'numUrls' : 3,
  'numDomains' : 2,
  'totalTime' : 1 * 60, // 5 hours
};
