const Rx = require('rx');
const Observable = Rx.Observable;
const jquery = require('jquery');
const urls = require('./utils/ApiUrls');

function transferProperty(object, from, to) {
  var o = new Object();
  o[to] = object[from];
  return o;
}

function requestInstanciaTratamento(date) {
  var dd = date.getDate();
  var mm = date.getMonth() + 1; // January is 0!
  var yyyy = date.getFullYear();

  dd = (dd < 10) ? '0' + dd : dd;
  mm = (mm < 10) ? '0' + mm : mm;

  let params = {
    'data': yyyy + '-' + mm + '-' + dd
  };
  return Observable.fromPromise(
    jquery.getJSON(urls.instanciatratamento(params)).promise()
  ).map(x => transferProperty(x, 'results', 'instanciatratamento'));
};

function requestAtendimentoFromTratamentoId(id) {
    let params = {
      'instancia_tratamento__id': id,
      'page_size': 100
    };
    return Observable.fromPromise(
      jquery.getJSON(urls.atendimento(params)).promise()
    ).map(x => transferProperty(x, 'results', 'atendimento'));
};


module.exports = {
  requestInstanciaTratamento: requestInstanciaTratamento,
  requestAtendimentoFromTratamentoId: requestAtendimentoFromTratamentoId
}
