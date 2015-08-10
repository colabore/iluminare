var urls = require('../utils/ApiUrls');
var Rx = require('rx');
var jquery = require('jquery');

function byInstanciaTratamentoId(action, store) {
  return action.subscribe(
    function (id) {
      console.log('Atendimentos by InstanciaTratamentoId ' + id);

      let params = {
        'status': 'C',
        'instancia_tratamento__id': id,
        'page_size': 100
      };

      jquery.getJSON(urls.atendimento(params), x => store.onNext(x));
    }
  );
};

function byId(action, store) {
  return action.subscribe(
    function (id) {
      console.log('Atendimento byId ' + id);

      let params = {
        'id': id
      };

      jquery.getJSON(urls.atendimento(params), x => store.onNext(x));
    }
  );
};

function create(options) {
  if (!options.byInstanciaTratamentoIdAction)
    throw new Error('byInstanciaTratamentoIdAction is required');

  if (!options.byIdAction)
    throw new Error('byIdAction is required');

  var model = {
    byInstanciaTratamentoIdStore: new Rx.ReplaySubject(),
    byIdStore: new Rx.ReplaySubject()
  };
  jquery.extend(model, options)

  byId(model.byIdAction, model.byIdStore);
  byInstanciaTratamentoId(model.byInstanciaTratamentoIdAction,
                          model.byInstanciaTratamentoIdStore);
  return model;
}

module.exports = create;
