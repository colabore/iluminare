var React = require('react');
var PacienteSearch = require('./PacienteSearch.react');
var PacienteList = require('./PacienteList.react');

var PacienteCheckin = React.createClass({
  render: function() {
    return (
      <div>
        <PacienteSearch />
        <PacienteList />
      </div>
    )
  }
});

module.exports = PacienteCheckin;
