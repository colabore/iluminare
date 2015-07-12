var React = require('react');
var Router = require('react-router'),
  RouteHandler = Router.RouteHandler;
var InstanciaTratatamentoPanel = require('../tratamento/InstanciaTratamentoPanel.react');
var TratamentoActions = require('../../actions/TratamentoActions');

var Atendimento = React.createClass({
  componentDidMount: function() {
    TratamentoActions.instanciatratamento();
  },
  render: function () {
    return (
      <div>
        <h2 className="paper-font-display2">Atendimentos</h2>
        <InstanciaTratatamentoPanel />
        <RouteHandler />
      </div>
    )
  }
});

module.exports = Atendimento;
