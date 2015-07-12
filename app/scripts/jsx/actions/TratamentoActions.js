var AppDispatcher = require('../dispatcher/AppDispatcher');
var AppConstants = require('../constants/AppConstants');

var TratamentoActions = {
  instanciatratamento: function() {
    AppDispatcher.dispatch({
      type: AppConstants.INTANCIATRATAMENTO_TODAY
    });
  },
};

module.exports = TratamentoActions;
