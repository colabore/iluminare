
var urls = require('../utils/ApiUrls');
var Rx = require('rx');
var jquery = require('jquery');

function tratamentos(store) {
  console.log('model::Tratamentos::tratamentos loaded');
  let params = {
    'page_size': 30
  };
  jquery.getJSON(urls.tratamento(params), x => store.onNext(x));
};

function create(options) {
  var model = {
    tratamentos: new Rx.ReplaySubject()
  };
  jquery.extend(model, options)

  tratamentos(model.tratamentos);
  return model;
}

module.exports = create;
