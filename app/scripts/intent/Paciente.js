var Rx = require('rx');

let intents = {
  searchByNameAction: new Rx.Subject(),
  infoAction: new Rx.Subject()
};

module.exports = intents;
