var React = require('react');
var PacienteSearch = require('./PacienteSearch.react');
var PacienteList = require('./PacienteList.react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  TextField = MaterialUI.TextField;
var injectTapEventPlugin = require("react-tap-event-plugin");
  injectTapEventPlugin();

var searchByNameAction;
var searchByNameStore;

var PacienteCheckin = React.createClass({
  childContextTypes: {
    muiTheme: React.PropTypes.object
  },
  getChildContext: function() {
    return {
      muiTheme: ThemeManager.getCurrentTheme()
    };
  },
  render: function() {
    return (
      <div>
        <h2 className="paper-font-display2">Paciente</h2>
        <PacienteSearch searchByNameAction={searchByNameAction} />
        <PacienteList searchByNameStore={searchByNameStore} />
      </div>
    )
  }
});

module.exports = function(options) {
  if (!options.searchByNameAction)
    throw new Error('searchByNameAction is required');

  if (!options.searchByNameAction)
    throw new Error('searchByNameAction is required');

  searchByNameAction = options.searchByNameAction;
  searchByNameStore = options.searchByNameStore;

  return PacienteCheckin;
};
