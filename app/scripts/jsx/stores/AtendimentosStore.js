var AppDispatcher = require('../dispatcher/AppDispatcher');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');
var urls = require('../utils/ApiUrls');
var assign = require('object-assign');
var jquery = require('jquery');

var CHANGE_EVENT = 'change';
var data = {'results': []};

var AtendimentosStore = assign({}, EventEmitter.prototype, {
  get: function() {
    return data;
  },
  emitChange: function() {
    this.emit(CHANGE_EVENT);
  },
  addChangeListener: function(callback) {
    this.on(CHANGE_EVENT, callback);
  },
  removeChangeListener: function(callback) {
    this.removeListener(CHANGE_EVENT, callback);
  },
  search: function(id) {
    let params = {
      'status': 'C',
      'instancia_tratamento__id': id
    };
    jquery.getJSON(urls.atendimento(params),
      function(result) {
        data = result;
        AtendimentosStore.emitChange();
      });
  }
});

AppDispatcher.register(function(action) {
  switch(action.type) {
    case AppConstants.ATENDIMENTOS_SEARCH:
        AtendimentosStore.search(action.id);
      break;
    default:
  }
});

module.exports = AtendimentosStore;
