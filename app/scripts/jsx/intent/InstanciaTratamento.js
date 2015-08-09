var Rx = require('rx');

let intents = {
  byDateAction: new Rx.Subject()
};

module.exports = intents;
