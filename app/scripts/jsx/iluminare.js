
var React = require('react');
var Router = require('react-router'),
  Route = Router.Route,
  RouteHandler = Router.RouteHandler,
  Link = Router.Link;

var PacienteCheckin = require('./components/paciente/PacienteCheckin.react');
var PacienteDetails = require('./components/paciente/PacienteDetails.react');

var Atendimento = React.createClass({
  render: function () {
    return (
      <div elevation="1">
        <h2 className="paper-font-display2">Atendimento</h2>
        <RouteHandler />
      </div>
    )
  }
});

var App = React.createClass({
  render () {
    return (
      <div>
        <h1>home</h1>
        <a href="#/paciente">Paciente</a>
      </div>
    )
  }
});

var routes = (
  <Route>
    <Route path="paciente" handler={PacienteCheckin} />
    <Route path="paciente/details/:id" handler={PacienteDetails} />
    <Route path="atendimento" handler={Atendimento}/>
    <Route path="voluntario" handler={PacienteCheckin}/>
    <Route path="relatorio" handler={PacienteCheckin}/>
  </Route>
);

Router.run(routes, function (Handler) {
  React.render(<Handler/>, document.getElementById('react-content'));
});
