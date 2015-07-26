var urls = require('../utils/ApiUrls');
var jquery = require('jquery');

function byId(action, store) {
  return action.subscribe(
    function (id) {
      console.log('Atendimentos byId ' + id);

      let params = {
        'status': 'C',
        'instancia_tratamento__id': id
      };

      jquery.getJSON(urls.atendimento(params), x => store.onNext(x));
    }
  );
};

function create(options) {
  if (!options.byIdAction)
    throw new Error('byIdAction is required');

  if (!options.byIdStore)
    throw new Error('byIdStore is required');

  byId(options.byIdAction, options.byIdStore);
}

module.exports = create;
