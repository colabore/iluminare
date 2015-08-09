var urls = require('../utils/ApiUrls');
var jquery = require('jquery');
var Rx = require('rx');

function searchByName(action, store) {
  var source = action.debounce(400);
  return source.subscribe(
    function (nome) {
      console.log('searchByName ' + nome);

      let params = {
        'search': nome
      }
      jquery.getJSON(urls.paciente(params), x => store.onNext(x));
    }
  );
};

function info(action, store) {
  return action.subscribe(
    function (id) {
      console.log('info ' + id);

      let params = {
        'id': id
      }
      jquery.getJSON(urls.paciente(params), function(data){
        if (data.results.length > 0)
          store.onNext(data.results[0]);
      });
    }
  );
};

function create(options) {
  if (!options.searchByNameAction)
    throw new Error('searchByNameAction is required');

  if (!options.infoAction)
    throw new Error('infoAction is required');

  var model = {
    searchByNameStore: new Rx.Subject(),
    infoStore: new Rx.Subject()
  };
  jquery.extend(model, options);

  searchByName(model.searchByNameAction, model.searchByNameStore);
  info(model.infoAction, model.infoStore);
  return model;
}

module.exports = create;
