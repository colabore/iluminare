var Rx = require('rx');

let intents = {
  getByTratamentoId: new Rx.Subject(),
  create: new Rx.Subject()
};

module.exports = intents;
