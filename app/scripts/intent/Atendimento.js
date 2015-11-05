var Rx = require('rx');

let intents = {
  byIdAction: new Rx.Subject(),
  update: new Rx.Subject()
};

module.exports = intents;
