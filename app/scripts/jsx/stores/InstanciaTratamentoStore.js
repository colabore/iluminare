var urls = require('../utils/ApiUrls');
var jquery = require('jquery');

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

function create(options) {
  if (!options.byDateAction)
    throw new Error('byDateAction is required');

  if (!options.byDateStore)
    throw new Error('byDateStore is required');

  byDate(options.byDateAction, options.byDateStore);
}

module.exports = create;
