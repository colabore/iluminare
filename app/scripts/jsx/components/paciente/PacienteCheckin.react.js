var React = require('react');
var PacienteSearch = require('./PacienteSearch.react');
var PacienteList = require('./PacienteList.react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  TextField = MaterialUI.TextField;
var injectTapEventPlugin = require("react-tap-event-plugin");
  injectTapEventPlugin();

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
        <PacienteSearch searchByNameAction={this.props.searchByNameAction} />
        <PacienteList searchByNameStore={this.props.searchByNameStore} />
      </div>
    )
  }
});

module.exports = PacienteCheckin;
