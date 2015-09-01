var Rx = require('rx');

let intents = {
  byDateAction: new Rx.Subject(),
  getByTratamentoId: new Rx.Subject(),
  create: new Rx.Subject()
};

module.exports = intents;
