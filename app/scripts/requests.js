const Rx = require('rx');
const Observable = Rx.Observable;
const jquery = require('jquery');
const urls = require('./utils/ApiUrls');

function requestInstanciaTratamento(date) {
  var dd = date.getDate();
  var mm = date.getMonth() + 1; // January is 0!
  var yyyy = date.getFullYear();

  dd = (dd < 10) ? '0' + dd : dd;
  mm = (mm < 10) ? '0' + mm : mm;

  let params = {
    'data': yyyy + '-' + mm + '-' + dd
  };

  function struct1 (x) {
    return {
      'instanciatratamento': x
    };
  }

  return Observable.fromPromise(
    jquery.getJSON(urls.instanciatratamento(params)).promise()
  ).map(x => struct1(x.results));
};

module.exports = {
  requestInstanciaTratamento: requestInstanciaTratamento
}
