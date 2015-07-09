
var React = require('react');
var PacienteCheckin = require('./components/paciente/PacienteCheckin.react');
var PacienteDetails = require('./components/paciente/PacienteDetails.react');

React.render(
  <PacienteCheckin />,
  document.getElementById('react-paciente-search')
);

React.render(
  <PacienteDetails />,
  document.getElementById('react-paciente-details')
);
