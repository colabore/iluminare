var React = require('react');
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager();
var InstanciaTratatamentoPanel = require('../tratamento/InstanciaTratamentoPanel.react');

var model;

var Atendimento = React.createClass({
  childContextTypes: {
    muiTheme: React.PropTypes.object
  },
  getChildContext: function() {
    return {
      muiTheme: ThemeManager.getCurrentTheme()
    }
  },
  render: function () {
    return (
      <div>
        <h2 className="paper-font-display2">Atendimentos</h2>
        <InstanciaTratatamentoPanel todayStore={model.byDateStore} />
      </div>
    )
  }
});

function create(options) {
  if (!options.byDateStore)
    throw new Error('byDateStore is required');

  if (!options.byDateAction)
    throw new Error('byDateAction is required');

  model = options;
  options.byDateAction.onNext(new Date());
  return Atendimento;
}

module.exports = create;
