var AppDispatcher = require('../dispatcher/AppDispatcher');
var AppConstants = require('../constants/AppConstants');

var PacienteActions = {
  search: function(text) {
    AppDispatcher.dispatch({
      type: AppConstants.PACIENTE_SEARCH,
      nome: text
    });
  },
  info: function(paciente_id) {
    AppDispatcher.dispatch({
      type: AppConstants.PACIENTE_INFO,
      id: paciente_id
    });
  }
};

module.exports = PacienteActions;
