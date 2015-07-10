var React = require('react');
var PacienteSearch = require('./PacienteSearch.react');
var PacienteList = require('./PacienteList.react');

var PacienteCheckin = React.createClass({
  render: function() {
    return (
      <div>
        <h2 className="paper-font-display2">Paciente</h2>
        <PacienteSearch />
        <PacienteList />
      </div>
    )
  }
});

module.exports = PacienteCheckin;
