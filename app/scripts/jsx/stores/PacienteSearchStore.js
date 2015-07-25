var AppDispatcher = require('../dispatcher/AppDispatcher');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');
var urls = require('../utils/ApiUrls');
var assign = require('object-assign');
var jquery = require('jquery');

var CHANGE_EVENT = 'change';
var pacientes = {'results': []};

var PacienteSearchStore = assign({}, EventEmitter.prototype, {
  get: function() {
    return pacientes;
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
  search: function(nome) {
    let params = {
      'search': nome
    }
    jquery.getJSON(urls.paciente(params),
      function(data) {
        pacientes = data;
        PacienteSearchStore.emitChange();
      });
  }
});

AppDispatcher.register(function(action) {
  switch(action.type) {
    case AppConstants.PACIENTE_SEARCH:
        PacienteSearchStore.search(action.nome);
      break;
    default:
  }
});

module.exports = PacienteSearchStore;
