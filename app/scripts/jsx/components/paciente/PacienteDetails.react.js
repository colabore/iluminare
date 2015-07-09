var React = require('react');
var PacienteInfo = require('./PacienteInfo.react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  Tabs = MaterialUI.Tabs,
  Tab = MaterialUI.Tab;

var PacienteDetails = React.createClass({
  render: function() {
    return (
      <Tabs>
        <Tab label="Informações">
          <PacienteInfo />
        </Tab>
      </Tabs>
    )
  }
});

module.exports = PacienteDetails;
