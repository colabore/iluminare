var React = require('react');
var InstanciaTratatamentoPanel = require('../tratamento/InstanciaTratamentoPanel.react');

var Atendimento = React.createClass({
  render: function () {
    return (
      <div>
        <h2 className="paper-font-display2">Atendimentos</h2>
        <InstanciaTratatamentoPanel todayStore={this.props.todayStore} />
      </div>
    )
  }
});

module.exports = Atendimento;
