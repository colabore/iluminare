var urls = require('../utils/ApiUrls');
var jquery = require('jquery');
var Rx = require('rx');

function byDate(action, store) {
  return action.subscribe(
    function (date) {
      console.log('byDate ' + date);

      var dd = date.getDate();
      var mm = date.getMonth() + 1; // January is 0!
      var yyyy = date.getFullYear();

      dd = (dd < 10) ? '0' + dd : dd;
      mm = (mm < 10) ? '0' + mm : mm;

      let params = {
        'data': yyyy + '-' + mm + '-' + dd
      };

      jquery.getJSON(urls.instanciatratamento(params), x => store.onNext(x));
    }
  );
};

function byTratamentoId(action, store) {
  return action.subscribe(
    function (id) {
      let params = {
        'tratamento__id': id,
        'ordering': '-id',
        'page_size': 5
      };
      jquery.getJSON(urls.instanciatratamento(params), x => store.onNext(x));
    }
  );
};

function create2(action) {
  return action.subscribe(
    function (id) {
      var date = new Date(Date.now());
      var dateString = date.getFullYear()
        + '-' + date.getMonth()
        + '-' + date.getDay();

      let params = {
        'coletivo': false,
      };
      jquery.ajax({
         url: '//localhost:8000/api/instanciatratamento/',
         type: 'POST',
         contentType: "application/json",
         dataType: 'text',
         data: JSON.stringify({
           "coletivo": false,
           "data": dateString,
           "tratamento": {id: 1}
         }),
         success: function(response) {
           console.log(response);
         },
         error: function(response) {
           console.log(response);
         }
      });
    }
  );
};

function create(options) {
  if (!options.byDateAction)
    throw new Error('byDateAction is required');

  var model = {
    byDateStore: new Rx.ReplaySubject(),
    byTratamentoId: new Rx.Subject()
  };
  jquery.extend(model, options);

  byDate(model.byDateAction, model.byDateStore);
  byTratamentoId(model.getByTratamentoId, model.byTratamentoId);
  create2(model.create);

  return model;
}

module.exports = create;
