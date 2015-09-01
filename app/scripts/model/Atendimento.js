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

function updateRequest(update) {
  update.subscribe(
    function (state){
      console.log('Atendimento model')
      console.log(state);
      jquery.ajax({
        url: '//localhost:8000/api/atendimento/',
        type: 'POST',
        contentType: "application/json",
        dataType: 'text',
        data: JSON.stringify({
          "id": 'http//localhost:8000/api/atendimento/' + state.id,
          "status": "A"
        }),
        success: (function(d){
          console.log(d);
        })
      })
    }
  )
}

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

  updateRequest(model.update);
  return model;
}

module.exports = create;
