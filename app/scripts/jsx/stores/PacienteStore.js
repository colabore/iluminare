var urls = require('../utils/ApiUrls');
var jquery = require('jquery');

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
    throw new Error('PacientesSearchByNameAction is required');

  if (!options.searchByNameStore)
    throw new Error('PacientesSearchByNameStore is required');

  if (!options.infoAction)
    throw new Error('PacienteInfoAction is required');

  if (!options.infoStore)
    throw new Error('PacienteInfoStore is required');

  searchByName(options.searchByNameAction, options.searchByNameStore);
  info(options.infoAction, options.infoStore);
}

module.exports = create;
