const functions = require('firebase-functions');
const Analytics = require('analytics-node');
const analytics = new Analytics(functions.config().segment.write_key);

exports.trackNewUser = functions.auth.user().onCreate((user) => {
  analytics.identify({
    userId: user.uid,
    traits: {
      name: user.displayName,
      email: user.email,
    }
  });
});
