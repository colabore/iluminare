var AppDispatcher = require('../dispatcher/AppDispatcher');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');
var assign = require('object-assign');
var jquery = require('jquery');

var CHANGE_EVENT = 'change';
var paciente = {'result': []};

var PacienteInfoStore = assign({}, EventEmitter.prototype, {
  get: function() {
    return paciente;
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
    jquery.getJSON( "http://localhost:8000/paciente/json/details/" + id,
      function(data) {
        paciente = data;
        PacienteInfoStore.emitChange();
      });
  }
});

AppDispatcher.register(function(action) {
  switch(action.type) {
    case AppConstants.PACIENTE_INFO:
        PacienteInfoStore.search(action.id);
      break;
    default:
  }
});

module.exports = PacienteInfoStore;
