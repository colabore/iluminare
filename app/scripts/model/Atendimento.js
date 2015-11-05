var urls = require('../utils/ApiUrls');
var Rx = require('rx');
var jquery = require('jquery');

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
  if (!options.byIdAction)
    throw new Error('byIdAction is required');

  var model = {
    byInstanciaTratamentoIdStore: new Rx.ReplaySubject(),
    byIdStore: new Rx.ReplaySubject()
  };
  jquery.extend(model, options)

  byId(model.byIdAction, model.byIdStore);

  updateRequest(model.update);
  return model;
}

module.exports = create;
