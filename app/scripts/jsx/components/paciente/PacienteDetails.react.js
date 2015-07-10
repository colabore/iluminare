var React = require('react');
var PacienteInfo = require('./PacienteInfo.react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  Tabs = MaterialUI.Tabs,
  Tab = MaterialUI.Tab;

var PacienteDetails = React.createClass({
  childContextTypes: {muiTheme: React.PropTypes.object},
  getChildContext: function() {return {muiTheme: ThemeManager.getCurrentTheme()}},
  componentDidMount: function() {
  },
  render: function() {
    return (
      <div>
        <h2 className="paper-font-display2">Paciente</h2>
        <Tabs>
          <Tab label="Informações">
            <PacienteInfo />
          </Tab>
          <Tab label="Tratamentos">
            <PacienteInfo />
          </Tab>
          <Tab label="Atendimentos">
            <PacienteInfo />
          </Tab>
        </Tabs>
      </div>
    )
  }
});

module.exports = PacienteDetails;
