var AppDispatcher = require('../dispatcher/AppDispatcher');
var AppConstants = require('../constants/AppConstants');

var AtendimentoActions = {
  search: function(id) {
    AppDispatcher.dispatch({
      type: AppConstants.ATENDIMENTOS_SEARCH,
      id: id
    });
  },
};

module.exports = AtendimentoActions;
