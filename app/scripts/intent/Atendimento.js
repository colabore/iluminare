var Rx = require('rx');

let intents = {
  byInstanciaTratamentoIdAction: new Rx.Subject(),
  byIdAction: new Rx.Subject()
};

module.exports = intents;
