// http://localhost:8000/api/instanciatratamento/.json?data=2015-07-12
var AppDispatcher = require('../dispatcher/AppDispatcher');
var EventEmitter = require('events').EventEmitter;
var AppConstants = require('../constants/AppConstants');
var urls = require('../utils/ApiUrls');
var assign = require('object-assign');
var jquery = require('jquery');

var CHANGE_EVENT = 'change';
var data = {'results': []};

var InstanciaTratamentoStore = assign({}, EventEmitter.prototype, {
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
  searchByDate: function(year, month, day) {
    let params = {
      'data': year + '-' + month + '-' + day
    };
    jquery.getJSON(urls.instanciatratamento(params),
      function(response) {
        data = response;
        InstanciaTratamentoStore.emitChange();
      });
  },
  searchToday: function() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; // January is 0!
    var yyyy = today.getFullYear();

    dd = (dd < 10) ? '0' + dd : dd;
    mm = (mm < 10) ? '0' + mm : mm;

    return this.searchByDate(yyyy, mm, dd);
  }
});

AppDispatcher.register(function(action) {
  switch(action.type) {
    case AppConstants.INTANCIATRATAMENTO_TODAY:
        InstanciaTratamentoStore.searchToday();
      break;
    default:
  }
});

module.exports = InstanciaTratamentoStore;
